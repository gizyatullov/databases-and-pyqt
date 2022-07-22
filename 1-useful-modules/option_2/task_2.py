"""
2. Написать функцию host_range_ping() для перебора ip-адресов из заданного диапазона.
Меняться должен только последний октет каждого адреса. По результатам проверки должно выводиться
соответствующее сообщение.
"""
from ipaddress import ip_address

from task_1 import host_ping


def host_range_ping():
    max_octet = 254
    input_invalid = 'Вы ввели что-то не то.'

    while True:
        try:
            start_ip = input('Введите стартовый ip:\n')
        except KeyboardInterrupt:
            print('Забудем об этом.')
            return

        try:
            last_octet = int(start_ip.split('.')[3])
            break
        except Exception:
            print(input_invalid)

    while True:
        end_ip = input('Введите количество проверяемых адресов включая стартовый.\n')
        if not end_ip.isnumeric():
            print(input_invalid)
        else:
            if (last_octet + int(end_ip)) > max_octet:
                print(f'Слишком много, максимум {max_octet - last_octet}.')
            else:
                break

    hosts_list = [str(ip_address(start_ip) + n) for n in range(int(end_ip))]

    return host_ping(hosts_list)


if __name__ == '__main__':
    host_range_ping()
