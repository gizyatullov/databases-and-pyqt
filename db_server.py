from datetime import datetime
from dataclasses import dataclass

from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey, DateTime
from sqlalchemy.orm import mapper, sessionmaker

SERVER_DB = 'sqlite:///db.sqlite3'
FORMAT_DATE_TIME = '%Y-%m-%d %H:%M:%S'


class ServerStorage:
    @dataclass
    class AllUsers:
        name: str
        last_login: datetime = datetime.now()
        id: int | None = None

    @dataclass
    class ActiveUsers:
        user: int
        ip_address: str
        port: int
        login_date_time: datetime
        id: int | None = None

    @dataclass
    class LoginHistory:
        user: int
        date_time: datetime
        ip: str
        port: int
        id: int | None = None

    def __init__(self):
        self.db_engine = create_engine(SERVER_DB, echo=False, pool_recycle=7200)
        self.metadata = MetaData()

        users_table = Table('Users', self.metadata,
                            Column('id', Integer, primary_key=True),
                            Column('name', String, unique=True),
                            Column('last_login', DateTime))

        active_users_table = Table('Active_users', self.metadata,
                                   Column('id', Integer, primary_key=True),
                                   Column('user', ForeignKey('Users.id'), unique=True),
                                   Column('ip_address', String),
                                   Column('port', Integer),
                                   Column('login_date_time', DateTime))

        user_login_history = Table('Login_history', self.metadata,
                                   Column('id', Integer, primary_key=True),
                                   Column('user', ForeignKey('Users.id')),
                                   Column('date_time', DateTime),
                                   Column('ip', String),
                                   Column('port', Integer))

        self.metadata.create_all(self.db_engine)

        mapper(self.AllUsers, users_table)
        mapper(self.ActiveUsers, active_users_table)
        mapper(self.LoginHistory, user_login_history)

        session_constructor = sessionmaker(bind=self.db_engine)
        self.session = session_constructor()

        self.session.query(self.ActiveUsers).delete()
        self.session.commit()

    def user_login(self, username: str, ip: str, port: int) -> None:
        found_user = self.session.query(self.AllUsers).filter_by(name=username)

        if found_user.count():
            user = found_user.first()
            user.last_login = datetime.now()
        else:
            user = self.AllUsers(name=username)
            self.session.add(user)
            self.session.commit()

        new_active_user = self.ActiveUsers(user=user.id,
                                           ip_address=ip,
                                           port=port,
                                           login_date_time=datetime.now())
        self.session.add(new_active_user)

        history = self.LoginHistory(user=user.id,
                                    date_time=datetime.now(),
                                    ip=ip,
                                    port=port)

        self.session.add(history)
        self.session.commit()

    def user_logout(self, username: str) -> None:
        user = self.session.query(self.AllUsers).filter_by(name=username).first()
        self.session.query(self.ActiveUsers).filter_by(user=user.id).delete()
        self.session.commit()

    def get_users(self) -> list[tuple]:
        query = self.session.query(
            self.AllUsers.name,
            self.AllUsers.last_login,
        )

        return query.all()

    def get_active_users(self) -> list[tuple]:
        query = self.session.query(
            self.AllUsers.name,
            self.ActiveUsers.ip_address,
            self.ActiveUsers.port,
            self.ActiveUsers.login_date_time
        ).join(self.AllUsers)

        return query.all()

    def get_login_history(self, username: str | None = None) -> list[tuple]:
        query = self.session.query(self.AllUsers.name,
                                   self.LoginHistory.date_time,
                                   self.LoginHistory.ip,
                                   self.LoginHistory.port,
                                   ).join(self.AllUsers)

        if username:
            query = query.filter(self.AllUsers.name == username)

        return query.all()


if __name__ == '__main__':
    test_db = ServerStorage()
    test_db.user_login(username='client_1', ip='192.168.0.1', port=5151)
    test_db.user_login(username='client_2', ip='192.168.0.2', port=5252)
    print(test_db.get_active_users(), 'ACTIVES')
    test_db.user_logout('client_1')
    print(test_db.get_active_users(), 'ACTIVES')
    print(test_db.get_login_history('client_1'), 'HISTORY')
    print(test_db.get_users(), 'ALL Users')
