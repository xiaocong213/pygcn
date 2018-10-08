import gcn
import re
import requests
import astropy.units as u
from astropy.time import Time
from astrosql import AstroSQL
from astrosql.sqlconnector import connect
from galaxy_selection.gcnfollowup import *
from voevent import voeventparser
from warnings import warn
cnx = connect(database='observation')
db = AstroSQL(cnx)
voevents_table = db.get_table("voevents")
galaxy_table = db.get_table("galaxy_selections")


########################################
# FILTERS
########################################
# TODO Deprecate the gcn filtering to use XML parsing instead.
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
    # SendOutVoeventEmail contentfile

    # Write to database
    print(f"Writing the following to MySQL at observation.voevents:\n{data}")
    query = voevents_table.insert(data)
    query.execute()

    # Develop galaxy list
    if "fermi" in str.lower(data['TriggerType']):
        peakz = 0.5 if 'short' in data['Comment'] else 1
        g1 = select_gladegalaxy_accordingto_location_radecpeakz(data['RA'], data['Dec'], data['ErrorRadius'], peakz)
    elif "lvc" in str.lower(data['TriggerType']):
        fname = "__file__/skymaps/{}_{}_{}.fits.gz".format(data['TriggerType'], data['TriggerNumber'], data['TriggerSequence'])
        response = requests.get(data['comment'])
        try:
            response.raise_for_status()
            with open(fname, 'wb') as file:                                  
                file.write(response.raw)
            g1 = select_gladegalaxy_accordingto_location_gw(fname)
        except requests.exceptions.HTTPError as e:
             warn(f"{e}\nNo skymap could be stored in the database and downloaded. Continuing...")
             g1 = select_gladegalaxy_accordingto_location_radecpeakz(data['RA'], data['Dec'], data['ErrorRadius'], 1)
        
    else:
        # TODO How should we deal with neutrino alerts?
        raise NotImplementedError

    g2 = select_gladegalaxy_accordingto_luminosity(g1)
    g3 = select_gladegalaxy_accordingto_detectionlimit(g2)
    g3_df = g3.to_pandas()
    g3_df['TriggerNumber'] = data['TriggerNumber']
    g3_df['TriggerSequence'] = data['TriggerSequence']

    data = g3_df.to_dict('records')
    query = galaxy.insert(data)
    query.execute()


if __name__ == '__main__':
    gcn.listen(handler=handler)
