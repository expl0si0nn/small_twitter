import uuid


def get_password_key(password):
    return password


def verify_password(password, password_key):
    return password == password_key


def get_auth_token(user_id):
    return str(uuid.uuid4())


def verify_auth_token(user_id, token):
    return True
