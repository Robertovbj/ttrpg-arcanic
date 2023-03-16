import sqlite3

class Database:
    def __init__(self):
        self.conn = sqlite3.connect("apocalypse.db")
        self.conn.execute("PRAGMA foreign_keys = 1")
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
    
    def update(self, table_name, primary_key, record_id, **kwargs):
        # Generate SET clause using keyword arguments
        set_clause = ', '.join([f"{key} = ?" for key in kwargs.keys()])

        # Generate query string
        query = f"UPDATE {table_name} SET {set_clause} WHERE {primary_key} = ?"

        # Generate parameter tuple
        params = tuple(kwargs.values()) + (record_id,)

        # Execute query and commit changes
        self.cursor.execute(query, params)
        self.conn.commit()

        # Return number of affected rows
        return self.cursor.rowcount
    
    def delete(self, table_name, column_name, value):
        query = f"DELETE FROM {table_name} WHERE {column_name} = ?"
        self.cursor.execute(query, (value,))
        self.conn.commit()
        
    def close(self):
        """Close the database connection"""
        self.conn.close()
