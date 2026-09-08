"""
现代纺织化学纤维全景数据库模式初始化工具 (Textile Chemical Fibers Schema Builder - 2026)
以纺织服装、家纺与产业用纺织品为核心，系统构建全系纤维物理化学及纺织工程深度知识架构
"""

import sqlite3
import os

DB_PATH = "chemical_fibers.db"
SQL_SCHEMA_PATH = "schema.sql"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_schema(conn):
    if not os.path.exists(SQL_SCHEMA_PATH):
        raise FileNotFoundError(f"Schema file not found: {SQL_SCHEMA_PATH}")
    with open(SQL_SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    conn.executescript(schema_sql)

def main():
    conn = get_db_connection()
    init_schema(conn)
    print("Textile Chemical Fibers schema initialized successfully from schema.sql.")
    conn.close()

if __name__ == "__main__":
    main()
