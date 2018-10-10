import healpy as hp  # UPDATED VERSION
import numpy as np
from scipy.stats import norm
import os

from astropy.coordinates import SkyCoord  # High-level coordinates
from astropy.coordinates import ICRS, Galactic, FK4, FK5  # Low-level frames
from astropy.coordinates import Angle, Latitude, Longitude  # Angles
import astropy.units as u
from astropy.table import Table,Column
import cosmolopy.magnitudes as mag

glade_RA_DEC_Dis_Bmag_ID='/media/data12/voevent/glade/glade_RA_DEC_Dis_Bmag_ID.npy'

##This nisde is the same size as the one from GW skymap, with pixel of 12582912
#nside = 1024
def make_skymap_from_radec(ra,dec,error,nside=1024) :
    totalnpixnumber=hp.nside2npix(nside)
    #probability pixels
    ppix=np.arange(totalnpixnumber)
    ramap,decmap=hp.pix2ang(nside,ppix,lonlat=True)
    cpix = SkyCoord(Longitude(ramap,unit=u.deg), Latitude(decmap,unit=u.deg), frame='icrs')
    ccentre=SkyCoord(ra, dec, unit="deg")
    #find the distance to the centre (in degree)
    dis=cpix.separation(ccentre)
    ##do a step funtion to assign the probability, to start, do a four step function
    ##1sigma=68.26%, 2sigma=95.46%, 3sigma=99.73%
    ##this is done according to pixle number
    ind1sigma=np.where(dis.value <= 1*error)
    ind2sigma=np.where(dis.value <= 2*error)
    ind3sigma=np.where(dis.value <= 3*error)
    ##the pixel number is pure, exclude the inside ones
    npix1sigma=len(ind1sigma[0])
    npix2sigma=len(ind2sigma[0])-npix1sigma
    npix3sigma=len(ind3sigma[0])-npix1sigma-npix2sigma
    pp1sigma=0.6826/npix1sigma
    pp2sigma=(0.9546-0.6826)/npix2sigma
    pp3sigma=(0.9973-0.9546)/npix3sigma
    ##Note, the order below can not be changed
    #probability of position
    pp=np.full(totalnpixnumber,(1.0-0.9973)/(totalnpixnumber-pp3sigma))
    #pp=np.zero(totalnpixnumber)
    pp[ind3sigma]=pp3sigma
    pp[ind2sigma]=pp2sigma
    pp[ind1sigma]=pp1sigma
    #to see the map if like
    #hp.mollview(m, title="Mollview image RING",norm='log')
    return pp

def cal_distance_p_from_powerlaw(distance,peakredshift=0.1,powerlawindex=-0.3) :

    from astropy.cosmology import WMAP9 as cosmo
    peakd=cosmo.luminosity_distance(peakredshift).value  ##returned value is in Mpc
    pdis=np.abs(peakd-distance)**powerlawindex
    return pdis

