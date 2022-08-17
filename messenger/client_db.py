from datetime import datetime
from dataclasses import dataclass

from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey, DateTime, Text
from sqlalchemy.orm import mapper, sessionmaker


class ClientStorage:
    @dataclass
    class KnownUsers:
        """Отображение таблицы известных пользователей."""
        username: str
        id: int | None = None

    @dataclass()
    class MessageHistory:
        """Отображение таблицы истории сообщений."""
        from_user: str
        to_user: str
        message: str
        date_time: datetime = datetime.now()
        id: int | None = None

    @dataclass
    class Contacts:
        """Отображение списка контактов."""
        username: str
        id: int | None = None

    def __init__(self, username: str):
        self.db_path = f'client_{username}.sqlite3'
        self.db_engine = create_engine(
            url=f'sqlite:///{self.db_path}', echo=False,
            pool_recycle=7200,
            connect_args={'check_same_thread': False})

        self.metadata = MetaData()

        users = Table('known_users', self.metadata,
                      Column('id', Integer, primary_key=True),
                      Column('username', String(64))
                      )

        history = Table('message_history', self.metadata,
                        Column('id', Integer, primary_key=True),
                        Column('from_user', String(64)),
                        Column('to_user', String(64)),
                        Column('message', Text),
                        Column('date_time', DateTime)
                        )

        contacts = Table('contacts', self.metadata,
                         Column('id', Integer, primary_key=True),
                         Column('username', String(64), unique=True)
                         )

        self.metadata.create_all(self.db_engine)

        mapper(self.KnownUsers, users)
        mapper(self.MessageHistory, history)
        mapper(self.Contacts, contacts)

        session_constructor = sessionmaker(bind=self.db_engine)
        self.session = session_constructor()

        self.session.query(self.Contacts).delete()
        self.session.commit()

    def add_contact(self, contact: str) -> None:
        """Добавление контактов."""
        if not self.session.query(self.Contacts).filter_by(username=contact).count():
            contact_row = self.Contacts(username=contact)
            self.session.add(contact_row)
            self.session.commit()

    def del_contact(self, contact: str) -> None:
        """Удаление контакта."""
        self.session.query(self.Contacts).filter_by(username=contact).delete()

    def add_users(self, users: list | tuple) -> None:
        """Добавление известных пользователей.
        Пользователи получаются только с сервера, поэтому таблица очищается."""
        self.session.query(self.KnownUsers).delete()
        for user in users:
            user_row = self.KnownUsers(user)
            self.session.add(user_row)
        self.session.commit()

    def save_message(self, from_user: str, to_user: str, message) -> None:
        """Сохранение сообщений."""
        message_row = self.MessageHistory(from_user=from_user, to_user=to_user, message=message)
        self.session.add(message_row)
        self.session.commit()

    def get_contacts(self) -> list[str]:
        """Возвращает контакты."""
        return [contact[0] for contact in self.session.query(self.Contacts.username).all()]

    def get_users(self) -> list[str]:
        """Возвращает список известных пользователей."""
        return [user[0] for user in self.session.query(self.KnownUsers.username).all()]

    def check_user(self, username: str) -> bool:
        """Проверяет наличие пользователя в известных."""
        if self.session.query(self.KnownUsers).filter_by(username=username).count():
            return True
        return False

    def check_contact(self, contact: str) -> bool:
        """Проверяет наличие пользователя в контактах."""
        if self.session.query(self.Contacts).filter_by(username=contact).count():
            return True
        return False

    def get_history(self, from_who: str | None = None, to_who: str | None = None) -> list[tuple]:
        """Возвращает историю переписки."""
        query = self.session.query(self.MessageHistory)
        if from_who:
            query = query.filter_by(from_user=from_who)
        if to_who:
            query = query.filter_by(to_user=to_who)

        return [(history_row.from_user, history_row.to_user, history_row.message, history_row.date_time)
                for history_row in query.all()]


if __name__ == '__main__':
    # отладка
    test_db = ClientStorage('test1')

    for i in ['test3', 'test4', 'test5']:
        test_db.add_contact(i)

    test_db.add_contact('test4')
    test_db.add_users(['test1', 'test2', 'test3', 'test4', 'test5'])
    test_db.save_message('test1', 'test2', f'Привет! я тестовое сообщение от {datetime.now()}!')
    test_db.save_message('test2', 'test1', f'Привет! я другое тестовое сообщение от {datetime.now()}!')
    print(test_db.get_contacts())
    print(test_db.get_users())
    print(test_db.check_user('test1'))
    print(test_db.check_user('test10'))
    print(test_db.get_history('test2'))
    print(test_db.get_history(to_who='test2'))
    print(test_db.get_history('test3'))
    test_db.del_contact('test4')
    print(test_db.get_contacts())
