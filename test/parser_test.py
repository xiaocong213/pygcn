import sys
import pprint
from lxml import etree
from pathlib import Path
from astrosql import AstroSQL

PROJECT_PATH = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_PATH))
from gcn.handlers import followupkait
from gcn import voeventparser

if __name__ == '__main__':
    args = sys.argv[1:]
    pprint = pprint.PrettyPrinter().pprint
    for fname in args:
        event = etree.parse(fname)
        root = event.getroot()
        pprint(voeventparser.parse(root))

