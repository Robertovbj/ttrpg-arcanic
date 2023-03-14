import sqlite3

class Database:
    def __init__(self):
        self.conn = sqlite3.connect("apocalypse.db")
        self.cursor = self.conn.cursor()

    def insert(self, table_name, values):
        """Insert a new row into the given table with the given values"""
        placeholders = ', '.join(['?' for _ in range(len(values))])
        insert_query = f"INSERT INTO {table_name} VALUES ({placeholders})"
        self.cursor.execute(insert_query, values)
        self.conn.commit()

    def select(self, table_name, columns=None, where=None):
        """Select rows from the given table, optionally with a WHERE clause"""
        columns_str = '*' if columns is None else ', '.join(columns)
        where_str = '' if where is None else f" WHERE {where}"
        select_query = f"SELECT {columns_str} FROM {table_name}{where_str}"
        self.cursor.execute(select_query)
        return self.cursor.fetchall()

    def close(self):
        """Close the database connection"""
        self.conn.close()
