"""
1. Написать функцию host_ping(), в которой с помощью утилиты ping будет проверяться доступность
сетевых узлов. Аргументом функции является список, в котором каждый сетевой узел должен быть
представлен именем хоста или ip-адресом. В функции необходимо перебирать ip-адреса и проверять
их доступность с выводом соответствующего сообщения («Узел доступен», «Узел недоступен»).
При этом ip-адрес сетевого узла должен создаваться с помощью функции ip_address().
"""
from ipaddress import ip_address
from subprocess import Popen, PIPE
import socket


def get_host_by_title(title_host: str) -> str | bool:
    try:
        address = socket.gethostbyname(title_host)
    except socket.gaierror:
        return False

    return address


def host_ping(list_ip_addresses: list[str] | tuple[str], timeout: int = 500, requests: int = 1) -> dict[str, list[str]]:
    results = {'Доступные узлы': [],
               'Недоступные узлы': []}

    for address in list_ip_addresses:

        try:
            address = ip_address(address)
        except ValueError:
            address = get_host_by_title(address)

            if not address:
                continue

        process = Popen(f'ping {address} -n {requests} -w {timeout}', shell=False, stdout=PIPE)
        process.wait()

        if process.returncode == 0:
            results['Доступные узлы'].append(str(address))
            log_string = f'{address} - Хост доступен'
        else:
            results['Недоступные узлы'].append(str(address))
            log_string = f'{address} - Хост недоступен'
        print(log_string)

    return results


if __name__ == '__main__':
    ip_addresses = ['instagram.com',
                    'yandex.ru',
                    '1.1.1.1',
                    '8.8.8.8',
                    'vk.com',
                    '95.68.206.123']
    host_ping(ip_addresses)

# RESULTS
# NO VPN
# 5.255.255.50 - Хост доступен
# 1.1.1.1 - Хост доступен
# 8.8.8.8 - Хост доступен
# 87.240.190.78 - Хост доступен
# 95.68.206.123 - Хост доступен
# VPN
# 157.240.236.174 - Хост доступен
# 77.88.55.70 - Хост доступен
# 1.1.1.1 - Хост недоступен
# 8.8.8.8 - Хост доступен
# 87.240.190.67 - Хост доступен
# 95.68.206.123 - Хост доступен
