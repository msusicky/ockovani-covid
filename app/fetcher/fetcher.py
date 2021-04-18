import csv
from datetime import datetime
from email import utils as eut
from io import StringIO
from typing import Optional

import requests

from app import db


class Fetcher:
    def __init__(self, table: str, url: str, check_date=True, ignore_errors=False):
        self._table = table
        self._url = url
        self.check_date = check_date
        self.ignore_errors = ignore_errors

    def get_modified_date(self) -> Optional[datetime]:
        headers = requests.head(url=self._url).headers
        if 'last-modified' in headers:
            modified_tuple = eut.parsedate_tz(headers['last-modified'])
            modified_timestamp = eut.mktime_tz(modified_tuple)
            return datetime.fromtimestamp(modified_timestamp)
        else:
            return None

    def fetch(self, import_id: int) -> None:
        pass

    def _truncate(self) -> None:
        db.engine.execute('truncate table {}'.format(self._table))

    @staticmethod
    def _psql_insert_copy(table, conn, keys, data_iter):
        """
        Execute SQL statement inserting data

        Parameters
        ----------
        table : pandas.io.sql.SQLTable
        conn : sqlalchemy.engine.Engine or sqlalchemy.engine.Connection
        keys : list of str
            Column names
        data_iter : Iterable that iterates the values to be inserted
        """
        # gets a DBAPI connection that can provide a cursor
        dbapi_conn = conn.connection
        with dbapi_conn.cursor() as cur:
            s_buf = StringIO()
            writer = csv.writer(s_buf)
            writer.writerows(data_iter)
            s_buf.seek(0)

            columns = ', '.join('"{}"'.format(k) for k in keys)
            if table.schema:
                table_name = '{}.{}'.format(table.schema, table.name)
            else:
                table_name = table.name

            sql = 'COPY {} ({}) FROM STDIN WITH CSV'.format(
                table_name, columns)
            cur.copy_expert(sql=sql, file=s_buf)
