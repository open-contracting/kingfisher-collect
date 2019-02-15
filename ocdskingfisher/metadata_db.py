import sqlalchemy as sa
from sqlalchemy.sql import select
import os
import datetime
import json
import alembic.config
import alembic.command


class MetadataDB(object):

    def __init__(self, directory_path=None):
        self.base_path = directory_path
        self.metadata_file = os.path.join(directory_path, "metadb.sqlite3")

        # if no path, "debug mode" with in memory db and echo SQL generated.
        if directory_path is None:
            self.db_url = "sqlite:///:memory:"
            self.engine = sa.create_engine(self.db_url, echo=True)
        else:
            self.db_url = "sqlite:///"+self.metadata_file
            self.engine = sa.create_engine(self.db_url)
        self.metadata = sa.MetaData()

        self.session = sa.Table('session', self.metadata,
                                sa.Column('publisher_name', sa.Text),
                                sa.Column('data_version', sa.Text),
                                sa.Column('base_url', sa.Text),
                                sa.Column('sample', sa.Boolean),
                                sa.Column('session_start_datetime', sa.DateTime),

                                sa.Column('gather_start_datetime', sa.DateTime, nullable=True),
                                sa.Column('gather_finished_datetime', sa.DateTime, nullable=True),
                                sa.Column('gather_errors', sa.Text, nullable=True),
                                sa.Column('gather_stacktrace', sa.Text, nullable=True),
                                sa.Column('gather_success', sa.Boolean, nullable=False, default=False),

                                sa.Column('fetch_start_datetime', sa.DateTime, nullable=True),
                                sa.Column('fetch_finished_datetime', sa.DateTime, nullable=True),
                                sa.Column('fetch_success', sa.Boolean, nullable=False, default=False),
                                )

        self.filestatus = sa.Table('filestatus', self.metadata,
                                   sa.Column('filename', sa.Text, primary_key=True),
                                   sa.Column('url', sa.Text, nullable=False),
                                   sa.Column('data_type', sa.Text, nullable=False),
                                   sa.Column('encoding', sa.Text, nullable=False, default='utf-8'),

                                   sa.Column('fetch_start_datetime', sa.DateTime, nullable=True),
                                   sa.Column('fetch_finished_datetime', sa.DateTime, nullable=True),
                                   sa.Column('fetch_errors', sa.Text, nullable=True),
                                   sa.Column('fetch_warnings', sa.Text, nullable=True),
                                   sa.Column('fetch_success', sa.Boolean, nullable=False, default=False),
                                   sa.Column('priority', sa.Integer, nullable=False, server_default='1'),
                                   )

        alembic_cfg = alembic.config.Config(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'metaalembic.ini')))
        alembic_cfg.set_main_option("sqlalchemy.url", self.db_url)

        with self.engine.begin() as connection:
            alembic_cfg.attributes['connection'] = connection
            alembic.command.upgrade(alembic_cfg, "head")

        self.metadata.create_all(self.engine)

    def create_session_metadata(self, publisher_name, sample, url, data_version):
        with self.engine.connect() as conn:
            s = select([self.session])
            result = conn.execute(s)
            if not result.fetchone():
                return conn.execute(self.session.insert(),
                                    publisher_name=publisher_name,
                                    sample=sample,
                                    base_url=url,
                                    session_start_datetime=datetime.datetime.utcnow(),
                                    data_version=data_version
                                    )

    """Returns a dict with all keys of the current session."""
    def get_session(self):
        with self.engine.connect() as conn:
            s = select([self.session])
            result = conn.execute(s)
            row = result.fetchone()
            return row

    def has_filestatus_filename(self, file_name):
        sql = sa.sql.text("""SELECT * FROM filestatus
                        WHERE filename =  :filename """)
        with self.engine.begin() as connection:
            result = connection.execute(sql, filename=file_name)
            return True if result.fetchone() else False

    def compare_filestatus_to_database(self, info):
        sql = sa.sql.text("""SELECT * FROM filestatus
                        WHERE filename =  :filename """)
        with self.engine.begin() as connection:
            result = connection.execute(sql, filename=info['filename'])
            database_info = result.fetchone()

        if not database_info:
            raise Exception('That filename does not exist!')

        if database_info['url'] != info['url']:
            return False

        if database_info['data_type'] != info['data_type']:
            return False

        if database_info['encoding'] != info.get('encoding', 'utf-8'):
            return False

        if database_info['priority'] != info.get('priority', 1):
            return False

        return True

    def add_filestatus(self, info):
        store = {
            'filename': info['filename'],
            'url': info['url'],
            'data_type': info['data_type'],
            'encoding': info.get('encoding', 'utf-8'),
            'priority': info.get('priority', 1),
        }
        with self.engine.connect() as conn:
            return conn.execute(self.filestatus.insert(), **store)

    """Returns a list of objects of each filestatus."""
    def list_filestatus(self):
        s = select([self.filestatus])
        with self.engine.connect() as conn:
            result = conn.execute(s)
            return list(result)

    def get_next_filestatus_to_fetch(self):
        sql = sa.sql.text("""SELECT * FROM filestatus
                WHERE fetch_success == 0 AND fetch_errors IS NULL
                ORDER BY priority DESC, filename DESC""")
        with self.engine.begin() as connection:
            result = connection.execute(sql)
            return result.fetchone()

    """Updates filestatus with start time"""
    def update_filestatus_fetch_start(self, filename):
        stmt = self.filestatus.update().\
            where(self.filestatus.c.filename == filename).\
            values(fetch_start_datetime=datetime.datetime.now())

        with self.engine.connect() as conn:
            return conn.execute(stmt)

    """Updates filestatus when fetched, takes boolean success flag, and a string of errors."""
    def update_filestatus_fetch_end(self, filename, errors=[], warnings=[]):
        stmt = self.filestatus.update().\
            where(self.filestatus.c.filename == filename).\
            values(fetch_finished_datetime=datetime.datetime.now(),
                   fetch_success=(len(errors) == 0),
                   fetch_errors=json.dumps(errors),
                   fetch_warnings=json.dumps(warnings)
                   )
        with self.engine.connect() as conn:
            return conn.execute(stmt)

    def update_session_gather_start(self):
        stmt = self.session.update().values(gather_start_datetime=datetime.datetime.now())
        with self.engine.connect() as conn:
            return conn.execute(stmt)

    """Updates session when done gathering, takes boolean success flag, and a list of errors."""
    def update_session_gather_end(self, success, errors, stacktrace):
        args = {}
        args["gather_finished_datetime"] = datetime.datetime.now()
        if success:
            args["gather_success"] = True
        else:
            args["gather_success"] = False
            args["gather_errors"] = json.dumps(errors)
            args["gather_stacktrace"] = str(stacktrace)
        stmt = self.session.update().values(**args)
        with self.engine.connect() as conn:
            return conn.execute(stmt)

    def update_session_fetch_start(self):
        stmt = self.session.update().values(fetch_start_datetime=datetime.datetime.now())
        with self.engine.connect() as conn:
            return conn.execute(stmt)

    """Updates session when done fetching, takes boolean success flag, and json string of errors."""
    def update_session_fetch_end(self):

        sql = sa.sql.text("""SELECT * FROM filestatus
                       WHERE fetch_success == 0""")
        with self.engine.begin() as connection:
            result = connection.execute(sql)
            success = not result.fetchone()

        stmt = self.session.update().values(
                                    fetch_success=success,
                                    fetch_finished_datetime=datetime.datetime.now())
        with self.engine.connect() as conn:
            return conn.execute(stmt)

    """Merge scrape status and all file status so we can display them."""
    def get_dict(self):
        with self.engine.connect() as conn:
            s = select([self.session])
            result = conn.execute(s)
            row = dict(result.fetchone())

            row['gather_errors'] = json.loads(row['gather_errors']) if row['gather_errors'] else None
            row['file_status'] = {}
            s = select([self.filestatus])
            result = conn.execute(s)
            for data in result:
                data = dict(data)
                data['fetch_errors'] = json.loads(data['fetch_errors']) if data['fetch_errors'] else None
                data['fetch_warnings'] = json.loads(data['fetch_warnings']) if data['fetch_warnings'] else None
                row['file_status'][data['filename']] = data

            return row

    def force_fetch_to_gather(self):
        with self.engine.connect() as conn:
            sql = sa.sql.text("""DELETE FROM filestatus WHERE fetch_success == 0""")
            conn.execute(sql)