def select_gladegalaxy_accordingto_location_radecpeakz(ra,dec,error,peakz,credzone=0.99,nsigmas_in_d=3.0) :

    prob=make_skymap_from_radec(ra,dec,error)

    print('Applying <',credzone,' pos prob cut and ',nsigmas_in_d,' sigma distance cut!')
    ####star here, it's the same for other triggers###
    # loading the galaxy catalog. this updated glade catalog including RA, DEC, distance, Bmag and ID
    galax = np.load(glade_RA_DEC_Dis_Bmag_ID)

    # map parameters:
    npix = len(prob)
    nside = hp.npix2nside(npix)

    # galaxy parameters(RA, DEC to theta, phi):
    galax = (galax[np.where(galax[:, 2] > 0), :])[0]  # filter out negative distance

    theta = 0.5 * np.pi - np.pi * (galax[:, 1]) / 180
    phi = np.deg2rad(galax[:, 0])
    d = np.array(galax[:, 2])

    # converting galaxy coordinates to map pixels:
    ipix = hp.ang2pix(nside, theta, phi)

    # finding given percent probability zone(default is 99%):
    probcutoff = 1
    probsum = 0
    npix99 = 0
    sortedprob = np.sort(prob)
    while probsum < credzone:
        probsum = probsum + sortedprob[-1]
        probcutoff = sortedprob[-1]
        sortedprob = sortedprob[:-1]
        npix99 = npix99 + 1
    area = npix99 * hp.nside2pixarea(nside, degrees=True)
    ####end here, it's the same for other triggers###
    ####################################################
    ####it's different below because it need to do distance cut

    # calculating probability for galaxies by the localization map:
    ppos = prob[ipix]
    distp = cal_distance_p_from_powerlaw(galax[:,2],peakredshift=peakz)
    cutp=np.median(distp)*nsigmas_in_d*0.3
    print('cutp is :',cutp)

    # cuttoffs- 99% of probability by angles and 3sigma by distance:
    inddistance = np.where(distp >= cutp)
    indcredzone = np.where(ppos >= probcutoff)
    print(len(indcredzone[0]),' was selected according to location')
    print(len(inddistance[0]),' was selected according to distance')

    ##at this step, we'll always do masscut
    #doMassCuttoff = True

    # if no galaxies
    if (galax[np.intersect1d(indcredzone, inddistance)]).size == 0:
        while probsum < 0.99995:
            if sortedprob.size == 0:
                break
            probsum = probsum + sortedprob[-1]
            probcutoff = sortedprob[-1]
            sortedprob = sortedprob[:-1]
            npix99 = npix99 + 1
        print('No galaxy select with default cut, prob<0.99, dis < 3 sigma')
        print('Loosing the pos prob cut to 0.99995')
        print('and loosing the dis prob cut to 5 sigma')
        cutp=np.median(distp)*5.0*0.3
        inddistance = np.where(distp >= cutp)
        indcredzone = np.where(ppos >= probcutoff)
        ##at this step, we'll always do masscut
        #doMassCuttoff = False

    indselectedgala=np.intersect1d(indcredzone, inddistance)
    ipix = ipix[indselectedgala]
    ppos = ppos[indselectedgala]
    distp = distp[indselectedgala]
    Sloc = ppos * distp
    Sloc = Sloc / np.sum(Sloc)

    galax = galax[indselectedgala]
    if galax.size == 0:
        # print "no galaxies in field"
        # print "99.995% of probability is ", npix99*hp.nside2pixarea(nside, degrees=True), "deg^2"
        # print "peaking at [RA,DEC](deg) = ", maxprobcoord
        print('No galaxy was selected')
        return

    ##great, we have galaxy selected, need to return them as astropy.table format, add the score information
    galaxytable=Table(galax,names=('raDeg', 'decDeg', 'disMpc','Bmag','gladeID'),dtype=('f', 'f', 'f','f','i'))
    print(len(galaxytable),' galaxies are selected!')
    ##add distance to center too
    dis=(SkyCoord(Longitude(galaxytable['raDeg'],unit=u.deg), Latitude(galaxytable['decDeg'],unit=u.deg), frame='icrs').separation(SkyCoord(ra, dec, unit="deg"))).value*60 ##degree to arcmin
    galaxytable.add_column(Column(dis,name='DisToCentre_Arcmin'))
    galaxytable.add_column(Column(Sloc,name='S_total'))
    galaxytable.add_column(Column(ppos,name='P_pos'))
    galaxytable.add_column(Column(distp,name='P_dis'))
    galaxytable.add_column(Column(Sloc,name='S_loc'))
    indextmp=np.argsort(galaxytable['S_total'])[::-1]
    galaxytable=galaxytable[indextmp]
    return galaxytable

