from setuptools import setup, find_packages

setup(name='server_chat_pyqt_June',
      version='0.0.1',
      description='Server packet',
      # Будем искать пакеты тут(включаем авто поиск пакетов)
      packages=find_packages(),
      author_email='gizyatullov0@gmail.com',
      author='Eric Gizyatullov',
      install_requeres=['PyQt5', 'sqlalchemy', 'pycruptodome', 'pycryptodomex']
      # зависимости которые нужно до установить
      )
