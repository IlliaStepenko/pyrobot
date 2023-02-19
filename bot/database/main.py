import asyncio
import os

import asyncpg
import psycopg2


class AsyncDataSource:
    def __init__(self):
        loop = asyncio.get_event_loop()

        try:
            from .local_config import DBConfig as Config
            pool = asyncpg.create_pool(dsn=Config.DSN)
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

    async def get_config(self):
        sql = ''' SELECT * FROM public."BotConfig"'''
        return await self.pool.fetch(sql)

    async def close(self):
        pass
       

