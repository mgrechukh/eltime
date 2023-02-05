import sqlite3
import time

q_create = "CREATE TABLE if not exists works (started int not null primary key, last_updated int not null, entry_text text);"
q_update = "INSERT OR REPLACE INTO works (started, last_updated, entry_text) values (?, ?, ?)"
q_aggregate = "SELECT strftime('%Y-%m-%d', datetime(last_updated, 'unixepoch')) as day, strftime('%Y-%m-%d %H:00', datetime(last_updated, 'unixepoch')) as end_hour, sum(last_updated - started) as duration, entry_text from works where last_updated > ? group by end_hour, entry_text"
q_entries = "SELECT DISTINCT entry_text from works"

class SqliteRecorder:
    def __init__(self, fname):
        self.conn = sqlite3.connect(fname, isolation_level=None)
        self.conn.execute('pragma journal_mode=wal')

        self.cursor = self.conn.cursor()
        self.cursor.execute(q_create)
        self.conn.commit()

    def get_entries(self):
        for d in self.cursor.execute(q_entries).fetchall():
            yield d[0]

    def update_session(self, start_ts, entry_text, now = 0):
        if not now:
            now = time.time()
        self.cursor.execute(q_update, (int(start_ts), now, entry_text))
        self.conn.commit()

    def get_aggregated_stats(self, notbefore = 0):
        return self.cursor.execute(q_aggregate, (notbefore, )).fetchall()
