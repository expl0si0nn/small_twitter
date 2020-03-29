import logging

from argparse import ArgumentParser

from lib.main import (
    add_run_server_args, run_server_main,
    add_init_db_args, init_db_main,
    add_modify_admins_args, modify_admins_main,
)


def setup_logging():
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    handlers = logging.getLogger().handlers
    if handlers:
        handlers[0].setFormatter(logging.Formatter("%(asctime)s\t%(levelname)s\t%(process)d\t%(thread)d\t%(message)s"))


def parse_args():
    parser = ArgumentParser('SmallTwitter server')
    subparsers = parser.add_subparsers(dest='mode')

    add_run_server_args(subparsers.add_parser('run_server'))
    add_init_db_args(subparsers.add_parser('init_db'))
    add_modify_admins_args(subparsers.add_parser('modify_admins'))

    return parser.parse_args()


def main():
    setup_logging()
    args = parse_args()

    if args.mode == 'run_server':
        run_server_main(args)
    elif args.mode == 'init_db':
        init_db_main(args)
    elif args.mode == 'modify_admins':
        modify_admins_main(args)
    else:
        raise NotImplementedError('Bad program mode')


if __name__ == '__main__':
    main()
