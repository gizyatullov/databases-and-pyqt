"""
3. Написать функцию host_range_ping_tab(), возможности которой основаны на функции из примера 2.
Но в данном случае результат должен быть итоговым по всем ip-адресам, представленным в
табличном формате (использовать модуль tabulate). Таблица должна состоять из двух колонок и
выглядеть примерно так:
Reachable
-------------
10.0.0.1
10.0.0.2

Unreachable
-------------
10.0.0.3
10.0.0.4
"""
from ipaddress import IPv4Address, ip_address

from tabulate import tabulate

from task_2 import host_range_ping


def host_range_ping_tab(host_start: IPv4Address, host_end: IPv4Address) -> None:
    response = host_range_ping(host_start, host_end)
    reachable = {
        'Reachable': response.reachable,

    }
    unreachable = {
        'Unreachable': response.unreachable,
    }

    print(tabulate(reachable, headers='keys'), end='\n\n')
    print(tabulate(unreachable, headers='keys'))


if __name__ == '__main__':
    address_1 = ip_address('8.8.8.8')
    address_2 = ip_address('8.8.8.9')
    host_range_ping_tab(address_1, address_2)
