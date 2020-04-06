import uuid

from lib.exceptions import ItemNotFoundError

from lib.models.record import MetaRecord
from lib.models.follow import Follow


GET_USER_POSTS_QUERY = '''
    SELECT *
    FROM {}
    WHERE user_id = ?
    ORDER BY timestamp DESC
'''

GET_USER_FEED_QUERY = '''
    SELECT
        p.user_id,
        p.post_id,
        p.post,
        p.timestamp,
        p.likes
    FROM {} AS p
    INNER JOIN (
        SELECT user_id
        FROM {}
        WHERE follower_id = ?
    ) AS f
    ON p.user_id = f.user_id
    ORDER BY timestamp DESC
'''


class Post(metaclass=MetaRecord):
    table = 'posts'
    primary_key = 'post_id'
    schema = (
        ('user_id', 'text'),
        ('post_id', 'text'),
        ('post', 'text'),
        ('timestamp', 'integer'),
        ('likes', 'integer'),
    )

    def __init__(self, user_id, post_id, post, timestamp, likes=0):
        self.user_id = user_id
        self.post_id = post_id or str(uuid.uuid4())
        self.post = post
        self.timestamp = timestamp
        self.likes = likes

    @classmethod
    def get_user_posts(cls, cursor, user_id):
        cursor.execute(GET_USER_POSTS_QUERY.format(Post.table), (user_id,))
        return [cls(*row) for row in cursor.fetchall()]

    @classmethod
    def get_user_feed(cls, cursor, user_id):
        cursor.execute(GET_USER_FEED_QUERY.format(Post.table, Follow.table), (user_id,))
        return [cls(*row) for row in cursor.fetchall()]
