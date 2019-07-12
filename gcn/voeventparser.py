# import astropy.units as u
import re
import logging
from lxml import etree
from gcn.notice_types import _notice_types

"""
XML Parser for VOEvent. Specifically built for VoEvent triggers sent through the Gamma-Ray Coordinates Network (GCN). 
"""

log = logging.getLogger(__name__)
FORMAT = '[%(asctime)s] %(module)s, line %(lineno)d: %(message)s '
logging.basicConfig(level=logging.INFO, format=FORMAT)


class VOEvent:
    NOTICE_TYPES = {int(v): k for k, v in _notice_types.items()}  # {notice_number: notice_type}

    def __init__(self, root, trigger_type=None, ignore_test=True):
        """
        Instantiate from an XML lxml element.

        Parameters
        ----------
        root : lxml.etree.Element
        trigger_type : str
            Trigger type/variant of the voevent.
        """
        self.type = trigger_type
        self.ignore_test = ignore_test
        self.role = root.attrib['role']
        self.check_test()  # Usually raises VOEvent exception

        self.who = root.find('./Who')
        self.what = root.find('./What')
        self.wherewhen = root.find('./WhereWhen')
        self.why = root.find('./Why')  # Usually missing

        self.number, self.sequence = self.get_trigger_id()
        self.time = self.get_time()
        self.RA, self.dec, self.error = self.get_radecerror_tuple()
        self.comment = self.get_comment()

    @staticmethod
    def parse_from_xml(fpath_or_root, ignore_test=True):
        """
        Parses a VOEvent XML object (lxml.etree.Element) extracting relevant data as described by VOEvent#get_data.

        Parameters
        ----------
        fpath_or_root: lxml.etree.Element
            VOEvent XML object
        ignore_test: bool
            If True and VOEvent has role='test', return None.
            A message may be logged specified by each VOEvent#__init__.

        Returns
        -------
        trigger: VOEvent
        """
        if isinstance(fpath_or_root, str):
            event = etree.parse(fpath_or_root)
            root = event.getroot()
        elif etree.iselement(fpath_or_root):
            root = fpath_or_root
        else:
            raise ValueError("Argument `fpath_or_root` is neither a string or etree.Element")

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
            trigger_type = str.upper(trigger_type)

        # Use the trigger type to get the proper VOEvent class and parse the XML content.
        trigger = None
        try:
            for VOEventSubclass in VOEvent.__subclasses__():  # go through each VOEvent subclasses
                notice_types_upper = [str.upper(n) for n in
                                      VOEventSubclass.NOTICE_TYPES.values()]  # all possible trigger type name
                if trigger_type in notice_types_upper:  # check trigger type name to all possible ones
                    trigger = VOEventSubclass(root, trigger_type=trigger_type, ignore_test=ignore_test)
                    break
        except VOEvent.TestError:
            log.warning("Quitting...\n")

        return trigger

    def check_test(self):
        if self.ignore_test and self.role == 'test':
            message = f'This is a {self.type} test trigger.'
            log.info(message)
            raise VOEvent.TestError(message)

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
            position2d = self.wherewhen.find('.//Position2D')  # May be missing
            ra = position2d.find('.//Value2/C1').text
            dec = position2d.find('.//Value2/C2').text
            error = position2d.find('./Error2Radius').text
            return ra, dec, error
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

    def __init__(self, root, **kwargs):
        super().__init__(root, **kwargs)

    def check_test(self):
        if self.ignore_test and self.role == 'test':
            message = 'This is a GW O3 test trigger.'
            log.info(message)
            raise VOEvent.TestError(message)

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
        number = grace_id 
        sequence = self.what.find("./Param[@name='Pkt_Ser_Num']").get('value')
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
        print('This is a AMON trigger.')
        try:
            number = self.what.find("./Param[@name='run_id']").get('value')
            sequence = self.what.find("./Param[@name='event_id']").get('value')
            return number, sequence
        except AttributeError:
            return None, None

class MAXI(VOEvent):
    INSTRUMENT = 'MAXI'
    NOTICE_TYPES = VOEvent.get_notice_types(INSTRUMENT)

    def __init__(self, root, **kwargs):
        super().__init__(root, **kwargs)

    def get_trigger_id(self):
        try:
            number = self.what.find("./Param[@name='TrigID']").get('value')
            sequence = self.what.find("./Param[@name='Pkt_Ser_Num']").get('value')
            return number, sequence
        except AttributeError:
            return (None, None)


TRIGGERS = [
    LVC,
    Fermi,
    AMON,
    MAXI,
    VOEvent
]


def parse(root, ignore_test=True):
    """
    Parses a VOEvent XML object (lxml.etree.Element) extracting relevant data as described by VOEvent#get_data.

    Parameters
    ----------
    root: lxml.etree.Element
        VOEvent XML object
    ignore_test: bool
        If True and VOEvent has role='test', return None.
        A message may be logged specified by each VOEvent#__init__.

    Returns
    -------
    data: dict or None
        For the sake of data integrity the value of the data dictionary are strings read directly from the VOEvent XML.
        Intepretation of data type is left to the user.
    """
    # Check trigger number and trigger sequence
    trigger = VOEvent.parse_from_xml(root, ignore_test=ignore_test)

    if trigger is None:
        log.warning("Couldn't parse trigger number or trigger sequence from this trigger. Quitting...\n")
        return None
    if None in [trigger.number, trigger.sequence]:
        log.warning("Couldn't parse trigger number or trigger sequence from this trigger.\n"
                    + f"These information were parsed at best:\n{trigger.get_data()}\nQuitting...\n")
        return None

    return trigger.get_data()
