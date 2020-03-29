import asyncio
import logging

from lib.connection import Connection
from lib.handlers import Handler


class Server:
    def __init__(self, host, port):
        self._host = host
        self._port = port

    @property
    def host(self):
        return self._host

    @property
    def port(self):
        return self._port

    async def handle(self, reader, writer):
        try:
            addr = writer.get_extra_info('peername')
            logging.info('Incoming request from {}'.format(addr))

            conn = Connection(reader, writer)

            request = await conn.read()
            response = Handler().handle_request(request)

            await conn.write(response)
            await conn.close()
        except KeyboardInterrupt:
            raise
        except Exception as e:
            logging.exception('Unhandled exception occured: {}'.format(e))

    async def loop(self):
        server = await asyncio.start_server(self.handle, self.host, self.port)

        addr = server.sockets[0].getsockname()
        logging.info('Serving on {}'.format(addr))

        async with server:
            await server.serve_forever()

    def start(self):
        asyncio.run(self.loop())
