#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 19 23:25:25 2024

@author: ericlevenson

description: GIS operations getting total lake fraction, size, density statistics for terrain classifications

Used to produce Tables S3 and S4
"""
import os
import numpy as np
import pandas as pd
import geopandas as gpd

lakes = gpd.read_file('/Users/ericlevenson/Dropbox (University of Oregon)/ArcticLakeScan/products/analysis/lakes3.shp')
perm = gpd.read_file('/Users/ericlevenson/Dropbox (University of Oregon)/ArcticLakeScan/GIS_layers/permafrost/permAK_geom.shp')
ancillary = gpd.read_file('/Users/ericlevenson/Dropbox (University of Oregon)/ArcticLakeScan/GIS_layers/permafrost/perm_glac_geo_union.shp')

ancillary.head()
akArea = 1506809293607.3547/1000000 # ak km2

## ***TABLE S4***

# get land areas per permafrost class
cont = perm.loc[perm['EXTENT'] == 'Cont']
discon = perm.loc[perm['EXTENT'] == 'Discon']
isol = perm.loc[perm['EXTENT'] == 'Isol']
spora = perm.loc[perm['EXTENT'] == 'Spora']

for i in [cont, discon, isol, spora]:
    print(i['area'].sum()/1000000)

contArea = 358345788580.29803/1000000
disconArea = 329258795157.564/1000000
isolArea = 194217980013.7188/1000000
sporaArea = 318253154739.3718/1000000
unfrzArea = akArea - contArea - disconArea - isolArea - sporaArea

# separate lake DFS for each permafrost class
cont = lakes.loc[lakes['EXTENT'] == 'Cont']
discon = lakes.loc[lakes['EXTENT'] == 'Discon']
isol = lakes.loc[lakes['EXTENT'] == 'Isol']
spora = lakes.loc[lakes['EXTENT'] == 'Spora']
unfrz = lakes.loc[lakes['EXTENT'] == 'unfrz']

# print mean lake size
for i in [cont, discon, spora, isol, unfrz]:
    print(i['areakm'].mean())
    
lakes['areakm'].mean() # total mean lake size



# ***Table S3***

ugc = lakes.loc[(lakes['glacial']=='Unglaciated') & (lakes['text2']=='Coarse')]
len(ugc)
for i in ['unfrz', 'Isol', 'Spora', 'Discon', 'Cont']:
    df = ugc.loc[ugc['EXTENT']==i]
    print(f"# lakes: {len(df)}, lake area: {df['areakm'].sum()}, mean lake size: {df['areakm'].mean()}")
ugc['areakm'].mean()

ugf = lakes.loc[(lakes['glacial']=='Unglaciated') & (lakes['text2']=='Fine')]
len(ugf)
for i in ['unfrz', 'Isol', 'Spora', 'Discon', 'Cont']:
    df = ugf.loc[ugf['EXTENT']==i]
    print(f"# lakes: {len(df)}, lake area: {df['areakm'].sum()}, mean lake size: {df['areakm'].mean()}")
ugf['areakm'].sum()

gf = lakes.loc[(lakes['glacial']=='Glaciated') & (lakes['text2']=='Fine')]
len(gf)
for i in ['unfrz', 'Isol', 'Spora', 'Discon', 'Cont']:
    df = gf.loc[gf['EXTENT']==i]
    print(f"# lakes: {len(df)}, lake area: {df['areakm'].sum()}, mean lake size: {df['areakm'].mean()}")

gf['areakm'].mean()


gc = lakes.loc[(lakes['glacial']=='Glaciated') & (lakes['text2']=='Coarse')]
len(gc)
for i in ['unfrz', 'Isol', 'Spora', 'Discon', 'Cont']:
    df = gc.loc[gc['EXTENT']==i]
    print(f"# lakes: {len(df)}, lake area: {df['areakm'].sum()}, mean lake size: {df['areakm'].mean()}")




