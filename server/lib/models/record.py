import functools

from lib.exceptions import ItemNotFoundError


@staticmethod
def init_db(table, schema, cursor, force=False):
    query = 'CREATE TABLE {} ({})'.format(table, ', '.join(' '.join((column, column_type)) for column, column_type in schema))
    if force:
        cursor.execute('DROP TABLE IF EXISTS {}'.format(table))
    cursor.execute(query)


def to_dict(self, schema):
    return {column: getattr(self, column) for column, _ in schema}


def create_me(self, table, schema, cursor):
    query = 'INSERT INTO {} VALUES ({})'.format(table, ', '.join(['?'] * len(schema)))
    cursor.execute(query, [getattr(self, column) for column, _ in self.schema])


def update_me(self, table, schema, primary_key, cursor):
    query = 'UPDATE {} SET {} WHERE {} = ?'.format(table, ', '.join('{} = ?'.format(column) for column, _ in schema), primary_key)
    cursor.execute(query, [getattr(self, column) for column, _ in self.schema] + [getattr(self, primary_key)])


@classmethod
def read_by_pk(cls, table, primary_key, cursor, primary_key_value):
    query = 'SELECT * FROM {} WHERE {} = ?'.format(table, primary_key)
    cursor.execute(query, (primary_key_value,))
    res = cursor.fetchone()
    if res is None:
        raise ItemNotFoundError()
    return cls(*res)


class MetaRecord(type):
    def __new__(cls, name, bases, dct):
        inst = super().__new__(cls, name, bases, dct)

        table = inst.table
        schema = inst.schema
        primary_key = inst.primary_key

        inst.init_db = functools.partialmethod(init_db, table, schema)
        inst.to_dict = functools.partialmethod(to_dict, schema)
        inst.create_me = functools.partialmethod(create_me, table, schema)
        inst.update_me = functools.partialmethod(update_me, table, schema, primary_key)
        inst.read_by_pk = functools.partialmethod(read_by_pk, table, primary_key)

        return inst
