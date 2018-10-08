from peewee import *
from astrosql import AstroSQL
from astrosql.sqlconnector import connect

DB = AstroSQL(database='observation')
voevents_table = DB.get_table('voevents')

class GalaxySelections(Model):
    TriggerNumber = IntegerField()
    TriggerSequence = IntegerField()
    RA = DecimalField(null=True)
    Dec = DecimalField(null=True)
    Bmag = DecimalField(null=True)
    GladeID = IntegerField(null=True)
    DisToCentre_Arcmin = DecimalField(null=True)
    DisMpc = DecimalField(null=True) 
    S_total = DecimalField(max_digits=15, decimal_places=14, null=True)
    P_pos = DecimalField(max_digits=15, decimal_places=14, null=True)
    P_dis = DecimalField(max_digits=15, decimal_places=14, null=True)
    S_loc = DecimalField(max_digits=15, decimal_places=14, null=True)
    S_lum = DecimalField(max_digits=15, decimal_places=14, null=True)
    S_det = DecimalField(max_digits=15, decimal_places=14, null=True) 

    class Meta:
        database = DB.database
        table_name = 'galaxy_selections'

if __name__ == "__main__":
    if not GalaxySelections.table_exists():
        GalaxySelections.create_table()

    # Add composite foreign key
    DB.database.execute_sql(
        f"ALTER TABLE `{GalaxySelections._meta.table_name}`" +
        "ADD CONSTRAINT `TriggerID`" +
        "FOREIGN KEY (`TriggerNumber`, `TriggerSequence`) REFERENCES `voevents` (`TriggerNumber`, `TriggerSequence`);  "
    )
