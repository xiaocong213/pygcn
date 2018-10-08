import astropy.units as u
import re
from lxml import etree
from pathlib import Path
from astropy.time import Time

########################################
# HELPER FUNCTIONS
########################################
def element2dict(e, depth=None):
    """Deprecated"""
    if len(e) == 0 or depth == 0:
        return e
    if not (depth is None):
        depth -= 1
    else:
        d = {}

        for child in e.iterchildren():
            d[child.tag] = element2dict(child, depth)

        return d


def value_by_name(e, name):
    """Deprecated"""
    for child in e:
        d = child.attrib
        if d['name'] == name:
            return d['value']

########################################
# MAIN
########################################

def parse(root):
    # Find and store elements
    # elements = {'who': None, 'what': None, 'wherewhen': None}
    # for child in root:
    #     tag = child.tag.lower()
    #     if tag in elements:
    #         elements[tag] = child

    # Define important children elements
    ivorn = root.attrib['ivorn']
    what = root.find('./What')
    wherewhen = root.find('./WhereWhen')
    astro_coords = wherewhen.find('./ObsDataLocation/ObservationLocation/AstroCoords')
    pos2D = astro_coords.find('./Position2D')

    # Extracting Values
    trigger_type = re.search('#[^\d]*[^\d]', ivorn)[0].replace('#', '')
    trigger_type =  trigger_type[:-1] if trigger_type[-1] == '_' else trigger_type
    trigger_id = what.find("./Param[@name='TrigID']").attrib['value']
    trigger_sequence = what.find("./Param[@name='Sequence_Num']").attrib['value']
    time = astro_coords.find('./Time/TimeInstant/ISOTime').text
    RA, Dec = pos2D.find('./Value2/C1').text, pos2D.find('./Value2/C1').text
    err = pos2D.find('Error2Radius').text

    comment = None
    if "LVC" in ivorn:
        skymap = what.find("./Param[@name='SKYMAP_URL_FITS_BASIC']")
        skymap = skymap.attrib['value'] if skymap else None
        comment = skymap
    elif "Fermi" in ivorn:
        Long_short = what.find("./Group[@name='Trigger_ID']/Param[@name='Long_short']")
        Long_short = Long_short.attrib['value'] if Long_short else None
        comment = Long_short


    # Parse and Clean
    trigger_id = int(trigger_id)
    trigger_sequence = int(trigger_sequence)
    time = Time(time).iso

    deg2arcsec = u.deg.to('arcsec')  # 3600
    RA = float(RA) * deg2arcsec
    Dec = float(Dec) * deg2arcsec
    radius_err = float(err) * deg2arcsec

    # Collect all data into a record (dictionary)
    data = {
        "TriggerNumber": trigger_id,
        "TriggerSequence": trigger_sequence,
        "TriggerType": trigger_type,
        "Time": time,
        "RA": RA,
        "Dec": Dec,
        "ErrorRadius": radius_err,
        'Comment': comment
    }

    return data