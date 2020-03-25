import logging
import sqlite3
import time
import uuid

from lib.crypt import get_password_key, verify_password, get_auth_token, verify_auth_token


def construct_result(code=200, data={}):
    return {
        'code': code,
        'data': data
    }


class AuthCheckResult:
    OK = 0
    NEED_REFRESH = 1
    FAIL = 2


class Handler:
    def __init__(self):
        self.db_conn = sqlite3.connect('small_twitter.db')

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

    def get_user_id_by_username(self, username):
        GET_USER_ID_QUERY = '''
            SELECT user_id
            FROM users
            WHERE username = ?
        '''

        cursor = self.db_conn.cursor()
        cursor.execute(GET_USER_ID_QUERY, (username,))
        user_id = cursor.fetchone()

        return user_id[0] if user_id is not None else None

    def check_auth(self, auth):
        username = auth.get('username')
        token = auth.get('token')
        if not username or not token:
            return AuthCheckResult.FAIL, ''

        user_id = self.get_user_id_by_username(username)

        if user_id is None:
            return AuthCheckResult.FAIL, ''

        if not verify_auth_token(user_id, token):
            return AuthCheckResult.FAIL, ''

        return AuthCheckResult.OK, user_id

    def handle_request(self, request):
        request_type = request.get('type')

        if request_type not in self.no_auth_check_handlers:
            auth_res, user_id = self.check_auth(request.get('auth', {}))
            if auth_res == AuthCheckResult.NEED_REFRESH:
                return construct_result(403, 'Need token refresh')
            elif auth_res == AuthCheckResult.FAIL:
                return construct_result(403, 'Bad auth token, you should sign in')
            self.context['user_id'] = user_id

        return self.type_to_handler.get(request_type, lambda _: construct_result(400, 'Bad request'))(request)

    def handle_signup(self, request):
        CREATE_USER_QUERY = '''
            INSERT INTO users VALUES (?, ?, ?, false)
        '''

        username = request.get('username')
        password = request.get('password')
        if not username or not password:
            return construct_result(400, 'Bad request')

        user_id = self.get_user_id_by_username(username)

        if user_id is not None:
            return construct_result(400, 'User already exists')

        cursor = self.db_conn.cursor()
        cursor.execute(CREATE_USER_QUERY, (str(uuid.uuid4()), username, get_password_key(password)))
        self.db_conn.commit()

        return construct_result()

    def handle_signin(self, request):
        GET_PASSWORD_KEY_QUERY = '''
            SELECT password_key
            FROM users
            WHERE user_id = ?
        '''

        username = request.get('username')
        password = request.get('password')
        if not username or not password:
            return construct_result(400, 'Bad request')

        user_id = self.get_user_id_by_username(username)

        if user_id is None:
            return construct_result(400, 'User not found')

        cursor = self.db_conn.cursor()
        cursor.execute(GET_PASSWORD_KEY_QUERY, (user_id,))
        password_key = cursor.fetchone()[0]

        if not verify_password(password, password_key):
            return construct_result(400, 'Bad password')

        return construct_result(200, {'auth_token': get_auth_token(user_id)})

    def handle_post(self, request):
        CREATE_POST_QUERY = '''
            INSERT INTO posts VALUES (?, ?, ?, ?, 0)
        '''

        text = request.get('text')
        if not text:
            return construct_result(400, 'Bad request')

        ts = int(time.time())

        cursor = self.db_conn.cursor()
        cursor.execute(CREATE_POST_QUERY, (self.context['user_id'], str(uuid.uuid4()), text, ts))
        self.db_conn.commit()

        return construct_result()

    def handle_follow(self, request):
        FOLLOW_USER_QUERY = '''
            INSERT INTO follows VALUES (?, ?)
        '''

        user_to_follow = request.get('user_to_follow')
        if not user_to_follow:
            return construct_result(400, 'Bad request')

        user_id_to_follow = self.get_user_id_by_username(user_to_follow)

        if user_id_to_follow is None:
            return construct_result(400, 'User not found')

        cursor = self.db_conn.cursor()
        cursor.execute(FOLLOW_USER_QUERY, (user_id_to_follow, self.context['user_id']))
        self.db_conn.commit()

        return construct_result()

    def handle_like(self, request):
        pass

    def handle_get_user_posts(self, request):
        pass

    def handle_get_user_feed(self, request):
        pass

    def handle_admin_info(self, request):
        pass
