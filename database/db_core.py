from peewee import Model, SqliteDatabase, CharField, PrimaryKeyField


db = SqliteDatabase(r'C:\Users\moawezz\Desktop\Sayad-bot\database\wordbook.db')

class WordBook(Model):
    _id = PrimaryKeyField()
    betaNoSymbols = CharField()
    betaSymbols = CharField()
    langNoSymbols = CharField()
    langLowercase = CharField()
    langFullWord = CharField()
    entry = CharField()
    soundName = CharField()


    class Meta:
        database = db
        table_name = 'wordbook'


db.connect()