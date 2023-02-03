import asyncio
import os

import asyncpg
import psycopg2


class AsyncDataSource:
    def __init__(self):
        loop = asyncio.get_event_loop()

        try:
            from .local_config import DBConfig as Config
            pool = asyncpg.create_pool(
                    user=Config.USER,
                    password=Config.PASSWORD,
                    host=Config.HOST,
                    port='5432',
                    database=Config.DBNAME
                )
        except Exception as e:
            dsn = os.environ.get('DATABASE_URL', None)
            pool = asyncpg.create_pool(dsn=dsn)

        self.pool = loop.run_until_complete(
            pool
        )

    async def get_target_chats(self):
        sql = '''SELECT * FROM public."TargetChats";'''
        return await self.pool.fetch(sql)

    async def get_source_chats(self):
        sql = '''SELECT * FROM public."SourceChats";'''
        return await self.pool.fetch(sql)

    async def get_white_list(self):
        sql = '''SELECT * FROM public."WhiteList";'''
        return await self.pool.fetch(sql)

    async def close(self):
        pass
        # self.conn.close()
        # self.cursor.close()


class DataSource:

    def __init__(self):
        try:
            from .local_config import DBConfig as Config
            self.conn = psycopg2.connect(**Config.as_conn_param_dict())
        except Exception as e:
            database_url = os.environ['DATABASE_URL']
            self.conn = psycopg2.connect(database_url, sslmode='require')

        self.cursor = self.conn.cursor()

    def get_target_chats(self):
        self.cursor.execute('''SELECT * FROM public."TargetChats";''')
        return self.cursor.fetchall()

    def get_source_chats(self):
        self.cursor.execute('''SELECT * FROM public."SourceChats";''')
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()
        self.cursor.close()
