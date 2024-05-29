#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan  4 17:43:53 2024

@author: ericlevenson

Assess uncertainty in ALPOD
"""
import os
import pandas as pd
import random
import geopandas as gpd
import numpy as np


# read in grid of 5km cells
df = pd.read_csv('/Users/ericlevenson/Dropbox (University of Oregon)/ArcticLakeScan/GIS_layers/grids/AK_5km.csv')
# get list of cell ids
ids = list(df['id'])
len(ids)

# randomly sample cells
check = random.sample(ids, 100)
len(check)
print(check)


# Create empty dataframes for each cell
directory = '/Users/ericlevenson/Dropbox (University of Oregon)/ArcticLakeScan/uncertaintyAssessment/cells/'

columnNames = ['id', 'omittedCount', 'omittedArea', 'omittedType', 'comittedArea', 'comittedType', 'comittedConnection', 'splitLakeSize', 'splitLakeCount']
paths = [ i for i in os.listdir(directory) if i.endswith('.csv')] # list of paths
paths
for i in paths:
    print(i)
    df = pd.read_csv(str(directory + i))
    df['splitLakeSize'] = []
    df['splitLakeCount'] = []
    df['splitLakePerc'] = []
    df.to_csv(str(directory+i))
    #print(i)
    
    
    
### Creating a new QA grid shapefile
cellgdf = gpd.read_file('/Users/ericlevenson/Dropbox (University of Oregon)/ArcticLakeScan/GIS_layers/grids/AK_5km.shp')
cellgdf['nid'] = cellgdf['id'].astype(int) # new id column
gdf2 = cellgdf[cellgdf['nid'].isin(check)] # filter for QA ids
gdf2.to_file('/Users/ericlevenson/Dropbox (University of Oregon)/ArcticLakeScan/uncertaintyAssessment/QAcellsSHP/QAcells.shp')




###########################################
## ***Calculate Uncertainty*** ##
######################################

## Step 1: Calculate F1 score for the whole thing

# Read in QA cells
qac = gpd.read_file('/Users/ericlevenson/Dropbox (University of Oregon)/ArcticLakeScan/uncertaintyAssessment/QAcellsSHP/QAcells.shp')
# Read in lakes clipped to QAs
qal = gpd.read_file('/Users/ericlevenson/Dropbox (University of Oregon)/ArcticLakeScan/uncertaintyAssessment/qaLakes.shp')

# Calculate areas
qac['cellArea'] = qac['geometry'].area
qal['lakeArea'] = qal['geometry'].area
qal = qal.loc[qal['lakeArea'] >= 0.001]
len(qal)
# for each cell: true positive, true negative, false positive, false negative
###tp = lakeArea - comitted area
###tn = area-lakeArea -comitted area
###fp = comitted area
###fn = omitted area

totalArea = qac['cellArea'].sum()
totalLake = qal['lakeArea'].sum()
qac
qac['id'] = qac['id'].astype('int').astype('str')
paths = [ i for i in os.listdir(directory) if i.endswith('.csv')] # list of paths
cells = []
omittedAreas = []
comittedAreas = []

for i in paths:
    df = pd.read_csv(directory+i)
    print(i)
    oa = df['omittedArea'].sum()
    print(oa)
    ca = df['comittedArea'].sum()
    omittedAreas.append(oa)
    comittedAreas.append(ca)
    cells.append(i.split('.')[0])
totalOmit = sum(omittedAreas)
totalComit = sum(comittedAreas)

TruePositive = totalLake - totalComit # 47,013,914.44672472
TrueNegative = totalArea - totalOmit - totalLake - totalComit
FalsePositive = totalComit
FalseNegative = totalOmit
precision = TruePositive/(TruePositive+FalsePositive)
recall = TruePositive/(TruePositive+FalseNegative)
f1 = 2*(precision*recall)/(precision+recall)
print(f1) #0.9999999370179297


errorDF = pd.DataFrame({'id':cells, 'omissionArea': omittedAreas, 'comissionArea':comittedAreas})
gdf = pd.merge(qac, errorDF, on='id')
errorDF['error'] = gdf['comissionArea'] - gdf['omissionArea']
gdf.hist(column='error', bins='auto')


##### Getting lake info per cell
lakes2 = gpd.sjoin(qac, qal, how = 'right')

## STATS: number of lakes, total lake area, median lake area, range of lake area, median ratio, 
grid_ids = qac['id'].tolist() # list of grid ids
len(grid_ids)#67050
lakeAreas_total = [] # initialize list of lake area per grid
lake_count = []

qal.head()
# loop through ids
for f,i in enumerate(grid_ids):
    # define new df for specific grid cell
    gridDF = lakes2.loc[lakes2['id']==i]
    #calculate statistics and append to lists
    
    #Lake Area
    lakeArea_total = gridDF['lakeArea'].sum()
    #Lake Count
    lake_count.append(len(gridDF))
    lakeAreas_total.append(lakeArea_total)
    #Progress
    print(f, ', of ', len(grid_ids), ', ', len(gridDF))
    
errorDF['lakeAreaPredicted'] = lakeAreas_total
errorDF['lakeCountPredicted'] = lake_count
errorDF['lakeArea'] = errorDF['lakeAreaPredicted'] - errorDF['error']

mse = (errorDF['error']**2).sum()/100
print(mse) #0.07221822765587492
rmse = np.sqrt(mse)
print(rmse)#0.26873449286586737
mae = np.abs(errorDF['error']).sum()/100
print(mae)
from sklearn.metrics import r2_score
r2 = r2_score(errorDF['lakeArea'], errorDF['lakeAreaPredicted'])
print(r2) #0.9999999999999224

###metrics for the lake fraction
errorDF['lakeFracActual'] = errorDF['lakeArea']/qac['cellArea']
errorDF['lakeFracPredicted'] = errorDF['lakeAreaPredicted']/qac['cellArea']

errorDF['lakeFracError'] = errorDF['lakeFracPredicted']-errorDF['lakeFracActual']
errorDF.hist(column='lakeFracError',bins='auto')

mse = (errorDF['lakeFracError']**2).sum()/100
print(mse) #0.07221822765587492
rmse = np.sqrt(mse)
print(rmse)#0.26873449286586737
mae = np.abs(errorDF['lakeFracError']).sum()/100
print(mae)
from sklearn.metrics import r2_score
r2 = r2_score(errorDF['lakeArea'], errorDF['lakeAreaPredicted'])
print(r2) #0.9999999999999224
