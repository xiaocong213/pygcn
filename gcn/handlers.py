# Copyright (C) 2014-2018  Leo Singer
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
"""
Payload handlers.
"""

#######################################
###Newly addded########################
import sys
import os
#######################################

import functools
import logging
from six.moves.urllib.parse import quote_plus

__all__ = ('get_notice_type', 'include_notice_types', 'exclude_notice_types',
           'archive', 'followupkait')


def get_notice_type(root):
    return int(root.find("./What/Param[@name='Packet_Type']").attrib['value'])


def include_notice_types(*notice_types):
    """Process only VOEvents whose integer GCN packet types are in
    `notice_types`. Should be used as a decorator, as in:

        import gcn.handlers
        import gcn.notice_types as n

        @gcn.handlers.include_notice_types(n.FERMI_GBM_GND_POS,
                                           n.FERMI_GBM_FIN_POS)
        def handle(payload, root):
            print('Got notice of type FERMI_GBM_GND_POS or FERMI_GBM_FIN_POS')
    """
    notice_types = frozenset(notice_types)

    def decorate(handler):
        @functools.wraps(handler)
        def handle(payload, root):
            if get_notice_type(root) in notice_types:
                handler(payload, root)
        return handle
    return decorate


def exclude_notice_types(*notice_types):
    """Process only VOEvents whose integer GCN packet types are not in
    `notice_types`. Should be used as a decorator, as in:

        import gcn.handlers
        import gcn.notice_types as n

        @gcn.handlers.exclude_notice_types(n.FERMI_GBM_GND_POS,
                                           n.FERMI_GBM_FIN_POS)
        def handle(payload, root):
            print('Got notice not of type FERMI_GBM_GND_POS '
                  'or FERMI_GBM_FIN_POS')
    """
    notice_types = frozenset(notice_types)

    def decorate(handler):
        @functools.wraps(handler)
        def handle(payload, root):
            if get_notice_type(root) not in notice_types:
                handler(payload, root)
        return handle
    return decorate

def archive(payload, root):
    """Payload handler that archives VOEvent messages as files in the current
    working directory. The filename is a URL-escaped version of the messages'
    IVORN."""
    ivorn = root.attrib['ivorn']
    filename = quote_plus(ivorn)
    with open(filename, 'wb') as f:
        f.write(payload)
    logging.getLogger('gcn.handlers.archive').info("archived %s", ivorn)

#######################################
###Newly addded########################
def followupkait(payload, root):
    """This is for KAIT follow up procedures"""
    ivorn = root.attrib['ivorn']

    ##first, do archive still, but seperate it into UT every day
    archive_path="/media/data12/voevent/archive/"
    from datetime import datetime
    savedir=archive_path+datetime.utcnow().strftime("%Y%m%d")+"/"
    if not os.path.exists(savedir) :
        os.makedirs(savedir)
        command="chgrp -R flipper "+savedir
        print(command)
        os.system(command)
        command="chmod 770 "+savedir
        print(command)
        os.system(command)
    filename = savedir+quote_plus(ivorn)
    with open(filename, 'wb') as f:
        f.write(payload)
    logging.getLogger('gcn.handlers.archive').info("archived %s", filename)

    ##send out email
    command="voeventalertemail "+filename
    os.system(command)

    ##Now here is the real processing
    import gcn.notice_types as n

    @gcn.handlers.include_notice_types(n.FERMI_GBM_GND_POS,
                                       n.FERMI_GBM_FLT_POS,
                                       n.FERMI_GBM_FIN_POS,
                                       n.SWIFT_BAT_GRB_POS_ACK,
                                       n.AGILE_GRB_WAKEUP,
                                       n.AGILE_GRB_GROUND,
                                       n.AGILE_GRB_REFINED,
                                       n.FERMI_LAT_POS_INI,
                                       n.FERMI_LAT_GND,
                                       n.MAXI_UNKNOWN,
                                       n.MAXI_TEST,
                                       n.LVC_PRELIM,
                                       n.LVC_INITIAL,
                                       n.LVC_UPDATE,
                                       n.LVC_TEST,
                                       n.LVC_CNTRPART,
                                       n.AMON_ICECUBE_COINC,
                                       n.AMON_ICECUBE_HESE,
                                       n.CALET_GBM_FLT_LC,
                                       n.CALET_GBM_GND_LC,
                                       n.LVC_SUPER_PRELIM,
                                       n.LVC_SUPER_INITIAL,
                                       n.LVC_SUPER_UPDATE,
                                       n.GWHEN_COINC,
                                       n.AMON_ICECUBE_EHE)
    def handle(payload, root):
        print('Got notice of type we want!')
