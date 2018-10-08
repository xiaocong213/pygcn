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
GCN Notice types, from <http://gcn.gsfc.nasa.gov/filtering.html>.
"""

_notice_types = dict(
    GRB_COORDS=1,
    TEST_COORDS=2,
    IM_ALIVE=3,
    KILL_SOCKET=4,
    MAXBC=11,
    BRAD_COORDS=21,
    GRB_FINAL=22,
    HUNTS_SRC=24,
    ALEXIS_SRC=25,
    XTE_PCA_ALERT=26,
    XTE_PCA_SRC=27,
    XTE_ASM_ALERT=28,
    XTE_ASM_SRC=29,
    COMPTEL_SRC=30,
    IPN_RAW=31,
    IPN_SEG=32,
    SAX_WFC_ALERT=33,
    SAX_WFC_SRC=34,
    SAX_NFI_ALERT=35,
    SAX_NFI_SRC=36,
    XTE_ASM_TRANS=37,
    spare38=38,
    IPN_POS=39,
    HETE_ALERT_SRC=40,
    HETE_UPDATE_SRC=41,
    HETE_FINAL_SRC=42,
    HETE_GNDANA_SRC=43,
    HETE_TEST=44,
    GRB_CNTRPART=45,
    SWIFT_TOO_FOM=46,
    SWIFT_TOO_SC_SLEW=47,
    DOW_TOD=48,
    spare50=50,
    INTEGRAL_POINTDIR=51,
    INTEGRAL_SPIACS=52,
    INTEGRAL_WAKEUP=53,
    INTEGRAL_REFINED=54,
    INTEGRAL_OFFLINE=55,
    INTEGRAL_WEAK=56,
    AAVSO=57,
    MILAGRO_POS=58,
    KONUS_LC=59,
    SWIFT_BAT_GRB_ALERT=60,
    SWIFT_BAT_GRB_POS_ACK=61,
    SWIFT_BAT_GRB_POS_NACK=62,
    SWIFT_BAT_GRB_LC=63,
    SWIFT_BAT_SCALEDMAP=64,
    SWIFT_FOM_OBS=65,
    SWIFT_SC_SLEW=66,
    SWIFT_XRT_POSITION=67,
    SWIFT_XRT_SPECTRUM=68,
    SWIFT_XRT_IMAGE=69,
    SWIFT_XRT_LC=70,
    SWIFT_XRT_CENTROID=71,
    SWIFT_UVOT_DBURST=72,
    SWIFT_UVOT_FCHART=73,
    SWIFT_BAT_GRB_LC_PROC=76,
    SWIFT_XRT_SPECTRUM_PROC=77,
    SWIFT_XRT_IMAGE_PROC=78,
    SWIFT_UVOT_DBURST_PROC=79,
    SWIFT_UVOT_FCHART_PROC=80,
    SWIFT_UVOT_POS=81,
    SWIFT_BAT_GRB_POS_TEST=82,
    SWIFT_POINTDIR=83,
    SWIFT_BAT_TRANS=84,
    SWIFT_XRT_THRESHPIX=85,
    SWIFT_XRT_THRESHPIX_PROC=86,
    SWIFT_XRT_SPER=87,
    SWIFT_XRT_SPER_PROC=88,
    SWIFT_UVOT_POS_NACK=89,
    SWIFT_BAT_ALARM_SHORT=90,
    SWIFT_BAT_ALARM_LONG=91,
    SWIFT_UVOT_EMERGENCY=92,
    SWIFT_XRT_EMERGENCY=93,
    SWIFT_FOM_PPT_ARG_ERR=94,
    SWIFT_FOM_SAFE_POINT=95,
    SWIFT_FOM_SLEW_ABORT=96,
    SWIFT_BAT_QL_POS=97,
    SWIFT_BAT_SUB_THRESHOLD=98,
    SWIFT_BAT_SLEW_POS=99,
    AGILE_GRB_WAKEUP=100,
    AGILE_GRB_GROUND=101,
    AGILE_GRB_REFINED=102,
    SWIFT_ACTUAL_POINTDIR=103,
    AGILE_POINTDIR=107,
    AGILE_TRANS=108,
    AGILE_GRB_POS_TEST=109,
    FERMI_GBM_ALERT=110,
    FERMI_GBM_FLT_POS=111,
    FERMI_GBM_GND_POS=112,
    FERMI_GBM_LC=113,
    FERMI_GBM_GND_INTERNAL=114,
    FERMI_GBM_FIN_POS=115,
    FERMI_GBM_ALERT_INTERNAL=116,
    FERMI_GBM_FLT_INTERNAL=117,
    FERMI_GBM_TRANS=118,
    FERMI_GBM_POS_TEST=119,
    FERMI_LAT_POS_INI=120,
    FERMI_LAT_POS_UPD=121,
    FERMI_LAT_POS_DIAG=122,
    FERMI_LAT_TRANS=123,
    FERMI_LAT_POS_TEST=124,
    FERMI_LAT_MONITOR=125,
    FERMI_SC_SLEW=126,
    FERMI_LAT_GND=127,
    FERMI_LAT_OFFLINE=128,
    FERMI_POINTDIR=129,
    SIMBADNED=130,
    FERMI_GBM_SUBTHRESH=131,
    SWIFT_BAT_MONITOR=133,
    MAXI_UNKNOWN=134,
    MAXI_KNOWN=135,
    MAXI_TEST=136,
    OGLE=137,
    CBAT=138,
    MOA=139,
    SWIFT_BAT_SUBSUB=140,
    SWIFT_BAT_KNOWN_SRC=141,
    VOE_11_IM_ALIVE=142,
    VOE_20_IM_ALIVE=143,
    FERMI_SC_SLEW_INTERNAL=144,
    COINCIDENCE=145,
    FERMI_GBM_FIN_INTERNAL=146,
    SUZAKU_LC=148,
    SNEWS=149,
    LVC_PRELIM=150,
    LVC_INITIAL=151,
    LVC_UPDATE=152,
    LVC_TEST=153,
    LVC_CNTRPART=154,
    AMON_ICECUBE_COINC=157,
    AMON_ICECUBE_HESE=158,
    CALET_GBM_FLT_LC=160,
    CALET_GBM_GND_LC=161,
	LVC_SUPER_PRELIM = 162,
	LVC_SUPER_INITIAL = 163,
	LVC_SUPER_UPDATE = 163,
	GWHEN_COINC = 169,
	AMON_ICECUBE_EHE = 169)

vars().update(**_notice_types)

try:
    # FIXME:
    # This module was added to the Python standard library in Python 3.4.
    from enum import IntEnum
except ImportError:
    __all__ = ()
else:
    NoticeType = IntEnum('NoticeType', _notice_types)
    del IntEnum
    __all__ = ('NoticeType',)

del _notice_types
