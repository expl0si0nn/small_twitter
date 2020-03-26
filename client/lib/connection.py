import base64
import json
import logging


class Connection:
    def __init__(self, connection_reader, connection_writer):
        self.connection_reader = connection_reader
        self.connection_writer = connection_writer

    async def read(self):
        data = await self.connection_reader.readline()
        message = {}

        try:
            message = json.loads(base64.b64decode(data))
        except:
            logging.warning('Invalid request')

        logging.debug('Got message: {}'.format(message))
        return message

    async def write(self, message):
        logging.debug('Going to send message: {}'.format(message))

        data = base64.b64encode(json.dumps(message).encode())
        self.connection_writer.write(data + b'\n')
        await self.connection_writer.drain()

    async def close(self):
        self.connection_writer.close()
        await self.connection_writer.wait_closed()
