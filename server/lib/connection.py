import base64
import json


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

        return message

    async def write(self, message):
        data = base64.b64encode(json.dumps(message).encode())
        self.connection_writer.write(data)
        await self.connection_writer.drain()

    async def close(self):
        self.connection_writer.close()
        await self.connection_writer.wait_closed()
