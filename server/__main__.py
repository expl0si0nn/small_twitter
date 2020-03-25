import logging
import sqlite3

from argparse import ArgumentParser

from lib.server import Server


def setup_logging():
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    handlers = logging.getLogger().handlers
    if handlers:
        handlers[0].setFormatter(logging.Formatter("%(asctime)s\t%(levelname)s\t%(process)d\t%(thread)d\t%(message)s"))


def parse_args():
    parser = ArgumentParser('SmallTwitter server')

    def add_run_server_args(parser):
        parser.add_argument('--host', default='127.0.0.1')
        parser.add_argument('--port', type=int, default=8080)

    def add_init_db_args(parser):
        parser.add_argument('--force', action='store_true', default=False)

    def add_modify_admins_args(parser):
        parser.add_argument('--username', required=True)
        parser.add_argument('--new_role', default='admin', help='Pass "admin" if you want to make user admin and anything else otherwise')

    subparsers = parser.add_subparsers(dest='mode')
    add_run_server_args(subparsers.add_parser('run_server'))
    add_init_db_args(subparsers.add_parser('init_db'))
    add_modify_admins_args(subparsers.add_parser('modify_admins'))

    return parser.parse_args()


def run_server_main(args):
    Server(args.host, args.port).start()


def init_db_main(args):
    DROP_TABLES_QUERY = '''
        DROP TABLE IF EXISTS users;
        DROP TABLE IF EXISTS posts;
        DROP TABLE IF EXISTS follows;
    '''
    CREATE_TABLE_QUERY = '''
        CREATE TABLE users (user_id text, username text, password_key text, is_admin boolean);
        CREATE TABLE posts (user_id text, post_id text, post text, timestamp integer, likes integer);
        CREATE TABLE follows (user_id text, follower_id text);
    '''

    db_conn = sqlite3.connect('small_twitter.db')

    if args.force:
        db_conn.executescript(DROP_TABLES_QUERY)
        db_conn.commit()

    db_conn.executescript(CREATE_TABLE_QUERY)
    db_conn.commit()

    db_conn.close()


def modify_admins_main(args):
    CHANGE_ADMIN_STATUS_QUERY = '''
        UPDATE users
        SET is_admin = ?
        WHERE username = ?
    '''

    db_conn = sqlite3.connect('small_twitter.db')
    db_conn.execute(CHANGE_ADMIN_STATUS_QUERY, (args.new_role == 'admin', args.username))
    db_conn.commit()
    db_conn.close()


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
