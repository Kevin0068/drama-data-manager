"""数据库管理器 - 初始化 SQLite 连接并创建所有表"""

import sqlite3


class Database:
    """SQLite 数据库管理器，负责连接管理和表创建。"""

    def __init__(self, db_path: str = "drama_manager.db"):
        """初始化数据库连接，启用外键，创建所有表。"""
        self._conn = sqlite3.connect(db_path)
        self._conn.execute("PRAGMA foreign_keys = ON")
        self._create_tables()

    def get_connection(self) -> sqlite3.Connection:
        """获取数据库连接。"""
        return self._conn

    def close(self):
        """关闭数据库连接。"""
        self._conn.close()

    def _create_tables(self):
        """创建所有数据表。"""
        cursor = self._conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS backends (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS drama_names (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                backend_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                FOREIGN KEY (backend_id) REFERENCES backends(id) ON DELETE CASCADE,
                UNIQUE(backend_id, name)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS months (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                backend_id INTEGER NOT NULL,
                label TEXT NOT NULL,
                FOREIGN KEY (backend_id) REFERENCES backends(id) ON DELETE CASCADE,
                UNIQUE(backend_id, label)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS imported_headers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                month_id INTEGER NOT NULL UNIQUE,
                headers_json TEXT NOT NULL,
                FOREIGN KEY (month_id) REFERENCES months(id) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS imported_rows (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                month_id INTEGER NOT NULL,
                row_index INTEGER NOT NULL,
                row_json TEXT NOT NULL,
                FOREIGN KEY (month_id) REFERENCES months(id) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS match_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                month_id INTEGER NOT NULL UNIQUE,
                matched_indices_json TEXT NOT NULL,
                FOREIGN KEY (month_id) REFERENCES months(id) ON DELETE CASCADE
            )
        """)

        self._conn.commit()
