from lib.server import Server
from lib.transaction import Transaction

from lib.models.user import User
from lib.models.post import Post
from lib.models.follow import Follow


def add_run_server_args(parser):
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=8080)


def run_server_main(args):
    Server(args.host, args.port).start()


def add_init_db_args(parser):
    parser.add_argument('--force', action='store_true', default=False)


def init_db_main(args):
    with Transaction() as tr:
        User.init_db(tr.cursor, args.force)
        Post.init_db(tr.cursor, args.force)
        Follow.init_db(tr.cursor, args.force)


def add_modify_admins_args(parser):
    parser.add_argument('--username', required=True)
    parser.add_argument('--new_role', default='admin', help='Pass "admin" if you want to make user admin and anything else otherwise')


def modify_admins_main(args):
    with Transaction() as tr:
        user = User.read_by_name(tr.cursor, args.username)
        user.is_admin = args.new_role == 'admin'
        user.update_me(tr.cursor)
