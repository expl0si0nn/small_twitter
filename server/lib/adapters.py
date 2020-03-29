from lib.exceptions import ItemNotFoundError
from lib.transaction import Transaction

from lib.models.user import User


def construct_posts_list_response(posts):
    res = []
    for post in posts:
        post_dict = post.to_dict()
        with Transaction() as tr:
            try:
                post_dict['username'] = User.read_by_pk(tr.cursor, post_dict.pop('user_id')).username
            except ItemNotFoundError:
                continue
        res.append(post_dict)
    return res


def construct_follows_list_response(follows, followers_mode=False):
    res = []
    for follow in follows:
        with Transaction() as tr:
            try:
                user_id = follow.user_id if not followers_mode else follow.follower_id
                res.append(User.read_by_pk(tr.cursor, user_id).username)
            except ItemNotFoundError:
                continue
    return res
