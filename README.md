# Alaska Lake and Pond Occurrence Dataset (ALPOD)
This repository stores the core algorithms used to produce ALPOD. Each algorithm's role in the overall dataset production is as follows:

### Step 1: Produce a maximum possible lake extent mask across Alaska ##
(1.1) S2bgrnExport.ipynb: Google Earth Engine (GEE) script to rapidly filter and visualize Sentinel-2 images. Used to identify and download 1-2 ice and cloud-free images per Sentinel-2 tile near the seasonal maximum lake extent.<br />
(1.2) U-Net lake predictions (See Mullen et al., 2023 for details). 60 m buffer, vectorize, and merge results.<br />
(1.3) Manually edit U-Net predictions in QGIS, correcting for both errors of omission and comission.<br />
(1.4) Upload the edited maximum lake extent shapefile to GEE.<br />
<br />
### Step 2: Produce lake occurrence image
(2.1) Split the study site into non-overlapping tile scheme, and upload tiles to GEE.<br />
(2.2) LakeOccurrenceBatches.ipynb: GEE script to iterate through tiles and produce a lake occurrence image. Works by producing a daily cloud-masked Sentinel-2 mosaic, clipping to the maximum lake extent mask, filtering the collection to remove images below defined coverage threshold, classifies water in each image using an adaptive NDWI thresholding algorithm, and exports a composite of the water classifications.<br />
(2.3) OccurrenceProcessing.py: Post-processing algorithm using a watershed segmentation method to clean up the GEE lake occurrence raster. Allows custom water occurrence thresholds to define lakes.<br />
<br />
### Step 3: Merge results and vectorize
(3.1) zeros.py: converts data formats of the lake occurrence rasters to enable merging.<br />
(3.2) merge.py: combine lake occurrence rasters by utm zone and export. binarize the occurrence raster and export.<br />
(3.3) Manually vectorize the results in QGIS using raster conversion toolbox.<br />
(3.4) Merge utm zone shapefiles in QGIS. Manually dissolve lakes spanning utm zones.<br />
<br />

### Steps 1-3 are in support of constructing ALPOD. Steps 4 and 5 are in support of the analysis for the manuscript: 'Constraining permafrost controls on the distribution of lakes and ponds across Alaska using a new high-resolution lake dataset'

### Step 4: Intersect ancillary datasets
(4.1) hu12.py: aggregates lake statistics to NHD watersheds, and spatially joins watersheds with ancillary datasets to classify watersheds by permafrost extent, glacial history, and geologic substrate by intersect.
(4.2) Produce a union of glacial, permafrost, and geology dataset to produce a feature for each unique combination of classes.
(4.3) terrainClassLakeStatistics.py: 
### Step 5: 