def select_gladegalaxy_accordingto_location_gw(gwskymap,credzone=0.99,nsigmas_in_d=3.0) :
    try:
        skymap = hp.read_map(gwskymap, field=None, verbose=False)
    except Exception as e:
        print("Failed to read sky map file",gwskymap)
        return
    ##the skymap file from gw has both the location information and also the distance information
    if (isinstance(skymap, np.ndarray) or isinstance(skymap, tuple)) and len(skymap) == 4:
        prob, distmu, distsigma, distnorm = skymap
        # print('Yes distance information available. Can produce galaxy list.')
    else:
        print('No distance information available. Cannot produce galaxy list. Check!')
        return

    print('Applying <',credzone,' pos prob cut and ',nsigmas_in_d,' sigma distance cut!')
    ####star here, it's the same for other triggers###
    # loading the galaxy catalog. this updated glade catalog including RA, DEC, distance, Bmag and ID
    galax = np.load(glade_RA_DEC_Dis_Bmag_ID)

    # map parameters:
    npix = len(prob)
    nside = hp.npix2nside(npix)

    # galaxy parameters(RA, DEC to theta, phi):
    galax = (galax[np.where(galax[:, 2] > 0), :])[0]  # filter out negative distance

    theta = 0.5 * np.pi - np.pi * (galax[:, 1]) / 180
    phi = np.deg2rad(galax[:, 0])
    d = np.array(galax[:, 2])

    # converting galaxy coordinates to map pixels:
    ipix = hp.ang2pix(nside, theta, phi)

    # finding given percent probability zone(default is 99%):
    probcutoff = 1
    probsum = 0
    npix99 = 0
    sortedprob = np.sort(prob)
    while probsum < credzone:
        probsum = probsum + sortedprob[-1]
        probcutoff = sortedprob[-1]
        sortedprob = sortedprob[:-1]
        npix99 = npix99 + 1
    area = npix99 * hp.nside2pixarea(nside, degrees=True)
    ####end here, it's the same for other triggers###
    ####################################################
    ####it's different below because it need to do distance cut

    # calculating probability for galaxies by the localization map:
    ppos = prob[ipix]
    distp = (norm(distmu[ipix], distsigma[ipix]).pdf(d) * distnorm[ipix]) 
      # * d**2)#/(norm(distmu[ipix], distsigma[ipix]).pdf(distmu[ipix]) * distnorm[ipix] * distmu[ipix]**2)

    # cuttoffs- 99% of probability by angles and 3sigma by distance:
    inddistance = np.where(np.abs(d - distmu[ipix]) < nsigmas_in_d * distsigma[ipix])
    indcredzone = np.where(ppos >= probcutoff)
    print(len(indcredzone[0]),' was selected according to location')
    print(len(inddistance[0]),' was selected according to distance')

    ##at this step, we'll always do masscut
    #doMassCuttoff = True

    # if no galaxies
    if (galax[np.intersect1d(indcredzone, inddistance)]).size == 0:
        while probsum < 0.99995:
            if sortedprob.size == 0:
                break
            probsum = probsum + sortedprob[-1]
            probcutoff = sortedprob[-1]
            sortedprob = sortedprob[:-1]
            npix99 = npix99 + 1
        print('No galaxy select with default cut, prob<0.99, dis < 3 sigma')
        print('Loosing the pos prob cut to 0.99995')
        print('and loosing the dis prob cut to 5 sigma')
        inddistance = np.where(np.abs(d - distmu[ipix]) < 5 * distsigma[ipix])
        indcredzone = np.where(ppos >= probcutoff)
        ##at this step, we'll always do masscut
        #doMassCuttoff = False

    indselectedgala=np.intersect1d(indcredzone, inddistance)
    ipix = ipix[indselectedgala]
    ppos = ppos[indselectedgala]
    distp = distp[indselectedgala]
    Sloc = ppos * distp
    Sloc = Sloc / np.sum(Sloc)

    galax = galax[indselectedgala]
    if galax.size == 0:
        # print "no galaxies in field"
        # print "99.995% of probability is ", npix99*hp.nside2pixarea(nside, degrees=True), "deg^2"
        # print "peaking at [RA,DEC](deg) = ", maxprobcoord
        return

    ##great, we have galaxy selected, need to return them as astropy.table format, add the score information
    galaxytable=Table(galax,names=('raDeg', 'decDeg', 'disMpc','Bmag','gladeID'),dtype=('f', 'f', 'f','f','i'))
    print(len(galaxytable),' galaxies are selected!')
    ##add distance to center too
    peakpid=np.argsort(prob)[-1]
    racent,deccent = hp.pix2ang(nside, peakpid,lonlat=True) ##must give lonlat=True keywork to make result degree
    dis=(SkyCoord(Longitude(galaxytable['raDeg'],unit=u.deg), Latitude(galaxytable['decDeg'],unit=u.deg), frame='icrs').separation(SkyCoord(racent, deccent, unit="deg"))).value*60 ##degree to arcmin
    galaxytable.add_column(Column(dis,name='DisToCentre_Arcmin'))
    galaxytable.add_column(Column(Sloc,name='S_total'))
    galaxytable.add_column(Column(ppos,name='P_pos'))
    galaxytable.add_column(Column(distp,name='P_dis'))
    galaxytable.add_column(Column(Sloc,name='S_loc'))
    indextmp=np.argsort(galaxytable['S_total'])[::-1]
    galaxytable=galaxytable[indextmp]
    return galaxytable

