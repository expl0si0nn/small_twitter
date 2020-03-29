import sqlite3


class Transaction:
    @property
    def cursor(self):
        return self._cursor

    def __enter__(self):
        self._conn = sqlite3.connect('small_twitter.db', timeout=5, isolation_level=None)
        self._conn.__enter__()
        self._conn.execute('BEGIN EXCLUSIVE TRANSACTION')
        self._cursor = self._conn.cursor()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._conn.execute('COMMIT TRANSACTION')
        self._conn.__exit__(exc_type, exc_value, traceback)
