import os

import psycopg2 as psycopg2


# from https://github.com/open-contracting/kingfisher-summarize/blob/main/ocdskingfishersummarize/db.py
class Database:
    def __init__(self, schema, table):
        """
        Creates the database connection, set the search path and create the required table if doesn't exists.
        """
        self.connection = psycopg2.connect(os.getenv('KINGFISHER_COLLECT_DATABASE_URL'))
        self.cursor = self.connection.cursor()
        self.schema = schema
        self.table = table
        self.cursor.execute(f'SET search_path = {self.schema}')
        self.create_country_table()

    def create_country_index(self):
        """
        Creates an index on the data->>'date' field
        """
        self.cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_{self.table} "
                            f"ON {self.table}(cast(data->>'date' as text));")

    def create_country_table(self):
        """
        Creates a table with a jsonb "data" column and creates and index on the data->>'date' field
        """
        self.cursor.execute(f'CREATE TABLE IF NOT EXISTS {self.table} (data jsonb);')
        self.create_country_index()

    def re_create_country_table(self):
        """
        Drops and recreate the table
        """
        self.cursor.execute(f'DROP TABLE {self.table} CASCADE ;')
        self.create_country_table()

    def insert_data_row(self, data):
        """
        Inserts a row in the country table. The data must be a compile release json
        """
        self.cursor.execute(f'INSERT INTO {self.table} values (%s)  ;', (data,))

    def get_last_release_date(self):
        """
        Returns the last data->>'date' that exists in the country table
        """
        self.cursor.execute(f"SELECT max(data->>'date') FROM {self.table};")
        return self.cursor.fetchone()[0]

    def commit(self):
        """
        Commits the transaction.
        """
        self.connection.commit()
