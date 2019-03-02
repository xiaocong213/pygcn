# import astropy.units as u
import re
import logging
from astropy.time import Time
from gcn.notice_types import _notice_types

"""
XML Parser for VOEvent. Specifically built for VoEvent triggers sent through the Gamma-Ray Coordinates Network (GCN). 
"""

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class VOEvent:
    NOTICE_TYPES = {int(v): k for k, v in _notice_types.items()}  # {notice_number: notice_type}

    def __init__(self, root, trigger_type=None):
        """
        Instantiate from an XML lxml element.

        Parameters
        ----------
        root : lxml.etree.Element
        trigger_type : str
            Trigger type/variant of the voevent.
        """
        self.type = trigger_type
        self.role = root.attrib['role']
        self.who = root.find('./Who')
        self.what = root.find('./What')
        self.wherewhen = root.find('./WhereWhen')
        self.why = root.find('./Why')  # Usually missing

        self.number, self.sequence = self.get_trigger_id()
        self.time = self.get_time()
        self.RA, self.dec, self.error = self.get_radecerror_tuple()
        self.comment = self.get_comment()

    def get_trigger_id(self):
        """
        Parses the trigger id from What/Param with names "TrigID" and "Pkt_Ser_Num"
        for trigger number and trigger sequence respectively.
        Returns
        -------
        trigger_id: tuple
        A tuple of (trigger number, trigger sequence)
        """
        # trigger_type = re.findall(r'[^\d]*[^\d]', ivorn_paths[-1])[0].replace('#', '_')
        # trigger_type = trigger_type[:-1] if trigger_type[-1] == '_' else trigger_type
        number = self.what.find("./Param[@name='TrigID']").get('value')
        sequence = self.what.find("./Param[@name='Pkt_Ser_Num']").get('value')
        return number, sequence

    def get_time(self):
        """
        Parses trigger time from Wherewhen/*/IsoTime returned as a iso datetime formatted string.

        Returns
        -------
        datetime : str
        """
        return self.wherewhen.find('.//ISOTime').text

    def get_radecerror_tuple(self):
        """
        Parses RA, Dec, Radius error from WhereWhen/PositionID/*/[Value2/C1, Value2/C2, Error2Radius].

        Returns
        -------
        coordinate_tuple : tuple
            Coordinate tuple of (RA, Dec, error)
        """
        try:
            position2d = self.wherewhen.find('./Position2D')  # May be missing
            return position2d.find('.//Value2/C1').text, position2d.find('.//Value2/C2').text, position2d.find(
                './Error2Radius').textq
        except AttributeError:
            return (None, None, None)

    def get_comment(self):
        """
        Parses comments from relevant tags. None for the parent VOEvent class.

        Returns
        -------
        comment : str
        """
        return None

    def get_data(self):
        """
        Returns
        -------
        data : dict
        """
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
        notice_types = {k: v for k, v in VOEvent.NOTICE_TYPES.items() if
                        str.lower(instrument) in str.lower(VOEvent.NOTICE_TYPES.get(k))}
        return notice_types

    class TestError(Exception):
        pass


class LVC(VOEvent):
    INSTRUMENT = 'LVC'
    NOTICE_TYPES = VOEvent.get_notice_types(INSTRUMENT)

    def __init__(self, root, ignore_test=False, **kwargs):
        self.ignore_test = ignore_test
        super().__init__(root)

    def get_trigger_id(self):
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

        # Extract the Grace ID
        grace_id = self.what.find("./Param[@name='GraceID']").get('value')
        number = re.findall(r'[\d].*', grace_id)[0]
        sequence = self.what.find("./Param[@name='Pkt_Ser_Num']").get('value')
        if self.ignore_test and self.role == 'test':
            message = 'This is a GW O3 test trigger.'
            log.info(message)
            raise VOEvent.TestError(message)
        return number, sequence

    def get_comment(self):
        try:
            # this is for O2
            # skymap = what.find("./Param[@name='SKYMAP_URL_FITS_BASIC']").get('value')
            # skymap = skymap.attrib['value'] if skymap is not None else None

            # this is for O3
            skymap = self.what.find("./Group[@type='GW_SKYMAP']/Param[@name='skymap_fits']").get('value')
            # skymap = self.what.find(".//Param[@name='skymap_fits']").get('value')
            return skymap
        except AttributeError:
            return None


class Fermi(VOEvent):
    INSTRUMENT = 'FERMI'
    NOTICE_TYPES = VOEvent.get_notice_types(INSTRUMENT)

    def __init__(self, root, **kwargs):
        super().__init__(root, **kwargs)

    def get_trigger_id(self):
        try:
            number = self.what.find("./Param[@name='TrigID']").get('value')
            sequence = self.what.find("./Param[@name='Sequence_Num']").get('value')
            return number, sequence
        except AttributeError:
            return (None, None)

    def get_comment(self):
        try:
            long_short = self.what.find("./Group[@name='Trigger_ID']/Param[@name='Long_short']").get('value')
            return long_short
        except AttributeError:
            return None


class AMON(VOEvent):
    INSTRUMENT = 'AMON'
    NOTICE_TYPES = VOEvent.get_notice_types(INSTRUMENT)

    def __init__(self, root, **kwargs):
        super().__init__(root, **kwargs)

    def get_trigger_id(self):
        # amon, Trigger number is in "run_id" and Trigger sequence is in "event_id".
        print('This is a AMON trigger.')
        try:
            number = self.what.find("./Param[@name='run_id']").get('value')
            sequence = self.what.find("./Param[@name='event_id']").get('value')
            return number, sequence
        except AttributeError:
            return (None, None)


TRIGGERS = [
    LVC,
    Fermi,
    AMON,
    VOEvent
]


def parse(root, ignore_test=False):
    """
    Parses a VOEvent XML formatted as an lxml.etree.Element extracting relevant data for database.
    See [VOEvent].get_data for data outputs.

    Parameters
    ----------
    root: lxml.etree.Element

    Returns
    -------
    data: dict or None

    """
    what = root.find('./What')

    # Extract the notice/trigger type stored in What/Param[name='Packet_Type'][value].
    packet_type = what.find("./Param[@name='Packet_Type']").get('value')
    if str.isdigit(packet_type):  # The packet type will either be a number or string
        trigger_type = VOEvent.NOTICE_TYPES.get(int(packet_type))
    else:
        trigger_type = packet_type

    # Check if the packet type was parse-able
    if trigger_type is None:  # Quit if no trigger type information can be parsed
        log.warning(r"No trigger type could be parsed from Param \"Packet_Type\" ")
        return None
    else:
        trigger_type = str.lower(trigger_type)

    # Use the trigger type to get the proper trigger class and parse the XML inside Trigger instance.
    try:
        trigger = None
        for Trigger in TRIGGERS:  # go through each trigger class
            notice_types_lower = [str.lower(n) for n in
                                  Trigger.NOTICE_TYPES.values()]  # all possible trigger type name
            if trigger_type in notice_types_lower:  # check trigger type name to all possible ones
                trigger = Trigger(root, trigger_type=trigger_type)
                break
    except VOEvent.TestError:
        log.warning("Quitting...\n")
        return None

    # Check trigger number and trigger sequence
    if (trigger is None):
        log.warning("Couldn't parse trigger number or trigger sequence from this trigger. Quitting...\n")
        return None
    if None in [trigger.number, trigger.sequence]:
        log.warning("Couldn't parse trigger number or trigger sequence from this trigger.\n"
                    + f"These information were parsed at best:\n{trigger.get_data()}\nQuitting...\n")
        return None

    return trigger.get_data()
