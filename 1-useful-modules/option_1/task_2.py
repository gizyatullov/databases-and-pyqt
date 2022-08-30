"""
2. Написать функцию host_range_ping() для перебора ip-адресов из заданного диапазона.
Меняться должен только последний октет каждого адреса. По результатам проверки должно выводиться
соответствующее сообщение.
"""
from dataclasses import dataclass
from ipaddress import IPv4Address, ip_address
from pprint import pprint

from task_1 import ping


def host_range_ping(address_start: IPv4Address, address_end: IPv4Address) -> dataclass:
    if address_start >= address_end:
        raise ValueError('Начальный адрес диапазона не должен быть больше или равен конечному адресу.')

    @dataclass
    class ReachableUnreachable:
        reachable = []
        unreachable = []

    data_inst = ReachableUnreachable()
    current_address = address_start
    while current_address <= address_end:
        data_inst.reachable.append(current_address) if ping(current_address) else data_inst.unreachable.append(
            current_address)
        current_address += 1

    return data_inst


if __name__ == '__main__':
    address_1 = ip_address('8.8.8.8')
    address_2 = ip_address('8.8.8.10')
    result = host_range_ping(address_1, address_2)
    pprint(result.reachable)
    pprint(result.unreachable)
