import asyncio
import logging
import sys
import traceback

from lib.connection import Connection


class Client:
    def __init__(self, server_host, server_port):
        self.server_host = server_host
        self.server_port = server_port

        self.no_auth_check_handlers = ['signup', 'signin']

        self.type_to_params = {
            'signup': ('username', 'password'),
            'signin': ('username', 'password'),
            'post': ('text',),
            'follow': ('username_to_follow',),
            'unfollow': ('username_to_unfollow',),
            'like': ('post_id',),
            'get_user_posts': ('username',),
            'get_followed_users': ('username',),
            'get_following_users': ('username',),
        }

        self.type_to_callback = {
            'signup': self.signup_callback,
            'signin': self.signin_callback,
            'post': self.post_callback,
            'follow': self.follow_callback,
            'unfollow': self.unfollow_callback,
            'like': self.like_callback,
            'get_user_posts': self.get_user_posts_callback,
            'get_user_feed': self.get_user_feed_callback,
            'get_followed_users': self.get_followed_users_callback,
            'get_following_users': self.get_following_users_callback,
            'admin': self.admin_callback,
        }

        self.context = {}

    async def handle_session(self):
        while True:
            try:
                print('Enter command name:')
                action = sys.stdin.readline().strip()

                if action == 'exit':
                    print('Exiting')
                    return
                elif action == 'help':
                    print('Available commands:\nhelp\nexit')
                    for command in self.type_to_callback:
                        print(command)
                    continue

                if action not in self.type_to_callback:
                    print('Bad command')
                    continue

                request = {'type': action}

                if action not in self.no_auth_check_handlers:
                    username = self.context.get('username')
                    auth_token = self.context.get('auth_token')
                    if not username or not auth_token:
                        print('You should signin first')
                        continue

                    request['auth'] = {'username': username, 'auth_token': auth_token}

                for param in self.type_to_params.get(action, ()):
                    print('Enter {}:'.format(param))
                    request[param] = sys.stdin.readline().strip()

                reader, writer = await asyncio.open_connection(self.server_host, self.server_port)
                conn = Connection(reader, writer)

                await conn.write(request)
                response = await conn.read()
                await conn.close()

                if response.get('code') == 200:
                    self.type_to_callback.get(action)(request, response.get('data', {}))
                else:
                    print('Error occured: {}'.format(response.get('data')))
            except KeyboardInterrupt:
                raise
            except Exception as e:
                logging.exception('Exception occured: {}'.format(e))
                # traceback.print_exc(file=open('client.log', 'a'))
                print('Something went wrong')

    def signup_callback(self, request, response):
        print('User {} registered'.format(request['username']))

    def signin_callback(self, request, response):
        print('User {} logged in'.format(request['username']))
        self.context['username'] = request['username']
        self.context['auth_token'] = response.get('auth_token')

    def post_callback(self, request, response):
        print('Post successful')

    def follow_callback(self, request, response):
        print('Followed {}'.format(request['username_to_follow']))

    def unfollow_callback(self, request, response):
        print('Unfollowed {}'.format(request['username_to_unfollow']))

    def like_callback(self, request, response):
        print('Liked {}'.format(request['post_id']))

    def get_user_posts_callback(self, request, response):
        print('Posts of user {}:'.format(request['username']))
        for post in response:
            print(post)

    def get_user_feed_callback(self, request, response):
        print('Posts feed:')
        for post in response:
            print(post)

    def get_followed_users_callback(self, request, response):
        print('Users followed by {}:'.format(request['username']))
        for user in response:
            print(user)

    def get_following_users_callback(self, request, response):
        print('Users following {}:'.format(request['username']))
        for user in response:
            print(user)

    def admin_callback(self, request, response):
        for k, v in response.items():
            print('All {}:'.format(k))
            for item in v:
                print(item)
