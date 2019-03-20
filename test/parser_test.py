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
import logging
import pprint
import sys
from pathlib import Path

from lxml import etree

PROJECT_PATH = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_PATH))
from gcn import voeventparser

DATA_PATH = "/media/data12/voevent/archive/"
VOEVENT_FILENAME = "20190304/ivo%3A%2F%2Fnasa.gsfc.gcn%2FFermi%23GBM_Gnd_Pos_2019-03-04T19%3A37%3A23.34_573421048_58-867"


def sanity(fpath):
    event = etree.parse(fpath)
    root = event.getroot()
    data = voeventparser.parse(root, ignore_test=False)

    print(data)
    assert data is not None, "Make sure 'ignore_test' is False."

    # Check data are strings
    assert all([isinstance(d, str) or (d is None) for d in data.values()]), "Data are not all strings; the parser should not assume data types."

    # Check valid keys
    keys = [
        'TriggerType', 'TriggerSequence', 'TriggerNumber',
        'RA', 'Dec', 'ErrorRadius',
        'Time', 'Comment'
    ]
    assert set(data.keys()) == set(keys)
    return data


def test_parse_lvc_trigger():
    fpath = str(Path(DATA_PATH) / '20190320/ivo%3A%2F%2Fgwnet%2FLVC%23MS190320a-1-Preliminary')
    data = sanity(fpath)
    assert data['TriggerNumber'] == 'MS190320a'
    assert data['TriggerSequence'] == '1'
    assert data['TriggerType'] == 'LVC_PRELIM'
    assert data['Time'] == "2019-03-20T00:36:20.057380"
    assert data['Comment'] == "https://gracedb.ligo.org/api/superevents/MS190320a/files/bayestar.fits.gz"
    return

def test_parse_fermi_trigger():
    fpath = str(Path(DATA_PATH) / '20190320/ivo%3A%2F%2Fnasa.gsfc.gcn%2FFermi%23GBM_Flt_Pos_2019-03-20T00%3A26%3A25.61_574734390_80-321')
    data = sanity(fpath)
    assert data['TriggerNumber'] == '574734390'
    assert data['TriggerSequence'] == '80'
    assert data['TriggerType'] == 'FERMI_GBM_FLT_POS'
    assert data['Time'] == "2019-03-20T00:26:25.61"
    assert data['Comment'] == None
    assert data['RA'] == '40.7833'
    assert data['Dec'] == '-34.5667'
    assert data['ErrorRadius'] == '50.0000'
    return

def test_parse_amon_trigger():
    fpath = str(Path(DATA_PATH) / '20190221/ivo%3A%2F%2Fnasa.gsfc.gcn%2FAMON%23ICECUBE_HESE_Event2019-02-21T08%3A25%3A39.71_132229_066688965-597')
    data = sanity(fpath)
    assert data['TriggerNumber'] == '132229'
    assert data['TriggerSequence'] == '66688965'
    assert data['TriggerType'] == 'AMON_ICECUBE_HESE'
    assert data['Time'] == "2019-02-21T08:25:39.71"
    assert data['Comment'] == None
    assert data['RA'] == '267.3650'
    assert data['Dec'] == '-16.9379'
    assert data['ErrorRadius'] == '1.2299'
    return

# if __name__ == '__main__':
#     """
#     >>> python parser_test.py voevents_file.xml
#     """
#     log = logging.getLogger(__name__)
#     logging.basicConfig(level=logging.INFO, format='%(message)s')
#     args = sys.argv[1:]
#     if len(args) == 0:
#         args.append(DATA_PATH + VOEVENT_FILENAME)
#     pprint = pprint.PrettyPrinter().pprint
#     results = []
#     for fname in args:
#         log.info(f"Parsing {fname}")
#         assert '/*' not in fname, f'{fname}: No such file or directory'
#         event = etree.parse(fname)
#         root = event.getroot()
#         data = voeventparser.parse(root)
#         results.append(data)
#         if data is not None:
#             pprint(results[-1])
#             print()
