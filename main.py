import gcn
import re
import astropy.units as u
from astropy.time import Time
from astrosql import AstroSQL
from astrosql.sqlconnector import connect
from voevent import voeventparser

cnx = connect(database='observation')
db = AstroSQL(cnx)
table = db.get_table("voevents")

########################################
# FILTERS
########################################
@gcn.include_notice_types(
    gcn.notice_types.FERMI_GBM_FLT_POS,
    gcn.notice_types.FERMI_GBM_GND_POS,
    gcn.notice_types.FERMI_GBM_FIN_POS,
    gcn.notice_types.SWIFT_BAT_GRB_POS_ACK,
    gcn.notice_types.AGILE_GRB_WAKEUP,
    gcn.notice_types.AGILE_GRB_GROUND,
    gcn.notice_types.AGILE_GRB_REFINED,
    gcn.notice_types.FERMI_LAT_POS_INI,
    gcn.notice_types.FERMI_LAT_GND,
    gcn.notice_types.MAXI_UNKNOWN,
    gcn.notice_types.MAXI_TEST,
    gcn.notice_types.LVC_PRELIM,
    gcn.notice_types.LVC_INITIAL,
    gcn.notice_types.LVC_UPDATE,
    gcn.notice_types.LVC_TEST,
    gcn.notice_types.LVC_CNTRPART,
    gcn.notice_types.AMON_ICECUBE_COINC,
    gcn.notice_types.AMON_ICECUBE_HESE,
    gcn.notice_types.CALET_GBM_FLT_LC,
    gcn.notice_types.CALET_GBM_GND_LC,
    gcn.notice_types.LVC_SUPER_PRELIM,
    gcn.notice_types.LVC_SUPER_INITIAL,
    gcn.notice_types.LVC_SUPER_UPDATE,
    gcn.notice_types.GWHEN_COINC,
    gcn.notice_types.AMON_ICECUBE_EHE
)

########################################
# MAIN
########################################

def handler(payload, root):
    print(root.attrib['ivorn'])

    # Parse event returned as data row
    data = voeventparser.parse(root)

    # send out email command
    #SendOutVoeventEmail contentfile

    # Write to database
    print(f"Writing the following to MySQL at observation.voevents:\n{data}")
    query = table.insert(data)
    query.execute()

if __name__ == '__main__':
    gcn.listen(handler=handler)
