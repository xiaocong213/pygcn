import sys
from lxml import etree
from pathlib import Path
PROJECT_PATH = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_PATH))

from voevent import voeventparser

DATAPATH = PROJECT_PATH / 'test/gcn_output'
fname = "ivo%3A%2F%2Fnasa.gsfc.gcn%2FFermi%23GBM_Gnd_Pos_2018-04-16T08%3A09%3A26.47_545558971_1-990"
event = etree.parse(str(DATAPATH / fname))
root = event.getroot()
print(voeventparser.parse(root))
