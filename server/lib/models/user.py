import uuid

from lib.models.record import MetaRecord
from lib.exceptions import ItemNotFoundError


READ_BY_NAME_QUERY = '''
SELECT *
FROM {}
WHERE username = ?;
'''


class User(metaclass=MetaRecord):
    table = 'users'
    primary_key = 'user_id'
    schema = (
        ('user_id', 'text'),
        ('username', 'text'),
        ('password_key', 'text'),
        ('is_admin', 'boolean'),
    )

    def __init__(self, user_id, username, password_key, is_admin=False):
        self.user_id = user_id or str(uuid.uuid4())
        self.username = username
        self.password_key = password_key
        self.is_admin = is_admin

    @classmethod
    def read_by_name(cls, cursor, username):
        cursor.execute(READ_BY_NAME_QUERY.format(User.table), (username,))
        res = cursor.fetchone()
        if res is None:
            raise ItemNotFoundError()
        return cls(*res)
