import sys

from dns_server import DnsServer


def main():
    """Init and run DNS server"""
    server = DnsServer("config.json")
    server.run()


if __name__ == '__main__':
    exit(main())
