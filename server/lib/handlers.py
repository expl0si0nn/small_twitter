import logging
import time

from lib.adapters import construct_posts_list_response
from lib.exceptions import ItemNotFoundError
from lib.transaction import Transaction

from lib.models.user import User
from lib.models.post import Post
from lib.models.follow import Follow


def construct_result(code=200, data={}):
    return {
        'code': code,
        'data': data
    }


class Handler:
    def __init__(self, auth_handler):
        self.auth_handler = auth_handler

        self.no_auth_check_handlers = ['signup', 'signin']
        self.admin_check_handlers = ['admin']

        self.type_to_handler = {
            'signup': self.handle_signup,
            'signin': self.handle_signin,
            'post': self.handle_post,
            'follow': self.handle_follow,
            'like': self.handle_like,
            'get_user_posts': self.handle_get_user_posts,
            'get_user_feed': self.handle_get_user_feed,
            'admin': self.handle_admin_info,
        }

        self.context = {}

    def handle_request(self, request):
        try:
            request_type = request.get('type')

            if request_type not in self.no_auth_check_handlers:
                username = request.get('auth', {}).get('username')
                token = request.get('auth', {}).get('auth_token')
                if not username or not token:
                    return construct_result(400, 'Bad request')

                with Transaction() as tr:
                    try:
                        user = User.read_by_name(tr.cursor, username)
                    except ItemNotFoundError:
                        return construct_result(404, 'User not found')

                if not self.auth_handler.verify_auth_token(user.user_id, token):
                    return construct_result(403, 'Bad auth token, you should sign in')

                self.context['user_id'] = user.user_id

            return self.type_to_handler.get(request_type, lambda _: construct_result(400, 'Bad request'))(request)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            logging.exception('Unhandled exception during request handling occured: {}'.format(e))
            return construct_result(500, 'Error occured')

    def handle_signup(self, request):
        username = request.get('username')
        password = request.get('password')
        if not username or not password:
            return construct_result(400, 'Bad request')

        with Transaction() as tr:
            no_users = False
            try:
                user = User.read_by_name(tr.cursor, username)
            except ItemNotFoundError:
                no_users = True

            if not no_users:
                return construct_result(400, 'User already exists')

            User(None, username, self.auth_handler.get_password_key(password)).create_me(tr.cursor)

        return construct_result()

    def handle_signin(self, request):
        username = request.get('username')
        password = request.get('password')
        if not username or not password:
            return construct_result(400, 'Bad request')

        with Transaction() as tr:
            try:
                user = User.read_by_name(tr.cursor, username)
            except ItemNotFoundError:
                return construct_result(404, 'User not found')

            if not self.auth_handler.verify_password(password, user.password_key):
                return construct_result(400, 'Bad password')

        return construct_result(200, {'auth_token': self.auth_handler.get_auth_token(user.user_id)})

    def handle_post(self, request):
        text = request.get('text')
        if not text:
            return construct_result(400, 'Bad request')

        ts = int(time.time())

        with Transaction() as tr:
            Post(self.context['user_id'], None, text, ts).create_me(tr.cursor)

        return construct_result()

    def handle_follow(self, request):
        username_to_follow = request.get('username_to_follow')
        if not username_to_follow:
            return construct_result(400, 'Bad request')

        with Transaction() as tr:
            try:
                user_to_follow = User.read_by_name(tr.cursor, username_to_follow)
            except ItemNotFoundError:
                return construct_result(404, 'User not found')

            Follow(None, user_to_follow.user_id, self.context['user_id']).create_me(tr.cursor)

        return construct_result()

    def handle_like(self, request):
        post_id = request.get('post_id')
        if not post_id:
            return construct_result(400, 'Bad request')

        with Transaction() as tr:
            try:
                post = Post.read_by_pk(tr.cursor, post_id)
            except ItemNotFoundError:
                return construct_result(404, 'Post not found')

            post.likes += 1
            post.update_me(tr.cursor)

        return construct_result()

    def handle_get_user_posts(self, request):
        username = request.get('username')
        if not username:
            return construct_result(400, 'Bad request')

        with Transaction() as tr:
            try:
                user = User.read_by_name(tr.cursor, username)
            except ItemNotFoundError:
                return construct_result(404, 'User not found')

            posts = Post.get_user_posts(tr.cursor, user.user_id)

        return construct_result(200, construct_posts_list_response(posts))

    def handle_get_user_feed(self, request):
        with Transaction() as tr:
            posts = Post.get_user_feed(tr.cursor, self.context['user_id'])

        return construct_result(200, construct_posts_list_response(posts))

    def handle_admin_info(self, request):
        pass
