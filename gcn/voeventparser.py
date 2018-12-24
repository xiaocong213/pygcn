# import astropy.units as u
import re
import logging
from astropy.time import Time
from gcn.notice_types import _notice_types

"""
XML Parser for VOEvent. Specifically built for VoEvent triggers sent through the Gamma-Ray Coordinates Network (GCN). 
"""

log = logging.getLogger(__name__)


class Voevent:
    NOTICE_TYPES = {v: k for k, v in _notice_types.items()}  # {notice_number: notice_type}

    def __init__(self, root, trigger_type=None):
        """
        Instantiate from an XML lxml element.
        """
        self.type = trigger_type
        self.role = root.attrib['role']
        self.who = root.find('./who')
        self.what = root.find('./what')
        self.wherewhen = root.find('./wherewhen')
        self.why = root.find('./why')  # Usually missing

        self.number, self.sequence = self.get_trigger_id()
        self.time = self.get_time()
        self.RA, self.dec, self.error = self.get_radecerror_tuple()
        self.comment = self.get_comment()

    def get_trigger_id(self):
        # trigger_type = re.findall(r'[^\d]*[^\d]', ivorn_paths[-1])[0].replace('#', '_')
        # trigger_type = trigger_type[:-1] if trigger_type[-1] == '_' else trigger_type
        number = self.what.find("./Param[@name='TrigID']").get('value')
        sequence = self.what.find("./Param[@name='Pkt_Ser_Num']").get('value')
        return number, sequence

    def get_time(self):
        return self.wherewhen.find('.//ISOTime').text

    def get_radecerror_tuple(self):
        try:
            position2d = self.wherewhen.find('./Position2D')  # May be missing
            return position2d.find('./Value/C1').text, position2d.find('./Value/C2').text, position2d.find(
                './Error2Radius').text
        except AttributeError:
            return None

    def get_comment(self):
        return None

    def get_data(self):
        data = {
            "TriggerNumber": self.number,
            "TriggerSequence": self.sequence,
            "TriggerType": self.type,
            "Time": self.time,
            "RA": self.RA,
            "Dec": self.dec,
            "ErrorRadius": self.error,
            "Comment": self.comment
        }
        return data

    @staticmethod
    def get_notice_types(instrument):
        notice_types = {k: v for k, v in Voevent.NOTICE_TYPES.items() if
                        str.lower(instrument) in str.lower(Voevent.NOTICE_TYPES.get(k))}
        return notice_types


class Lvc(Voevent):
    INSTRUMENT = 'LVC'
    NOTICE_TYPES = Voevent.get_notice_types(INSTRUMENT)

    def __init__(self, root):
        super().__init__(root)

    def get_trigger_id(self):
        if self.role == 'test':
            log.info('This is a GW O3 test trigger.')
            return None
        # elif 'ms' == str.lower(trigger_type.split(r'_')[-1]) or 'ts' == str.lower(trigger_type.split(r'_')[-1]):
        #     print('this is a GW O3 test trigger')
        #     return None
        # elif 's' == str.lower(trigger_type.split(r'_')[-1]):
        #     trigger_numbertmp = what.find("./Param[@name='GraceID']").get('value')
        #     trigger_number_date = trigger_numbertmp
        #     trigger_number_xyz = trigger_numbertmp
        #     trigger_number_date = re.sub('[a-zA-Z]', '', trigger_number_date)
        #     trigger_number_xyz = (re.sub('[0-9]', ' ', trigger_number_xyz)).split()[-1]
        #     idtmp = 0
        #     for letter in trigger_number_xyz:
        #         idtmp += ord(letter)
        #     trigger_number_xyz = idtmp
        #     trigger_number = str(trigger_number_date) + str(trigger_number_xyz)
        #     trigger_sequence = what.find("./Param[@name='Pkt_Ser_Num']").get('value')
        else:
            log.info('This is a GW O3 real trigger.')
            grace_id = self.what.find("./Param[@name='GraceID']").get('value')
            number = re.findall(r'[\d].*', grace_id)[0]
            sequence = self.what.find("./Param[@name='Pkt_Ser_Num']").get('value')
        return number, sequence

    def get_comment(self):
        # this is for O2
        # skymap = what.find("./Param[@name='SKYMAP_URL_FITS_BASIC']").get('value')
        # skymap = skymap.attrib['value'] if skymap is not None else None

        # this is for O3
        skymap = self.what.find("./Group[@type='GW_SKYMAP']/Param[@name='skymap_fits']").get('value')
        # skymap = self.what.find(".//Param[@name='skymap_fits']").get('value')

        return skymap


class Fermi(Voevent):
    INSTRUMENT = 'FERMI'
    NOTICE_TYPES = Voevent.get_notice_types(INSTRUMENT)

    def __init__(self, root):
        super().__init__(root)

    def get_trigger_id(self):
        number = self.what.find("./Param[@name='TrigID']").get('value')
        sequence = self.what.find("./Param[@name='Sequence_Num']").get('value')
        return number, sequence

    def get_comment(self):
        try:
            long_short = self.what.find("./Group[@name='Trigger_ID']/Param[@name='Long_short']").get('value')
            return long_short
        except AttributeError:
            return None


class Amon(Voevent):
    INSTRUMENT = 'AMON'
    NOTICE_TYPES = Voevent.get_notice_types(INSTRUMENT)

    def __init__(self, root):
        super().__init__(root)

    def get_trigger_id(self):
        # amon, Trigger number is in "run_id" and Trigger sequence is in "event_id".
        print('This is a AMON trigger.')
        number = self.what.find("./Param[@name='run_id']").get('value')
        sequence = self.what.find("./Param[@name='event_id']").get('value')
        return number, sequence


TRIGGERS = [
    Lvc,
    Fermi,
    Amon
]


def parse(root):
    """
    Parameters
    ----------
    root: lxml.etree.Element

    Returns
    -------
    data: dict or None
    """
    # Define important children elements
    # ivorn = root.attrib['ivorn']
    what = root.find('./What')
    wherewhen = root.find('./WhereWhen')

    # The notice type or trigger type is extracted from "Packet_Type" What/Param.
    packet_type = what.find("./Param[@name='Packet_Type']").get('value')
    if type(packet_type) is int:
        trigger_type = Voevent.NOTICE_TYPES.get(packet_type)
    else:
        trigger_type = packet_type

    # Check if the packet type was parsable
    if trigger_type is None:  # Quit if no trigger type information can be parsed
        log.warning(r"No trigger type could be parsed from Param \"Packet_Type\" ")
        return None

    # Use the trigger type to get the proper trigger class and parse the XML inside Trigger instance.
    trigger = None
    for Trigger in TRIGGERS:
        if trigger_type in Trigger.NOTICE_TYPES:
            trigger = Trigger(root, trigger_type)
            break

    # Check trigger number and trigger sequence
    if (trigger is None) or (None in [trigger.number, trigger.sequence]):
        log.warning("Couldn't parse trigger number or trigger sequence from this trigger. Quitting...")
        return None

    return trigger.get_data()
