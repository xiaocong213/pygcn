from peewee import *
from astrosql import AstroSQL
from astrosql.sqlconnector import connect

DB = AstroSQL(database='observation')
voevents_table = DB.get_table('voevents')


class GalaxySelections(Model):
    TriggerNumber = IntegerField(null=True)
    TriggerSequence = IntegerField(null=True)
    raDeg = DecimalField(null=True)
    decDeg = DecimalField(null=True)
    disMpc = DecimalField(null=True)
    Bmag = DecimalField(null=True)
    gladeID = IntegerField(null=True)
    DisToCentre_Arcmin = DecimalField(null=True)
    S_total = DecimalField(max_digits=15, decimal_places=14, null=True)
    P_pos = DecimalField(max_digits=15, decimal_places=14, null=True)
    P_dis = DecimalField(max_digits=15, decimal_places=14, null=True)
    S_loc = DecimalField(max_digits=15, decimal_places=14, null=True)
    S_lum = DecimalField(max_digits=15, decimal_places=14, null=True)
    S_det = DecimalField(max_digits=15, decimal_places=14, null=True)
    Kait_observable = CharField(max_length=1, null=True)
    Kait_observed = CharField(max_length=1, null=True)
    Time_observed = DateTimeField(null=True)
    Limit_mag = DecimalField(null=True)
    Comment = CharField(null=True)

    class Meta:
        database = DB.database
        table_name = 'voevents_galaxy'


if __name__ == "__main__":
    if not GalaxySelections.table_exists():
        GalaxySelections.create_table()

    # Add composite foreign key
    # DB.database.execute_sql(
    #     f"ALTER TABLE `{GalaxySelections._meta.table_name}`" +
    #     "ADD CONSTRAINT `TriggerID`" +
    #     "FOREIGN KEY (`TriggerNumber`, `TriggerSequence`) REFERENCES `voevents` (`TriggerNumber`, `TriggerSequence`) ON DELETE CASCADE;"
    # )
