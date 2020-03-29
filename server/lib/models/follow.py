import uuid

from lib.models.record import MetaRecord
from lib.exceptions import ItemNotFoundError


GET_FOLLOWING_USERS_QUERY = '''
    SELECT *
    FROM {}
    WHERE user_id = ?
'''


GET_FOLLOWED_USERS_QUERY = '''
    SELECT *
    FROM {}
    WHERE follower_id = ?
'''


class Follow(metaclass=MetaRecord):
    table = 'follows'
    primary_key = 'follow_id'
    schema = (
        ('follow_id', 'text'),
        ('user_id', 'text'),
        ('follower_id', 'text'),
    )

    def __init__(self, follow_id, user_id, follower_id):
        self.follow_id = follow_id or str(uuid.uuid4())
        self.user_id = user_id
        self.follower_id = follower_id

    @classmethod
    def get_following_users(cls, cursor, user_id):
        cursor.execute(GET_FOLLOWING_USERS_QUERY.format(Follow.table), (user_id,))
        return [cls(*row) for row in cursor.fetchall()]

    @classmethod
    def get_followed_users(cls, cursor, follower_id):
        cursor.execute(GET_FOLLOWED_USERS_QUERY.format(Follow.table), (follower_id,))
        return [cls(*row) for row in cursor.fetchall()]
