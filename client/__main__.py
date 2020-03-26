import asyncio
import logging

from argparse import ArgumentParser

from lib.client import Client


def setup_logging():
    logging.basicConfig(stream=open('client.log', 'w'))
    logging.getLogger().setLevel(logging.DEBUG)
    handlers = logging.getLogger().handlers
    if handlers:
        handlers[0].setFormatter(logging.Formatter("%(asctime)s\t%(levelname)s\t%(process)d\t%(thread)d\t%(message)s"))


def parse_args():
    parser = ArgumentParser('SmallTwitter client')

    parser.add_argument('--server_host', required=True)
    parser.add_argument('--server_port', type=int, default=8080)

    return parser.parse_args()


async def main():
    setup_logging()
    args = parse_args()
    await Client(args.server_host, args.server_port).handle_session()


if __name__ == '__main__':
    asyncio.run(main())
