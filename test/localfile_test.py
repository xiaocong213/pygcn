import sys
import pprint
from lxml import etree
from pathlib import Path
from astrosql import AstroSQL

PROJECT_PATH = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_PATH))
from gcn.handlers import followupkait
from gcn import voeventparser

pprint = pprint.PrettyPrinter().pprint
DB = AstroSQL(database='observation')
voevents_table = DB.get_table('voevents')

DATAPATH = PROJECT_PATH / 'test/gcn_output'
fname = "ivo%3A%2F%2Fnasa.gsfc.gcn%2FFermi%23GBM_Gnd_Pos_2018-04-16T08%3A09%3A26.47_545558971_1-990"
event = etree.parse(str(DATAPATH / fname))
root = event.getroot()
pprint(voeventparser.parse(root))
# trigger_number = root.find("./What/Param[@name='TrigID']").attrib['value']
# voevents_table.delete().where(voevents_table.TriggerNumber == trigger_number).execute()
# followupkait(str(DATAPATH/fname), root)
