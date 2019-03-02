import sys
import pprint
from lxml import etree
from pathlib import Path
from astrosql import AstroSQL

PROJECT_PATH = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_PATH))
from gcn.handlers import followupkait
from gcn import voeventparser

DATA_PATH = "/media/data12/voevent/archive/"
VOEVENT_FILENAME = "20190301/ivo%3A%2F%2Fnasa.gsfc.gcn%2FFermi%23GBM_Flt_Pos_2019-03-01T10%3A01%3A15.66_573127280_46-572"

if __name__ == '__main__':
    """
    >>> python parser_test.py voevents_file.xml
    """
    args = sys.argv[1:]
    if len(args) == 0:
        args.append(DATA_PATH + VOEVENT_FILENAME)
    pprint = pprint.PrettyPrinter().pprint
    results = []
    for fname in args:
        print(f"Parsing: {fname}")
        assert '/*' not in fname, f'{fname}: No such file or directory'
        event = etree.parse(fname)
        root = event.getroot()
        data = voeventparser.parse(root)
        results.append(data)
        if data is not None:
            pprint(results[-1])
            print()
