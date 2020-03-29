import base64
import hashlib
import logging
import os
import secrets
import time

import jwt


class AuthHandler:
    def __init__(self, pbkdf2_key_length=64, pbkdf2_digest_alg='sha512', pbkdf2_iterations=100000, pbkdf2_delimiter='::',
                 jwt_algorithm='ES512', jwt_private_key=None, jwt_public_key=None, jwt_tolerance_seconds=60 * 5,
                 jwt_access_expiration_seconds=60 * 60 * 2, jwt_refresh_expiration_seconds=60 * 60 * 24 * 2):
        self.pbkdf2_key_length = pbkdf2_key_length
        self.pbkdf2_digest_alg = pbkdf2_digest_alg
        self.pbkdf2_iterations = pbkdf2_iterations
        self.pbkdf2_delimiter = pbkdf2_delimiter

        self.jwt_algorithm = jwt_algorithm
        self.jwt_private_key = jwt_private_key or os.environ.get('JWT_PRIVATE_KEY')
        self.jwt_public_key = jwt_public_key or os.environ.get('JWT_PUBLIC_KEY')
        if self.jwt_public_key is None or self.jwt_public_key is None:
            raise Exception('No keys for jwt')

        self.jwt_tolerance_seconds = jwt_tolerance_seconds
        self.jwt_access_expiration_seconds = jwt_access_expiration_seconds
        self.jwt_refresh_expiration_seconds = jwt_refresh_expiration_seconds

    def get_password_key(self, password):
        salt = secrets.token_bytes(self.pbkdf2_key_length)

        digest = hashlib.pbkdf2_hmac(
            self.pbkdf2_digest_alg,
            bytes(password, 'utf-8'),
            salt,
            self.pbkdf2_iterations,
            self.pbkdf2_key_length,
        )
        parts = [
            self.pbkdf2_digest_alg,
            salt.hex(),
            digest.hex(),
            str(self.pbkdf2_iterations),
        ]

        return self.pbkdf2_delimiter.join(parts)

    def verify_password(self, password, password_key):
        alg, salt, digest, iterations = password_key.split(self.pbkdf2_delimiter)
        digest = bytes.fromhex(digest)
        iterations = int(iterations)

        digest_ = hashlib.pbkdf2_hmac(
            alg,
            bytes(password, 'utf-8'),
            bytes.fromhex(salt),
            iterations,
            len(digest),
        )

        return digest == digest_


    def get_auth_token(self, user_id):
        return jwt.encode(
            {
                'user_id': user_id,
                'exp': (int(time.time()) + self.jwt_access_expiration_seconds)
            },
            base64.decodebytes(self.jwt_private_key.encode('utf-8')),
            self.jwt_algorithm,
        ).decode('utf-8')


    def _decode_token(self, token, verify=True):
        try:
            return jwt.decode(
                token,
                base64.decodebytes(self.jwt_public_key.encode('utf-8')),
                algorithms=[self.jwt_algorithm],
                leeway=self.jwt_tolerance_seconds,
                verify=verify,
            )
        except jwt.exceptions.PyJWTError:
            return {}

    def verify_auth_token(self, user_id, token):
        logging.debug('Decoded token is {}'.format(self._decode_token(token)))
        return self._decode_token(token).get('user_id') == user_id
