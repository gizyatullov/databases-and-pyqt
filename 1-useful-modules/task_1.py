"""
1. Написать функцию host_ping(), в которой с помощью утилиты ping будет проверяться доступность
сетевых узлов. Аргументом функции является список, в котором каждый сетевой узел должен быть
представлен именем хоста или ip-адресом. В функции необходимо перебирать ip-адреса и проверять
их доступность с выводом соответствующего сообщения («Узел доступен», «Узел недоступен»).
При этом ip-адрес сетевого узла должен создаваться с помощью функции ip_address().
"""
import subprocess
from ipaddress import ip_address, IPv4Address


def ping(host: IPv4Address | str) -> bool:
    try:
        out = subprocess.run(f'ping {host}',
                             shell=True,
                             stdout=subprocess.PIPE,
                             timeout=12)
    except subprocess.TimeoutExpired:
        return False

    return out.returncode == 0


def host_ping(hosts: list[IPv4Address | str]) -> None:
    for host in hosts:
        print(f'Узел {host} доступен' if ping(host) else f'Узел {host} недоступен')


if __name__ == '__main__':
    host_list = [
        ip_address('89.250.167.60'),
        'yandex.ru',
        'instagram.com',
        ip_address('1.1.1.1'),
        ip_address('8.8.8.8'),
    ]

    host_ping(host_list)
