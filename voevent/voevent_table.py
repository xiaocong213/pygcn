from peewee import *
from astrosql import AstroSQL
from astrosql.sqlconnector import connect

db = AstroSQL(database='observation')

class VOEvent(Model):
    TriggerNumber = IntegerField()
    TriggerSequence = IntegerField()
    TriggerType = TextField()
    Time = DateTimeField()
    RA = DecimalField(null=True, decimal_places=2)
    Dec = DecimalField(null=True, decimal_places=2)
    ErrorRadius = DecimalField(null=True)
    Comments = CharField(null=True)

    class Meta:
        database = db.db
        table_name = 'voevents'
        primary_key = CompositeKey('TriggerNumber', 'TriggerSequence')

if __name__ == "__main__":
    if not VOEvent.table_exists():
        VOEvent.create_table()
