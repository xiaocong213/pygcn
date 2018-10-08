import sys
from lxml import etree
from pathlib import Path
PROJECT_PATH = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_PATH))

from voevent import voeventparser

DATAPATH = Path('gcn_output/')
fname = "ivo%253A%252F%252Fnasa.gsfc.gcn%252FFermi%2523GBM_Fin_Pos2018-04-16T08%253A09%253A26.47_545558971_0-394"
event = etree.parse(str(DATAPATH / fname))
root = event.getroot()
print(voeventparser.parse(root))
