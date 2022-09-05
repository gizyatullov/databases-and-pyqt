# from setuptools import setup, find_packages
#
# setup(name='server_chat_pyqt_gizy',
#       version='0.0.1',
#       description='Server packet',
#       # Будем искать пакеты тут(включаем авто поиск пакетов)
#       packages=find_packages(),
#       author_email='gizyatullov0@gmail.com',
#       author='Eric Gizyatullov',
#       install_requeres=['PyQt5', 'sqlalchemy', 'pycruptodome', 'pycryptodomex']
#       # зависимости которые нужно до установить
#       )


import sys

from cx_Freeze import setup, Executable

build_exe_options = {
    'packages': ['common', 'logs', 'server', 'unit_tests']
}

setup(
    name='server_chat_pyqt_gizy',
    version='0.0.1',
    description='Server',
    options={
        'build_exe': build_exe_options
    },
    executables=[Executable('server_test.py',
                            base='Win32GUI',
                            targetName='server.exe')]
)
