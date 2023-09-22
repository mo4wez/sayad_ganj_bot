from peewee import Model, SqliteDatabase, CharField, PrimaryKeyField, FieldAlias

eng_db = SqliteDatabase(r'C:\Users\moawezz\Desktop\Sayad-bot\database\uppsala_wordbook.db')

if not eng_db.is_closed():
    eng_db.close()


class EnglishWordBook(Model):
    letter = CharField()
    balochi = CharField()
    latin = CharField()
    definitions = CharField()

    class Meta:
        database = eng_db
        table_name = 'word_data'

id_alias = FieldAlias(EnglishWordBook.id, 'id_alias')

eng_db.connect()
eng_db.create_tables([EnglishWordBook], safe=True)

primary_key_field_name = EnglishWordBook._meta.primary_key.name
print("Primary Key Field Name:", primary_key_field_name)