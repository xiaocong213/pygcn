# import astropy.units as u
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

    # Extracting Values
    ivorn_paths = ivorn.split(r'/')
    trigger_type = re.search(r'[^\d]*[^\d]', ivorn_paths[-1])[0].replace('#', '_')
    trigger_type = trigger_type[:-1] if trigger_type[-1] == '_' else trigger_type

    if 'amon' in str.lower(trigger_type):
        #amon, it uses ID, and run_id and event_id together to be ID
        print('this is a amon trigger')
        trigger_id = what.find("./Param[@name='run_id']").attrib['value']
        trigger_sequence = what.find("./Param[@name='event_id']")
    elif 'ms' == str.lower(trigger_type.split(r'_')[-1]) or 'ts' == str.lower(trigger_type.split(r'_')[-1]) :
        print('this is a GW O3 test trigger')
        #trigger_idtmp = what.find("./Param[@name='GraceID']").attrib['value']
        #trigger_id_date = trigger_idtmp
        #trigger_id_xyz  = trigger_idtmp
        #trigger_id_date = re.sub('[a-zA-Z]','',trigger_id_date)
        #trigger_id_xyz  = (re.sub('[0-9]',' ',trigger_id_xyz)).split()[-1]
        #idtmp=0
        #for letter in trigger_id_xyz :
        #    idtmp+=ord(letter)
        #trigger_id_xyz=idtmp
        #trigger_id=str(trigger_id_date)+str(trigger_id_xyz)
        #trigger_sequence = what.find("./Param[@name='Pkt_Ser_Num']")
        return None
    elif 's' == str.lower(trigger_type.split(r'_')[-1]) :
        print('this is a GW O3 real trigger')
        trigger_idtmp = what.find("./Param[@name='GraceID']").attrib['value']
        trigger_id_date = trigger_idtmp
        trigger_id_xyz  = trigger_idtmp
        trigger_id_date = re.sub('[a-zA-Z]','',trigger_id_date)
        trigger_id_xyz  = (re.sub('[0-9]',' ',trigger_id_xyz)).split()[-1]
        idtmp=0
        for letter in trigger_id_xyz :
            idtmp+=ord(letter)
        trigger_id_xyz=idtmp
        trigger_id=str(trigger_id_date)+str(trigger_id_xyz)
        trigger_sequence = what.find("./Param[@name='Pkt_Ser_Num']")
    else :
        trigger_id = what.find("./Param[@name='TrigID']").attrib['value']
        trigger_sequence = what.find("./Param[@name='Sequence_Num']")

    # Some voevents don't have Sequence_Num (e.g., MAXI)
    # another option is judge isinstance(trigger_sequence, etree._Element)
    trigger_sequence = trigger_sequence.attrib['value'] if trigger_sequence is not None else 1

    time = astro_coords.find('./Time/TimeInstant/ISOTime').text

    RA, Dec = astro_coords.find('./Position2D/Value2/C1'), astro_coords.find('./Position2D/Value2/C2')
    err = astro_coords.find('Position2D/Error2Radius')

    comment = None
    if ("lvc" in str.lower(ivorn)) or ("gwnet" in str.lower(ivorn)):
        #this is for O2
        #skymap = what.find("./Param[@name='SKYMAP_URL_FITS_BASIC']")
        #skymap = skymap.attrib['value'] if skymap is not None else None
        #this is for O3
        skymap = what.find("./Group[@type='GW_SKYMAP']/Param[@name='skymap_fits']")
        skymap = skymap.attrib['value'] if skymap is not None else None
        comment = skymap
    elif "fermi" in str.lower(ivorn):
        Long_short = what.find("./Group[@name='Trigger_ID']/Param[@name='Long_short']")
        Long_short = Long_short.attrib['value'] if Long_short is not None else None
        comment = Long_short

    # Parse and Clean
    trigger_id = int(trigger_id)
    trigger_sequence = int(trigger_sequence)
    time = Time(time).iso

    # deg2arcsec = u.deg.to('arcsec')  # 3600
    if 'lvc' in str.lower(ivorn) or 'gwnet' in str.lower(ivorn):
        RA = None
        Dec = None
        radius_err = None
    else:
        RA = float(RA.text)
        Dec = float(Dec.text)
        radius_err = float(err.text)
        ##AMON error is given in arcmin, change it to degree
        ##but in the trigger we received, it's given in degree, strange
        #if 'amon' in str.lower(trigger_type):
        #    radius_err = radius_err / 60.0

    # Collect all data into a record (dictionary)
    data = {
        "TriggerNumber": trigger_id,
        "TriggerSequence": trigger_sequence,
        "TriggerType": trigger_type,
        "Time": time,
        "RA": RA,
        "Dec": Dec,
        "ErrorRadius": radius_err,
        "Comment": comment
    }

    return data