def select_gladegalaxy_accordingto_luminosity(galaxytable, doMassCuttoff=True, completeness=0.5, minGalaxies=100) :


    ##if galaxy number less than 500, don't do mass cut
    if len(galaxytable) < 500 :
        doMassCuttoff = False

    # schecter function parameters:
    alpha = -1.07
    MB_star = -20.7  # random slide from https://www.astro.umd.edu/~richard/ASTRO620/LumFunction-pp.pdf but not really...?

    from scipy.special import gammaincc
    from scipy.special import gammaincinv
    # normalized luminosity to account for mass:
    luminosity = mag.L_nu_from_magAB(galaxytable['Bmag'] - 5 * np.log10(galaxytable['disMpc'] * (10 ** 5)))
    Slum = luminosity / np.sum(luminosity)
    galaxytable.add_column(Column(Slum,name='S_lum'))

    # taking 50% of mass (missingpiece is the area under the schecter function between l=inf and the brightest galaxy in the field.
    # if the brightest galaxy in the field is fainter than the schecter function cutoff- no cutoff is made.
    # while the number of galaxies in the field is smaller than minGalaxies- we allow for fainter galaxies, until we take all of them.

    # no galaxies brighter than this in the field- so don't count that part of the Schechter function
    missingpiece = gammaincc(alpha + 2, 10 ** (-(min(galaxytable['Bmag'] - 5 * np.log10(galaxytable['disMpc'] * (
            10 ** 5))) - MB_star) / 2.5))

    while doMassCuttoff:
        MB_max = MB_star + 2.5 * np.log10(gammaincinv(alpha + 2, completeness + missingpiece))

        if (min(galaxytable['Bmag'] - 5 * np.log10(galaxytable['disMpc'] * (10 ** 5))) - MB_star) > 0:
        # if the brightest galaxy in the field is fainter then cutoff brightness- don't cut by brightness
            MB_max = 100

        brightest = np.where(galaxytable['Bmag'] - 5 * np.log10(galaxytable['disMpc'] * (10 ** 5)) < MB_max)
        print('MB_max: ',MB_max)
        if len(brightest[0]) < minGalaxies:
            if completeness >= 0.9:  # tried hard enough. just take all of them
                completeness = 1  # just to be consistent.
                doMassCuttoff = False
            else:
                completeness = (completeness + (1. - completeness) / 2)
        else:  # got enough galaxies
            galaxytable = galaxytable[brightest]
            doMassCuttoff = False

    print(len(galaxytable),' galaxies are selected!')
    ##great, we can now return the new result, need redo the normalization if any galaxy was cut
    galaxytable['S_lum']=galaxytable['S_lum']/np.sum(galaxytable['S_lum'])
    galaxytable['S_total']=(galaxytable['S_total']*galaxytable['S_lum'])/np.sum(galaxytable['S_total']*galaxytable['S_lum'])
    indextmp=np.argsort(galaxytable['S_total'])[::-1]
    galaxytable=galaxytable[indextmp]
    return galaxytable

def select_gladegalaxy_accordingto_detectionlimit(galaxytable, sensitivity=22, minmag=-12., maxmag=-17., mindistFactor=0.01) :

    minL = mag.f_nu_from_magAB(minmag)
    maxL = mag.f_nu_from_magAB(maxmag)

    # accounting for distance
    absolute_sensitivity = sensitivity - 5 * np.log10(galaxytable['disMpc'] * (10 ** 5))

    absolute_sensitivity_lum = mag.f_nu_from_magAB(absolute_sensitivity)
    distanceFactor = np.zeros(len(galaxytable))

    distanceFactor[:] = ((maxL - absolute_sensitivity_lum) / (maxL - minL))
    distanceFactor[mindistFactor > (maxL - absolute_sensitivity_lum) / (maxL - minL)] = mindistFactor
    distanceFactor[absolute_sensitivity_lum < minL] = 1
    distanceFactor[absolute_sensitivity > maxL] = mindistFactor
    distanceFactor=distanceFactor/np.sum(distanceFactor)
    galaxytable.add_column(Column(distanceFactor,name='S_det'))

    ##ii = np.argsort(p * luminosity_score * distanceFactor)[::-1]

    ### counting galaxies that constitute 50% of the probability(~0.5*0.98)
    ##sum = 0
    ##galaxies50per = 0
    ##observable50per = 0  # how many of the galaxies in the top 50% of probability are observable.
    ##sum_seen = 0
    ##enough = True
    ##while sum < 0.5:
    ##    if galaxies50per >= len(ii):
    ##        enough = False
    ##        break
    ##    sum = sum + (p[ii[galaxies50per]] * luminosity_score[ii[galaxies50per]]) / float(normalization)
    ##    sum_seen = sum_seen + (p[ii[galaxies50per]] * luminosity_score[ii[galaxies50per]] * distanceFactor[
    ##        ii[galaxies50per]]) / float(normalization)
    ##    galaxies50per = galaxies50per + 1

    ### event stats:
    ###
    ### Ngalaxies_50percent = number of galaxies consisting 50% of probability (including luminosity but not distance factor)
    ### actual_percentage = usually arround 50
    ### seen_percentage = if we include the distance factor- how much are the same galaxies worth
    ### 99percent_area = area of map in [deg^2] consisting 99% (using only the map from LIGO)
    ##stats = {"Ngalaxies_50percent": galaxies50per, "actual_percentage": sum * 100, "seen_percentage": sum_seen,
    ##         "99percent_area": area}


    print(len(galaxytable),' galaxies are selected!')
    ##great, we can now return the new result, need redo the normalization if any galaxy was cut
    galaxytable['S_total']=(galaxytable['S_total']*galaxytable['S_det'])/np.sum(galaxytable['S_total']*galaxytable['S_det'])
    indextmp=np.argsort(galaxytable['S_total'])[::-1]
    galaxytable=galaxytable[indextmp]
    return galaxytable

