import subprocess
import sys

from pydantic import BaseModel


class ST(BaseModel):
    exit: str = 'exit'
    start: str = 'start'
    close: str = 'close'


def main(action: ST):
    process = []
    mess = f"""Выберите действие: {action.exit} - выход, {action.start} - запустить сервер и клиенты, \
{action.close} - закрыть все окна\n"""

    while True:
        ask = input(mess).lower()

        match ask:
            case action.exit:
                sys.exit(0)
            case action.start:
                process.append(subprocess.Popen('py server.py', creationflags=subprocess.CREATE_NEW_CONSOLE))

                for n in range(1, 3):
                    process.append(
                        subprocess.Popen(f'py client.py -n CLIENT{n}', creationflags=subprocess.CREATE_NEW_CONSOLE))

            case action.close:
                if not process:
                    print('Все окна и так закрыты!')

                while process:
                    victim = process.pop()
                    victim.kill()

            case _:
                print('Неизвестная команда.')


if __name__ == '__main__':
    commands = {
        'exit': 'e',
        'start': 's',
        'close': 'c',
    }

    st = ST.parse_obj(commands)

    try:
        main(st)
    except KeyboardInterrupt:
        print('До встречи.')
