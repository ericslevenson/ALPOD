#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 19 10:55:22 2024

@author: ericlevenson

description: Spatial joins and overlays to assign attributes to watersheds 
(relief, MAP, glacial history), and assign lakes to watersheds.
"""

import os
import numpy as np
import pandas as pd
import geopandas as gpd


## Step 1: Attaching permafrost, geologic, and glacial attributes to watersheds

# read in watersheds
ws = gpd.read_file('/Users/ericlevenson/Dropbox (University of Oregon)/ArcticLakeScan/GIS_layers/watersheds/hu12_clipped.shp')
# read in watershed centroids
wsc = gpd.read_file('/Users/ericlevenson/Dropbox (University of Oregon)/ArcticLakeScan/GIS_layers/watersheds/hu12_centroids.shp')
# read in permafrost
pfro = gpd.read_file('/Users/ericlevenson/Dropbox (University of Oregon)/ArcticLakeScan/GIS_layers/permafrost/UiO_PEX_PERZONES_5.0_20181128_2000_2016_NH/UiO_PEX_PERZONES_5.0_20181128_2000_2016_NH.shp')
# read in lgm
lgm = gpd.read_file('/Users/ericlevenson/Dropbox (University of Oregon)/ArcticLakeScan/GIS_layers/glacial/lgm_dissolve.shp')
# read in mi6
mi6= gpd.read_file('/Users/ericlevenson/Dropbox (University of Oregon)/ArcticLakeScan/GIS_layers/glacial/mi6_dissolve.shp')
# read in watersheds that were previously intersected with ak geology in qgis
wsgeo = gpd.read_file('/Users/ericlevenson/Dropbox (University of Oregon)/ArcticLakeScan/GIS_layers/watersheds/hu12_geol_union.shp')
# read in lake centroids with lake attributes
lp = gpd.read_file('/Users/ericlevenson/Dropbox (University of Oregon)/ArcticLakeScan/products/analysis/lakePointsPermHandTriElevDa.shp'))


# reproject to albers
ws = ws.to_crs('EPSG:3338')
wsc = wsc.to_crs('EPSG:3338')
pfro = pfro.to_crs('EPSG:3338')
lgm = lgm.to_crs('EPSG:3338')
mi6 = mi6.to_crs('EPSG:3338')
wsgeo = wsgeo.to_crs('EPSG:3338')
lp = lp.to_crs('EPSG:3338')

# attach permafrost to centroids
wsc = gpd.sjoin(wsc, pfro, how='left')
# attach lgm to centroids
wsc = wsc.drop(columns='index_right')
wsc = gpd.sjoin(wsc, lgm, how='left')
# rename FEATURE to lgm
wsc = wsc.rename(columns={'FEATURE':'LGM', 'EXTENT':'pfextent'})
# fill nas with unglaciated
wsc['LGM'] = wsc['LGM'].fillna('no')
wsc = wsc.drop(columns='index_right')
# attach MI6
wsc = gpd.sjoin(wsc, mi6, how='left')
wsc['MI6'] = wsc['MI6'].fillna('no')
# attach second permafrost dataset to centroids
wsc = gpd.sjoin(wsc, pfro2, how='left')
wsc = wsc.drop(columns='index_right')
wsc.columns
ws.columns

# merge with watersheds

# dropping repeat columns
wsc = wsc.drop(columns=['name', 'geometry', 'states', 'geometry', 'ID', 'GRIDCODE' ])
ws = pd.merge(ws, wsc, on='huc12')
ws.columns

### Adding geology

# Step 1: categorize texture to create column for dominant texture in watershed
wsgeo['TEXTURE'] = wsgeo['TEXTURE'].astype('category')
categories = wsgeo['TEXTURE'].cat.categories
# Step 1.5: add area column
wsgeo['area'] = wsgeo['geometry'].area
# Step 2: create dataframe with area for unique texture and huc12 combinations
category_area_per_huc12 = wsgeo.groupby(['huc12', 'TEXTURE'])['area'].sum()
category_area_per_huc12.reset_index(inplace=True)
wsgeo.rename(columns={'index': 'huc12'}, inplace=True)

# Step 3: Pivot the table to get categories as columns and merge with df1
category_area_per_huc12 = category_area_per_huc12.reset_index().pivot(index='huc12', columns='TEXTURE', values='area').fillna(0)
category_area_per_huc12.head()

# Step 4: Merge with df1
ws = ws.merge(category_area_per_huc12, on='huc12', how='left')
max_column_names = ws.idxmax(axis=1)
ws['texture'] = ws[['Ice', 'Rocky', 'Sandy', 'Silty', 'Water']].idxmax(axis=1)
ws['texture'] = ws[['Rocky', 'Sandy', 'Silty']].idxmax(axis=1)
set(list(ws['text']))

## STEP2: get statistics about lakes and attach to watersheds

# Okay, now merge with the lakes!

lp = gpd.sjoin(lp, ws, how='left')
lp.columns

## STATS: number of lakes, total lake area, median lake area, range of lake area, median ratio, 
huc_ids = ws['huc12'].tolist() # list of grid ids
lakeAreas_total = [] # initialize list of lake area per grid
lakeAreas_median = [] # initialize list of lake area per grid
lakeAreas_min = []
lakeAreas_max =[] # initialize list of lake area per grid
lakeAreas_std =[]
lakeAreas_mean = []
lake_count = []
lakePers = []
deltaArea_total = []
deltaRad_total = []
thresh50s = []
b50s = []
a50s=[]
thresh75s = []
b75s = []
a75s=[]
thresh25s = []
b25s = []
a25s=[]

# Function to find lake size at which >50% of lake area
def lakeSize(gridDF, column_value, threshold):
    # Calculate the sum of the column
    total_sum = gridDF[column_value].sum()
    # Sort the column values in ascending order
    sorted_values = gridDF[column_value].sort_values()
    cumulative_sum = 0
    threshold_value = None
    count_above = 0
    count_below = 0
    # Iterate through sorted values to find the threshold
    for value in sorted_values:
        cumulative_sum += value
        # Check if 50% of the sum has been reached
        if cumulative_sum >= total_sum * threshold:
            threshold_value = value
            break
    # Count rows above and below the threshold
    count_above = (gridDF[column_value] > threshold_value).sum()
    count_below = (gridDF[column_value] <= threshold_value).sum()
    return threshold_value, count_above, count_below


# loop through ids
for f,i in enumerate(huc_ids):
    # define new df for specific grid cell
    gridDF = lp.loc[lp['huc12']==str(i)]
    #calculate statistics and append to lists
    
    #Lake Area
    lakeArea_total = gridDF['areakm'].sum()
    lakeAreas_total.append(lakeArea_total)
    lakeArea_median = gridDF['areakm'].median()
    lakeAreas_median.append(lakeArea_median)
    lakeArea_min = gridDF['areakm'].min()
    lakeAreas_min.append(lakeArea_min)
    lakeArea_max = gridDF['areakm'].max()
    lakeAreas_max.append(lakeArea_max)
    lakeArea_std = np.std(gridDF['areakm'])
    lakeAreas_std.append(lakeAreas_max)
    lakeArea_mean = np.mean(gridDF['areakm'])
    lakeAreas_mean.append(lakeArea_mean)
    #lakeArea variability
    lakeVar = gridDF['deltaArea'].sum()
    deltaArea_total.append(lakeVar)
    deltaRad = gridDF['deltaRad'].sum()
    deltaRad_total.append(deltaRad)
    lakePer_total = gridDF['perimeter'].sum()
    lakePers.append(lakePer_total)
    #Lake Count
    lake_count.append(len(gridDF))
    #Lake Size Thresholds
    thresh50, a50, b50 = lakeSize(gridDF, 'areakm', .5)
    thresh50s.append(thresh50)
    a50s.append(a50)
    b50s.append(b50)
    thresh75, a75, b75 = lakeSize(gridDF, 'areakm', .75)
    thresh75s.append(thresh75)
    a75s.append(a75)
    b75s.append(b75)
    thresh25, a25, b25 = lakeSize(gridDF, 'areakm', .25)
    thresh25s.append(thresh25)
    a25s.append(a25)
    b25s.append(b25)
    #Progress
    print(f, ', of ', len(huc_ids), ', ', len(gridDF))

# attaching to watersheds
ws['lake_area'] = lakeAreas_total
ws['lake_med'] = lakeAreas_median
ws['lake_mean'] = lakeAreas_mean
ws['lake_min'] = lakeAreas_min
ws['lake_max'] = lakeAreas_max
ws['lake_std'] = lakeAreas_std
ws['lake_count'] = lake_count
ws['deltaRadTot'] = deltaRad_total
ws['deltaAreaTot'] = deltaArea_total
ws['perimeter'] = lakePers    
# recalculate area
ws['area2'] = ws['geometry'].area/1000000
# water fraction
ws['lakeFrac'] = ws['lake_area']/ws['area2']
ws['deltaFrac'] = ws['deltaAreaTot']/ws['area2']
ws['t50'] = thresh50s
ws['a50'] = a50s
ws['b50'] = b50s
ws['t75'] = thresh75s
ws['a75'] = a75s
ws['b75'] = b75s
ws['t25'] = thresh25s
ws['a25'] = a25s
ws['b25'] = b25s



# Add geometry attributes
ws['areakm'] = ws['geometry'].area

# Create unfrozen category
ws['pfextent'] = ws['pfextent'].fillna('Unfrz')

# rename glacial classes
glacmap = {'no':'unglaciated', 'ICE':'glaciated'}
ws['LGM'] = ws['LGM'].map(glacmap)
ws['MI6'] = ws['MI6'].map(glacmap)

# Combine lgm and mi6
ws['glacial'] = ''
ws.loc[(ws['LGM']=='glaciated') | (ws['MI6']=='glaciated'), 'glacial'] = 'postglacial'
ws['glacial'] = ws['glacial'].map({'':'unglaciated', 'postglacial':'postglacial'})
ws['glacial'] = ws['glacial'].fillna('unglaciated')
# group fine substrate
ws['texture2'] = ''
ws.loc[ws['texture']=='Rocky', 'texture2'] = 'coarse'
ws.loc[ws['texture']=='Sandy', 'texture2'] = 'fine'
ws.loc[ws['texture']=='Silty', 'texture2'] = 'fine'

# combined terrain classifications (process domains)
ws['pd'] = ''
ws.loc[(ws['glacial'] == 'postglacial') & (ws['texture2']=='coarse'), 'pd'] = 'postglacial_coarse'
ws.loc[(ws['glacial'] == 'postglacial') & (ws['texture2']=='fine'), 'pd'] = 'postglacial_fine'
ws.loc[(ws['glacial'] == 'unglaciated') & (ws['texture2']=='coarse'), 'pd'] = 'unglaciated_coarse'
ws.loc[(ws['glacial'] == 'unglaciated') & (ws['texture2']=='fine'), 'pd'] = 'unglaciated_fine'

# dropping list column
ws = ws.drop(columns=['lake_std'])

# combining all terrain classes
ws['terr_class'] = ''
ws.loc[(ws['pd'] == 'unglaciated_fine') & (ws['pfextent']=='Unfrz'), 'terr_class'] = 'ug_fine_unfrz'
ws.loc[(ws['pd'] == 'unglaciated_fine') & (ws['pfextent']=='Isol'), 'terr_class'] = 'ug_fine_isol'
ws.loc[(ws['pd'] == 'unglaciated_fine') & (ws['pfextent']=='Spora'), 'terr_class'] = 'ug_fine_spora'
ws.loc[(ws['pd'] == 'unglaciated_fine') & (ws['pfextent']=='Discon'), 'terr_class'] = 'ug_fine_discon'
ws.loc[(ws['pd'] == 'unglaciated_fine') & (ws['pfextent']=='Cont'), 'terr_class'] = 'ug_fine_cont'

ws.loc[(ws['pd'] == 'unglaciated_coarse') & (ws['pfextent']=='Unfrz'), 'terr_class'] = 'ug_coarse_unfrz'
ws.loc[(ws['pd'] == 'unglaciated_coarse') & (ws['pfextent']=='Isol'), 'terr_class'] = 'ug_coarse_isol'
ws.loc[(ws['pd'] == 'unglaciated_coarse') & (ws['pfextent']=='Spora'), 'terr_class'] = 'ug_coarse_spora'
ws.loc[(ws['pd'] == 'unglaciated_coarse') & (ws['pfextent']=='Discon'), 'terr_class'] = 'ug_coarse_discon'
ws.loc[(ws['pd'] == 'unglaciated_coarse') & (ws['pfextent']=='Cont'), 'terr_class'] = 'ug_coarse_cont'

ws.loc[(ws['pd'] == 'postglacial_fine') & (ws['pfextent']=='Unfrz'), 'terr_class'] = 'g_fine_unfrz'
ws.loc[(ws['pd'] == 'postglacial_fine') & (ws['pfextent']=='Isol'), 'terr_class'] = 'g_fine_isol'
ws.loc[(ws['pd'] == 'postglacial_fine') & (ws['pfextent']=='Spora'), 'terr_class'] = 'g_fine_spora'
ws.loc[(ws['pd'] == 'postglacial_fine') & (ws['pfextent']=='Discon'), 'terr_class'] = 'g_fine_discon'
ws.loc[(ws['pd'] == 'postglacial_fine') & (ws['pfextent']=='Cont'), 'terr_class'] = 'g_fine_cont'

ws.loc[(ws['pd'] == 'postglacial_coarse') & (ws['pfextent']=='Unfrz'), 'terr_class'] = 'g_coarse_unfrz'
ws.loc[(ws['pd'] == 'postglacial_coarse') & (ws['pfextent']=='Isol'), 'terr_class'] = 'g_coarse_isol'
ws.loc[(ws['pd'] == 'postglacial_coarse') & (ws['pfextent']=='Spora'), 'terr_class'] = 'g_coarse_spora'
ws.loc[(ws['pd'] == 'postglacial_coarse') & (ws['pfextent']=='Discon'), 'terr_class'] = 'g_coarse_discon'
ws.loc[(ws['pd'] == 'postglacial_coarse') & (ws['pfextent']=='Cont'), 'terr_class'] = 'g_coarse_cont'


## Write to file
ws.to_file('/Users/ericlevenson/Dropbox (University of Oregon)/ArcticLakeScan/GIS_layers/watersheds/hu12_recreate.shp')

ws.columns
