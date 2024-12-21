
"""
Database Configuration Module

Description:
Manages database connections and connection pooling.
Implementation includes:
- Connection pool initialization
- Connection management
- PostgreSQL configuration
"""





import psycopg2
from psycopg2 import pool
from urllib.parse import quote_plus

# DataBase Connection and Management using psycopg2

class DatabasePool:
    _connection_pool = None

    @classmethod
    def initialize(cls):
        if not cls._connection_pool:
            cls._connection_pool = pool.SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                user='user',
                password='',
                host='localhost',
                port='5432',
                database='library_management'
            )
        return cls._connection_pool

    @classmethod
    def get_connection(cls):
        if not cls._connection_pool:
            cls.initialize()
        return cls._connection_pool.getconn()

    @classmethod
    def return_connection(cls, connection):
        cls._connection_pool.putconn(connection)