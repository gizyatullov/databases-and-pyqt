from datetime import datetime
from dataclasses import dataclass

from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey, DateTime
from sqlalchemy.orm import mapper, sessionmaker


class ServerStorage:
    @dataclass
    class Users:
        username: str
        last_login: datetime = datetime.now()
        id: int | None = None

        def __repr__(self):
            return f'{self.__class__.__name__} ({self.username})'

    @dataclass
    class ActiveUsers:
        user_id: int
        ip_addr: str
        port: int
        entry_time: datetime = datetime.now()
        id: int | None = None

        def __repr__(self):
            return f'{self.__class__.__name__} ({self.ip_addr}:{self.port})'

    @dataclass
    class UserStories:
        user_id: int
        ip_addr: str
        port: int
        date_time: datetime = datetime.now()
        id: int | None = None

        def __repr__(self):
            return f'{self.__class__.__name__} ({self.ip_addr}:{self.port})'

    def __init__(self):
        self.path_db = 'db.sqlite3'
        self.db_engine = create_engine(f'sqlite:///{self.path_db}', echo=False, pool_recycle=7200)
        self.metadata = MetaData()

        users_table = Table('users', self.metadata,
                            Column('id', Integer, primary_key=True),
                            Column('username', String(64), unique=True),
                            Column('last_login', DateTime))

        active_users_table = Table('active_users', self.metadata,
                                   Column('id', Integer, primary_key=True),
                                   Column('user_id', ForeignKey('users.id'), unique=True),
                                   Column('ip_addr', String(15)),
                                   Column('port', Integer),
                                   Column('entry_time', DateTime))

        user_stories_table = Table('user_stories', self.metadata,
                                   Column('id', Integer, primary_key=True),
                                   Column('user_id', ForeignKey('users.id')),
                                   Column('ip_addr', String),
                                   Column('port', Integer),
                                   Column('date_time', DateTime))

        self.metadata.create_all(self.db_engine)

        mapper(self.Users, users_table)
        mapper(self.ActiveUsers, active_users_table)
        mapper(self.UserStories, user_stories_table)

        session_constructor = sessionmaker(bind=self.db_engine)
        self.session = session_constructor()

        self.session.query(self.ActiveUsers).delete()
        self.session.commit()

    def write_db_entry_user(self, username: str, ip_addr: str, port: int) -> None:
        """
        Должна выполняться при входе пользователя, фиксирует факт входа в таблицах
        """
        query = self.session.query(self.Users).filter_by(username=username)

        if query.count():
            user = query.first()
            user.last_login = datetime.now()
        else:
            user = self.Users(username=username)
            self.session.add(user)
            self.session.commit()

        new_active_user = self.ActiveUsers(user_id=user.id, ip_addr=ip_addr, port=port)
        self.session.add(new_active_user)

        new_history_user = self.UserStories(user_id=user.id, ip_addr=ip_addr, port=port)
        self.session.add(new_history_user)

        self.session.commit()

    def write_db_disabling_user(self, username: str) -> None:
        """
        Должна выполняться при выходе пользователя, удаляет из активных пользователей
        """
        user = self.session.query(self.Users).filter_by(username=username).first()

        self.session.query(self.ActiveUsers).filter_by(user_id=user.id).delete()
        self.session.commit()

    def get_all_users(self) -> list[tuple]:
        """
        Возвращает username и время последнего входа всех пользователей
        """
        response = self.session.query(
            self.Users.username,
            self.Users.last_login
        ).all()

        return response

    def get_active_users(self) -> list[tuple]:
        """
        Возвращает username, ip_addr, port, entry_time активных пользователей
        в виде списка кортежей с соответствующими индексами
        """
        response = self.session.query(
            self.Users.username,
            self.ActiveUsers.ip_addr,
            self.ActiveUsers.port,
            self.ActiveUsers.entry_time
        ).join(self.Users).all()

        return response

    def get_history_user(self, username: str | None = None) -> list[tuple]:
        """
        Возвращает историю входа конкретного пользователя или всех с данными username, ip_addr, port, date_time
        """
        query = self.session.query(
            self.Users.username,
            self.UserStories.ip_addr,
            self.UserStories.port,
            self.UserStories.date_time
        ).join(self.Users)

        if username:
            query = query.filter(self.Users.username == username)

        return query.all()


if __name__ == '__main__':
    # Для отладки
    from pprint import pprint

    test_db = ServerStorage()

    test_db.write_db_entry_user(username='client1', ip_addr='95.68.206.123', port=5151)
    print('created entered user')
    test_db.write_db_entry_user(username='client2', ip_addr='95.68.206.124', port=5152)
    print('created entered user')
    print('get_active_users')
    pprint(test_db.get_active_users())

    test_db.write_db_disabling_user(username='client1')
    print('disabling_user')
    print('get_active_users')
    pprint(test_db.get_active_users())

    print('get_history_user (client1)')
    pprint(test_db.get_history_user('client1'))

    test_db.write_db_disabling_user(username='client2')
    print('disabling_user')

    print('all_users')
    pprint(test_db.get_all_users())
