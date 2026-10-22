import mysql.connector
from app.config import DB_CONFIG

class Database:
    """Tầng truy cập dữ liệu MySQL, tách khỏi lớp giao diện."""
    def connect(self):
        return mysql.connector.connect(**DB_CONFIG)

    def fetch_all(self, sql, params=None):
        conn = self.connect()
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(sql, params or ())
            return cur.fetchall()
        finally:
            conn.close()

    def fetch_one(self, sql, params=None):
        rows = self.fetch_all(sql, params)
        return rows[0] if rows else None

    def execute(self, sql, params=None):
        conn = self.connect()
        try:
            cur = conn.cursor()
            cur.execute(sql, params or ())
            conn.commit()
            return cur.lastrowid
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
