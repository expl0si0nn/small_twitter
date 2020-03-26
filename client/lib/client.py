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

        self.type_to_handler = {
            'signup': (self.handle_signup, ('username', 'password')),
            'signin': (self.handle_signin, ('username', 'password')),
            'post': (self.handle_post, ('text',)),
            'follow': (self.handle_follow, ('user_to_follow',)),
            'like': (self.handle_like, ('post_id',)),
            'get_user_posts': (self.handle_get_user_posts, ('username',)),
            'get_user_feed': (self.handle_get_user_feed, ()),
            'admin': (self.handle_admin_info, ()),
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
                if action not in self.type_to_handler:
                    print('Bad command')
                    continue

                params = {'type': action}

                if action not in self.no_auth_check_handlers:
                    username = self.context.get('username')
                    auth_token = self.context.get('auth_token')
                    if not username or not auth_token:
                        print('You should signin first')
                        continue

                    params['auth'] = {'username': username, 'auth_token': auth_token}

                for param in self.type_to_handler[action][1]:
                    print('Enter {}:'.format(param))
                    params[param] = sys.stdin.readline().strip()

                reader, writer = await asyncio.open_connection(self.server_host, self.server_port)
                conn = Connection(reader, writer)

                await self.type_to_handler[action][0](conn, params)
                await conn.close()
            except KeyboardInterrupt:
                raise
            except Exception as e:
                logging.exception('Exception occured: {}'.format(e))
                # traceback.print_exc(file=open('client.log', 'a'))
                print('Something went wrong')

    async def handle_signup(self, conn, params):
        await conn.write(params)
        response = await conn.read()

        if response.get('code') == 200:
            print('User {} registered'.format(params['username']))
        else:
            print('Error occured: {}'.format(response.get('data')))

    async def handle_signin(self, conn, params):
        await conn.write(params)
        response = await conn.read()

        if response.get('code') == 200:
            print('User {} logged in'.format(params['username']))
            self.context['username'] = params['username']
            self.context['auth_token'] = response.get('data', {}).get('auth_token')
        else:
            print('Error occured: {}'.format(response.get('data')))

    async def handle_post(self, conn, params):
        await conn.write(params)
        response = await conn.read()

        if response.get('code') == 200:
            print('Post successful')
        else:
            print('Error occured: {}'.format(response.get('data')))

    async def handle_follow(self, conn, params):
        await conn.write(params)
        response = await conn.read()

        if response.get('code') == 200:
            print('Followed {}'.format(params['user_to_follow']))
        else:
            print('Error occured: {}'.format(response.get('data')))

    async def handle_like(self, conn, params):
        await conn.write(params)
        response = await conn.read()

        if response.get('code') == 200:
            print('Liked {}'.format(params['post_id']))
        else:
            print('Error occured: {}'.format(response.get('data')))

    async def handle_get_user_posts(self, conn, params):
        await conn.write(params)
        response = await conn.read()

        if response.get('code') == 200:
            print('Posts of user {}:'.format(params['username']))
            for post in response.get('data', []):
                print(post)
        else:
            print('Error occured: {}'.format(response.get('data')))

    async def handle_get_user_feed(self, conn, params):
        await conn.write(params)
        response = await conn.read()

        if response.get('code') == 200:
            print('Posts feed:')
            for post in response.get('data', []):
                print(post)
        else:
            print('Error occured: {}'.format(response.get('data')))

    async def handle_admin_info(self, conn, params):
        pass
