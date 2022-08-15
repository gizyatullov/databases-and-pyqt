from datetime import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey


class ServerStorage:
    BaseModel = declarative_base()

    class User(BaseModel):
        __tablename__ = 'user'

        id = Column(Integer, primary_key=True)
        username = Column(String(64), unique=True, nullable=False, index=True)
        last_login = Column(DateTime)

        def __init__(self, username: str):
            self.username = username
            self.last_login = datetime.now()

        def __repr__(self):
            return f'{self.__class__.__name__} ({self.username})'

    class HistoryUser(BaseModel):
        __tablename__ = 'history_user'

        id = Column(Integer, primary_key=True)
        user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'), unique=True, nullable=False),
        ip_addr = Column(String(15))
        port = Column(Integer)
        date_time = Column(DateTime)

        user = relationship('User', backref='history')

        def __init__(self, user_id: int, ip_addr: str, port: int, date_time: datetime = datetime.now()):
            self.user_id = user_id
            self.ip_addr = ip_addr
            self.port = port
            self.date_time = date_time

    class ActiveUser(BaseModel):
        __tablename__ = 'active_user'

        id = Column(Integer, primary_key=True)
        user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'), unique=True, nullable=False),
        ip_addr = Column(String(15))
        port = Column(Integer)
        entry_time = Column(DateTime)

        user = relationship('User', backref='active')

        def __init__(self, user_id: int, ip_addr: str, port: int, entry_time: datetime = datetime.now()):
            self.user_id = user_id
            self.ip_addr = ip_addr
            self.port = port
            self.entry_time = entry_time

        def __repr__(self):
            return f'{self.__class__.__name__} ({self.ip_addr}:{self.port})'

    def __init__(self):
        self.path_db = 'db.sqlite3'
        self.db_engine = create_engine(f'sqlite:///{self.path_db}', echo=False, pool_recycle=7200)
        self.BaseModel.metadata.create_all(bind=self.db_engine)

        self.session_maker = sessionmaker(bind=self.db_engine)
        self.session = self.session_maker()

        self.session.query(self.ActiveUser).delete()
        self.session.commit()

    def write_db_entry_user(self, username: str, ip_addr: str, port: int) -> None:
        """
        Должна выполняться при входе пользователя, фиксирует факт входа в таблицах
        """
        response = self.session.query(self.User).filter_by(username=username)

        if response.count():
            user = response.first()
            user.last_login = datetime.now()
        else:
            user = self.User(username=username)
            self.session.add(user)
            self.session.commit()

        new_active_user = self.ActiveUser(user_id=user.id, ip_addr=ip_addr, port=port)
        self.session.add(new_active_user)

        new_history_user = self.HistoryUser(user_id=user.id, ip_addr=ip_addr, port=port)
        self.session.add(new_history_user)

        self.session.commit()

    def write_db_disabling_user(self, username: str) -> None:
        """
        Должна выполняться при выходе пользователя, удаляет из активных пользователей
        """
        user = self.session.query(self.User).filter_by(username=username).first()

        self.session.query(self.ActiveUser).filter_by(user_id=user.id).delete()
        self.session.commit()

    def get_all_users(self) -> list[tuple]:
        """
        Возвращает username и время последнего входа всех пользователей
        """
        response = self.session.query(
            self.User.username,
            self.User.last_login
        ).all()

        return response

    def get_active_users(self) -> list[tuple]:
        """
        Возвращает username, ip_addr, port, entry_time активных пользователей
        в виде списка кортежей с соответствующими индексами
        """
        response = self.session.query(
            self.User.username,
            self.ActiveUser.ip_addr,
            self.ActiveUser.port,
            self.ActiveUser.entry_time
        ).join(self.User).all()

        return response

    def get_history_user(self, username: str | None = None):
        """
        Возвращает историю входа конкретного пользователя или всех с данными username, ip_addr, port, date_time
        в виде
        """
        query = self.session.query(
            self.User.username,
            self.HistoryUser.ip_addr,
            self.HistoryUser.port,
            self.HistoryUser.date_time
        ).join(self.User)

        if username:
            query = query.filter(self.User.username == username)

        return query.all()


if __name__ == '__main__':
    # Для отладки
    from pprint import pprint

    db = ServerStorage()
    db.write_db_entry_user(username='client1', ip_addr='95.68.206.123', port=5151)
    db.write_db_entry_user(username='client2', ip_addr='95.68.206.124', port=5152)

    pprint(db.get_active_users())
