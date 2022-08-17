from datetime import datetime
from dataclasses import dataclass

from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey, DateTime
from sqlalchemy.orm import mapper, sessionmaker


class ServerStorage:
    @dataclass
    class Users:
        """Отображение таблицы пользователей"""
        username: str
        last_login: datetime = datetime.now()
        id: int | None = None

        def __repr__(self):
            return f'{self.__class__.__name__} ({self.username})'

    @dataclass
    class ActiveUsers:
        """Отображение таблицы активных пользователей"""
        user_id: int
        ip_addr: str
        port: int
        entry_time: datetime = datetime.now()
        id: int | None = None

        def __repr__(self):
            return f'{self.__class__.__name__} ({self.ip_addr}:{self.port})'

    @dataclass
    class UserStories:
        """Отображение таблицы истории входов."""
        user_id: int
        ip_addr: str
        port: int
        date_time: datetime = datetime.now()
        id: int | None = None

        def __repr__(self):
            return f'{self.__class__.__name__} ({self.ip_addr}:{self.port})'

    @dataclass
    class UserContacts:
        """С кем общался пользователь"""
        user_id: int
        contact_id: int
        id: int | None = None

    @dataclass
    class HistoryUserActions:
        """История действий"""
        user_id: int
        id: int | None = None
        sent: int = 0
        accepted: int = 0

    def __init__(self, path_db: str):
        self.path_db = path_db
        self.db_engine = create_engine(f'sqlite:///{self.path_db}',
                                       echo=False,
                                       pool_recycle=7200,
                                       connect_args={'check_same_thread': False})
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

        user_contacts_table = Table('user_contacts', self.metadata,
                                    Column('id', Integer, primary_key=True),
                                    Column('user_id', ForeignKey('users.id')),
                                    Column('contact_id', ForeignKey('users.id'))
                                    )

        history_user_actions_table = Table('history_user_actions', self.metadata,
                                           Column('id', Integer, primary_key=True),
                                           Column('user_id', ForeignKey('users.id')),
                                           Column('sent', Integer),
                                           Column('accepted', Integer)
                                           )

        self.metadata.create_all(self.db_engine)

        mapper(self.Users, users_table)
        mapper(self.ActiveUsers, active_users_table)
        mapper(self.UserStories, user_stories_table)
        mapper(self.UserContacts, user_contacts_table)
        mapper(self.HistoryUserActions, history_user_actions_table)

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

            new_user_actions = self.HistoryUserActions(user_id=user.id)
            self.session.add(new_user_actions)

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

    def process_message(self, sender: str, recipient: str) -> None:
        """Функция фиксирует передачу сообщения и делает соответствующие отметки в БД"""
        query_sender = self.session.query(self.Users).filter_by(username=sender)
        query_recipient = self.session.query(self.Users).filter_by(username=recipient)

        if not query_sender.count() or not query_recipient.count():
            return

        sender = query_sender.first().id
        recipient = query_recipient.first().id

        sender_row = self.session.query(self.HistoryUserActions).filter_by(user=sender).first()
        sender_row.sent += 1
        recipient_row = self.session.query(self.HistoryUserActions).filter_by(user=recipient).first()
        recipient_row.accepted += 1

        self.session.commit()

    def add_contact(self, username: str, contact: str) -> None:
        """Добавляет контакт для пользователя."""
        user = self.session.query(self.Users).filter_by(username=username).first()
        contact = self.session.query(self.Users).filter_by(username=contact).first()

        if not contact or self.session.query(self.UserContacts).filter_by(user_id=user.id,
                                                                          contact_id=contact.id).count():
            return

        contact_row = self.UserContacts(user_id=user.id, contact_id=contact.id)

        self.session.add(contact_row)
        self.session.commit()

    def delete_contact(self, username: str, contact: str) -> None:
        """Удаляет контакт из БД"""
        user = self.session.query(self.Users).filter_by(username=username).first()
        contact = self.session.query(self.Users).filter_by(username=contact).first()

        if not contact:
            return

        self.session.query(self.UserContacts).filter(
            self.UserContacts.user_id == user.id,
            self.UserContacts.contact_id == contact.id
        ).delete()

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

    def get_history(self, username: str | None = None) -> list[tuple]:
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

    def get_contacts(self, username: str) -> list[str]:
        """Возвращает список контактов пользователя."""
        user = self.session.query(self.Users).filter_by(username=username).one()

        query = self.session.query(self.UserContacts,
                                   self.Users.username).join(self.Users,
                                                             self.UserContacts.contact_id == self.Users.id).filter_by(
            user_id=user.id)

        return [contact[1] for contact in query.all()]

    def message_history(self) -> list[tuple]:
        """Возвращает количество переданных и полученных сообщений у пользователей."""
        query = self.session.query(
            self.Users.username,
            self.Users.last_login,
            self.HistoryUserActions.sent,
            self.HistoryUserActions.accepted
        ).join(self.Users)

        return query.all()


if __name__ == '__main__':
    # Для отладки
    from pprint import pprint

    test_db = ServerStorage(path_db='db.sqlite3')

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
    pprint(test_db.get_history('client1'))

    test_db.write_db_disabling_user(username='client2')
    print('disabling_user')

    print('all_users')
    pprint(test_db.get_all_users())

    test_db.add_contact(username='client2', contact='client1')
    test_db.add_contact(username='client1', contact='client3')
    test_db.add_contact(username='client1', contact='client6')

    test_db.delete_contact(username='client1', contact='client3')

    test_db.process_message(sender='client1', recipient='client6')

    print('message_history')
    pprint(test_db.message_history())
