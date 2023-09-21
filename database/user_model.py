from peewee import Model, SqliteDatabase, CharField

db = SqliteDatabase('bot_users.db')

class User(Model):
    chat_id = CharField(unique=True)
    fist_name = CharField()
    username = CharField(null=True)

    class Meta:
        database = db

db.connect()
db.create_tables([User], safe=True)