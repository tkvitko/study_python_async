"""
Применения модулю ipaddress не нашел.
Если бы нельзя было передать hostname, ее использование было бы хоть как-то оправданно.
А учитывая hostname, совсем нет.
"""

import os
from tabulate import tabulate

CHECK_COUNT = 1
CHECK_TIMEOUT = 2  # seconds


def is_host_unavailable(host: str) -> bool:
    """Ping host. Return True if host is unreachable, False if it is OK"""

    response = os.system(f"ping -c {CHECK_COUNT} -W {CHECK_TIMEOUT} {host}")
    return bool(response)


def get_last_octet(ip: str):
    """Returns the last octet of IPv4"""

    return int(ip.split('.')[-1])


def get_first_octets(ip: str, octets_numer: int = 3):
    """Returns the string of the first N octets of IPv4"""

    return '.'.join(ip.split('.')[:octets_numer])


def create_range_of_hosts(start: str, end: str) -> list:
    """Returns the list of IPv4 addresses based on start and end"""

    start_position = get_last_octet(start)
    end_position = get_last_octet(end)
    first_octets = get_first_octets(ip=start, octets_numer=3)
    return [f'{first_octets}.{str(i)}' for i in range(start_position, end_position + 1)]


def ping_hosts(hosts: list) -> list:
    """Pings the list of hosts"""

    results = list()
    for host in hosts:
        result = is_host_unavailable(host=host)
        results.append((host, 'down') if result else (host, 'up'))
    return results


def ping_hosts_range(start: str, end: str) -> list:
    """Pings the range of hosts"""

    return ping_hosts(hosts=create_range_of_hosts(start, end))


def ping_host_range_tab(start: str, end: str) -> None:
    """Pings the range of hosts and prints beautiful table"""

    print(tabulate(ping_hosts_range(start, end), headers=['host', 'result']))


if __name__ == '__main__':
    targets = ['192.168.110.1', '8.8.8.8', 'ya.ru']
    ping_hosts(hosts=targets)
    ping_hosts_range('192.168.10.1', '192.168.10.4')
    ping_host_range_tab('192.168.10.1', '192.168.10.4')
