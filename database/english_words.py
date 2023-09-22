from peewee import Model, SqliteDatabase, CharField

db = SqliteDatabase('./uppsala_wordbook.db')

class EnglishWordBook(Model):
    letter = CharField()
    balochi = CharField()
    latin = CharField()
    definitions = CharField()

    class Meta:
        database = db
        table_name = 'word_data'

db.connect()