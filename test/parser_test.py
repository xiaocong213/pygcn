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
VOEVENT_FILENAME = "20190201/ivo%3A%2F%2Fnasa.gsfc.gcn%2FFermi%23LAT_Test_Pos_2019-02-01T02%3A02%3A19.00_099999_1-965"

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
        log.info(f"Parsing: {fname}")
        assert '/*' not in fname, f'{fname}: No such file or directory'
        event = etree.parse(fname)
        root = event.getroot()
        data = voeventparser.parse(root)
        results.append(data)
        if data is not None:
            pprint(results[-1])
            print()
