from peewee import *
from astrosql import AstroSQL
from astrosql.sqlconnector import connect

cnx = connect(database='observation')
db = AstroSQL(cnx)

class VOEvent(Model):
    TriggerNumber = IntegerField()
    TriggerSequence = IntegerField()
    TriggerType = TextField()
    Time = DateTimeField()
    RA = DecimalField(null=True)
    Dec = DecimalField(null=True)
    ErrorRadius = DecimalField(null=True)

    class Meta:
        database = db.db
        table_name = 'voevents'

if __name__ == "__main__":
    if not VOEvent.table_exists():
        VOEvent.create_table()