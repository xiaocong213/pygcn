"""
Tests the VOEvent Parser (`../gcn/voeventparser.py`) on some VOEvent XML file.

>>> python parser_test.py /path/to/voevents_file.xml
INFO:__main__:Parsing: /media/data12/voevent/archive/20190302/ivo%3A%2F%2Fgwnet%2FLVC%23MS190302a-1-Preliminary
{'Comment': 'https://gracedb.ligo.org/api/superevents/MS190302a/files/bayestar.fits.gz',
 'Dec': None,
 'ErrorRadius': None,
 'RA': None,
 'Time': '2019-03-02T00:40:06.805722',
 'TriggerNumber': '190302a',
 'TriggerSequence': '1',
 'TriggerType': None}
"""
import sys
import pprint
import logging
from lxml import etree
from pathlib import Path
from astrosql import AstroSQL

PROJECT_PATH = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_PATH))
from gcn.handlers import followupkait
from gcn import voeventparser

DATA_PATH = "/media/data12/voevent/archive/"
VOEVENT_FILENAME = "20190304/ivo%3A%2F%2Fnasa.gsfc.gcn%2FFermi%23GBM_Gnd_Pos_2019-03-04T19%3A37%3A23.34_573421048_58-867"

if __name__ == '__main__':
    """
    >>> python parser_test.py voevents_file.xml
    """
    log = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    args = sys.argv[1:]
    if len(args) == 0:
        args.append(DATA_PATH + VOEVENT_FILENAME)
    pprint = pprint.PrettyPrinter().pprint
    results = []
    for fname in args:
        log.info(f"Parsing {fname}")
        assert '/*' not in fname, f'{fname}: No such file or directory'
        event = etree.parse(fname)
        root = event.getroot()
        data = voeventparser.parse(root)
        results.append(data)
        if data is not None:
            pprint(results[-1])
            print()
