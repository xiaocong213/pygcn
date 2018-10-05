#import astropy.units as u
import re
from lxml import etree
from pathlib import Path
from astropy.time import Time

########################################
# HELPER FUNCTIONS
########################################
def element2dict(e, depth=None):
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
    for child in e:
        d = child.attrib
        if d['name'] == name:
            return d['value']

########################################
# MAIN
########################################

def parse(root):
    rootdict = root.attrib  # Metadata for root

    # Find and store elements
    elements = {'who': None, 'what': None, 'wherewhen': None}
    for child in root:
        tag = child.tag.lower()
        if tag in elements:
            elements[tag] = child

    # Define important children elements
    ivorn = rootdict['ivorn']
    wherewhen = element2dict(elements['wherewhen'])
    astro_coords = wherewhen['ObsDataLocation']['ObservationLocation']['AstroCoords']
    pos2D = astro_coords['Position2D']

    # Extracting Values
    #trigger_type = re.search('#[^\d]*[^\d]', ivorn)[0].replace('#', '')
    trigger_type = re.search('/[A-Z]*#[^\d]*[^\d]', ivorn)[0].replace('#', '_')
    if trigger_type[0] == '/' :
        ##get rid of the last "_" symble
        trigger_type=trigger_type[1:]
    if trigger_type[-1] == '_' :
        ##get rid of the last "_" symble
        trigger_type=trigger_type[0:-1]
    trigger_id = value_by_name(elements['what'], 'TrigID')
    ##Fermi triggers had Sequence_Num, MAXI do not have it
    if 'GBM' in trigger_type :
        trigger_sequence = value_by_name(elements['what'], 'Sequence_Num')
    else :
        trigger_sequence = 1

    time = astro_coords['Time']['TimeInstant']['ISOTime'].text
    RA, Dec = pos2D['Value2']['C1'].text, pos2D['Value2']['C2'].text
    err = pos2D['Error2Radius'].text
    if 'AMON' in trigger_type :
        ##AMON error is given in arcmin, change it to degree
        err = err / 60.0

    # Parse and Clean
    trigger_id = int(trigger_id)
    trigger_sequence = int(trigger_sequence)
    time = Time(time).iso

    #deg2arcsec = u.deg.to('arcsec')  # 3600
    RA = float(RA)
    Dec = float(Dec)
    radius_err = float(err)

    # Collect all data into a record (dictionary)
    data = {
        "TriggerNumber": trigger_id,
        "TriggerSequence": trigger_sequence,
        "TriggerType": trigger_type,
        "Time": time,
        "RA": RA,
        "Dec": Dec,
        "ErrorRadius": radius_err,
        "Comment": 'test'
    }

    return data
