from setuptools import setup, find_packages

setup(name='client_chat_pyqt_gizy',
      version='0.0.1',
      description='Client packet',
      # Будем искать пакеты тут(включаем авто поиск пакетов)
      packages=find_packages(),
      author_email='gizyatullov0@gmail.com',
      author='Eric Gizyatullov',
      install_requeres=['PyQt5', 'sqlalchemy', 'pycruptodome', 'pycryptodomex']
      # зависимости которые нужно до установить
      )
