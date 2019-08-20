import numpy as np
import argparse
import os
import pandas as pd


from astropy.coordinates import SkyCoord  # High-level coordinates
from astropy.coordinates import ICRS, Galactic, FK4, FK5  # Low-level frames
from astropy.coordinates import Angle, Latitude, Longitude  # Angles
import astropy.units as u
from astropy.table import Table,Column

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('ID')
    parser.add_argument('-l', '--list', action='store_true', help="this is a list")
    args = parser.parse_args()

    if args.list :
        ids = pd.read_csv(args.ID, delim_whitespace = True, names = ['id'])
    else :
        ids=int(args.ID)
    #print(ids)

    glade_RA_DEC_Dis_Bmag_ID='/media/data12/voevent/glade/glade_RA_DEC_Dis_Bmag_ID.npy'
    galaxytable = np.load(glade_RA_DEC_Dis_Bmag_ID)
    for i in range(len(ids)) :
        eachid=ids['id'][i]-1
        coord=SkyCoord(galaxytable[eachid][0], galaxytable[eachid][1], unit="deg")
        radecstr=coord.to_string('hmsdms',sep=':').split()
        rastr=radecstr[0]
        decstr=radecstr[1]
        print(ids['id'][i],rastr,decstr,galaxytable[eachid][0], galaxytable[eachid][1])
