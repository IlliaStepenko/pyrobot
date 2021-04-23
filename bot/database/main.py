import os
import psycopg2


class DataSource:

    def __init__(self):
        try:
            from .local_config import DBConfig
            self.conn = psycopg2.connect(**DBConfig.as_conn_param_dict())
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