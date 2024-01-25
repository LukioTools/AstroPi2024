#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pyIGRF: code to synthesise magnetic field values from the 13th generation of the
        International Geomagnetic Reference Field (IGRF), released in December 2019

 @author: Ciaran Beggan (British Geological Survey)
 
 See https://www.ngdc.noaa.gov/IAGA/vmod/ for information on the IGRF
 
 Based on existing codes: igrf13.f (FORTRAN) and chaosmagpy (Python3)
 
 With acknowledgements to: Clemens Kloss (DTU Space), David Kerridge (BGS),
      william Brown and Grace Cox.
 
     This is a program for synthesising geomagnetic field values from the 
     International Geomagnetic Reference Field series of models as agreed
     in December 2019 by IAGA Working Group V-MOD. 
     
     This is the 13th generation IGRF.
     
     The main-field models for 1900.0, 1905.0,..1940.0 and 2020.0 are 
     non-definitive, those for 1945.0, 1950.0,...2015.0 are definitive and
     the secular-variation model for 2020.0 to 2025.0 is non-definitive.

     Main-field models are to degree and order 10 (i.e. 120 coefficients)
     for 1900.0-1995.0 and to 13 (i.e. 195 coefficients) for 2000.0 onwards. 
     The predictive secular-variation model is to degree and order 8 (i.e. 80
     coefficients).

 Inputs:
 -------
     Inputs are via the command line:    
     
     Options include: 
         Write to (1) screen or (2) filename          
    
    Type of computation:
         (1) values at a single locations at one time (spot value)
         (2) values at same location at one year intervals (time series), 
         (3) grid of values at one time (grid); 
     
        Positions can be in:  
         (1) geodetic (WGS-84)
         (2) geocentric coordinates
         
     Latitude & longitude entered as: 
         (1) decimal degrees or 
         (2) degrees & minutes (not in grid)
    
     Altitude can be entered as:
         (1) Geodetic: height above the ellipsoid in km
         (2) Geocentric: distance from the Earth's centre in km
        
     Date: in decimal years (e.g. 2020.25)
 
 Outputs: 
 -----------
      : main field (in nanoTesla) and secular variation (in nanoTesla/year)
 
 
 Dependencies: 
 -------------
     : numpy, scipy
 
 Recent history of code:
 -----------------------
     Initial release: April 2020 (Ciaran Beggan, BGS)
 
 !!! This code has been rewrited and edited for generic usage !!!
"""
from scipy import interpolate
from MagneticField import igrf_utils as iut
import Math as m

# Load in the file of coefficients
IGRF_FILE = r'./MagneticField/IGRF13.shc'
igrf = iut.load_shcfile(IGRF_FILE, None)

class InputData:
    date = 2024
    alt = 7000
    lat = 0
    colat = 0
    lon = 0
    itype = 2
    sd = 0
    cd = 0

    def __init__(self, date, alt, lat, colat, lon, itype, sd, cd):
        self.date = date
        self.alt = alt
        self. lat = lat
        self. colat = colat
        self.lon = lon
        self.itype = itype
        self.sd = sd
        self.cd = cd



class MagneticField:

    #can be direcly passed into getMagneticFieldVector
    def GetData(latidue, longitude, altitude, date):
        itype = 2

        latd = iut.check_float(latidue)
        lond = iut.check_float(longitude)

        lat, lon = iut.check_lat_lon_bounds(latd, 0, lond, 0)
        colat = 90 - lat

        alt = iut.check_float(altitude)
        sd = 0;
        cd = 0
        return  InputData(date, alt, lat, colat, lon, itype, sd, cd)

    def GetMagneticFieldVector(input):

        # Interpolate the geomagnetic coefficients to the desired date(s)
        # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
        f = interpolate.interp1d(igrf.time, igrf.coeffs, fill_value='extrapolate')
        coeffs = f(input.date)

        # Compute the main field B_r, B_theta and B_phi value for the location(s)
        Br, Bt, Bp = iut.synth_values(coeffs.T, input.alt, input.colat, input.lon,
                                      igrf.parameters['nmax'])
        # For the SV, find the 5 year period in which the date lies and compute
        # the SV within that period. IGRF has constant SV between each 5 year period
        # We don't need to subtract 1900 but it makes it clearer:
        epoch = (input.date - 1900) // 5
        epoch_start = epoch * 5
        # Add 1900 back on plus 1 year to account for SV in nT per year (nT/yr):
        coeffs_sv = f(1900 + epoch_start + 1) - f(1900 + epoch_start)
        Brs, Bts, Bps = iut.synth_values(coeffs_sv.T, input.alt, input.colat, input.lon,
                                         igrf.parameters['nmax'])

        # Use the main field coefficients from the start of each five epoch
        # to compute the SV for Dec, Inc, Hor and Total Field (F)
        # [Note: these are non-linear components of X, Y and Z so treat separately]
        coeffsm = f(1900 + epoch_start);
        Brm, Btm, Bpm = iut.synth_values(coeffsm.T, input.alt, input.colat, input.lon,
                                         igrf.parameters['nmax'])

        # Rearrange to X, Y, Z components
        X = -Bt;
        Y = Bp;
        Z = -Br
        # For the SV
        dX = -Bts;
        dY = Bps;
        dZ = -Brs
        Xm = -Btm;
        Ym = Bpm;
        Zm = -Brm

        # Compute the four non-linear components
        dec, hoz, inc, eff = iut.xyz2dhif(X, Y, Z)
        # The IGRF SV coefficients are relative to the main field components
        # at the start of each five year epoch e.g. 2010, 2015, 2020
        decs, hozs, incs, effs = iut.xyz2dhif_sv(Xm, Ym, Zm, dX, dY, dZ)

        return m.Vector(X,Y,Z)