def gen_kait_rqs_from_table(galaxytable,outputhourbase=24,outputrqsbase=0, eachrqsnumber=30, outputdir='./', runcommand=True) :

    head="""TELESCOP = 'Thirty inch'                                                        
OBSERVER = 'SN'                                                                 
PROCEDUR = 'sn3'                                                                
SENDMAIL = F                                                                    
INTERVAL = 3                                                                    
CATFILE  = 'weidong.cat'                                                        
PRIORITY =  2.0                                                                 
GUIDEMOD = 'noguide'                                                            
FILTERS  = 'clear'                                                              
EXPTIME  =  20.0                                                                
OBSTIME  =   10                                                                 
GAIN     = 4                                                                    
MOONDIST = 20.0                                                                 
MOONWIDTH= 5.0                                                                  
WESTLIM  = 45.0                                                                 
EASTLIM  = -45.0"""
    
    #print(head)
    ##first need to drop the targets too south, KAIT limit is -34.3
    print(len(galaxytable)," galaxies input")
    galaxytable=galaxytable[np.where(galaxytable['decDeg'] > -34.2)]
    print(len(galaxytable)," galaxies selected after cut of dec > -34.2")
    ##first calculate the mean Hour from the table
    hour="{:0>2d}".format(outputhourbase+int(np.mean(galaxytable['raDeg']/15.0)))
    targetnumber=len(galaxytable)
    lefttargetnumber=targetnumber
    group=0
    scpcommand="scp obscommand "
    obscommand=""
    ##max group is 50
    while lefttargetnumber > 0 and group < 50 :
        grouprqs=str("NA"+hour+"_"+"{:0>2d}".format(group+outputrqsbase))
        outfile=grouprqs+'.rqs'
        print(grouprqs)
        firstline="REQID    = '"+grouprqs+"'\n"
        #print(head)
        startind=group*eachrqsnumber
        strtmp='\n'
        for i in range(eachrqsnumber) :
            if startind+i >= targetnumber :
                #print('now break')
                break
            coord=SkyCoord(galaxytable['raDeg'][startind+i], galaxytable['decDeg'][startind+i], unit="deg")
            radecstr=coord.to_string('hmsdms',sep=':').split()
            rastr=radecstr[0]
            decstr=radecstr[1]
            objectid="G{:0>7d}".format(galaxytable['gladeID'][startind+i])
            strtmp=strtmp+"RA       = '"+rastr+"'\n"
            strtmp=strtmp+"DEC      = '"+decstr+"'\n"
            strtmp=strtmp+"EPOCH    = 2000.0\n"
            strtmp=strtmp+"OBJECT   = '"+objectid+"'\n"
            strtmp=strtmp+"MAG      = 12.30\n"
            strtmp=strtmp+"END\n"
            #print(strtmp)
        with open(os.path.join(outputdir, outfile), 'w') as f:
            f.write(firstline+head+strtmp)
        group=group+1
        lefttargetnumber=lefttargetnumber-eachrqsnumber
        scpcommand=scpcommand+" "+outfile
        obscommand=obscommand+"tin manual "+outfile+" ; sleep 120; "
    ##write the obscommand file first before scp command, need to scp this file
    obscommand="#!/bin/sh\n"+obscommand
    print(obscommand)
    outfile='obscommand'
    with open(os.path.join(outputdir, outfile), 'w') as f:
        f.write(obscommand)
    command="chmod a+x "+outputdir+outfile
    print(command)
    os.system(command)

    scpcommand=scpcommand+" kait@ttauri.ucolick.org:/home/kait/targets/"
    print(scpcommand)
    outfile='scpcommand'
    with open(os.path.join(outputdir, outfile), 'w') as f:
        f.write(scpcommand)
    ##need to change dir to outputdir to run the scpcommand
    os.chdir(outputdir)
    os.system(scpcommand)

    if runcommand :
        command="ssh kait@ttauri.ucolick.org /home/kait/targets/obscommand"
        print(command)
        os.system(command)
