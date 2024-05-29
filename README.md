# Alaska Lake and Pond Occurrence Dataset (ALPOD)
This repository stores the core algorithms used to produce ALPOD. Each algorithm's role in the overall dataset production is as follows:

## Step 1: Produce a maximum possible lake extent mask across Alaska ##
(1.1) S2bgrnExport.ipynb: Google Earth Engine (GEE) script to rapidly filter and visualize Sentinel-2 images. Used to identify and download 1-2 ice and cloud-free images per Sentinel-2 tile near the seasonal maximum lake extent.
(1.2) U-Net lake predictions (See Mullen et al., 2023 for details). 60 m buffer, vectorize, and merge results.
(1.3) Manually edit U-Net predictions in QGIS, correcting for both errors of omission and comission.
(1.4) Upload the edited maximum lake extent shapefile to GEE.


## Step 2: Produce lake occurrence image
(2.1) Split the study site into non-overlapping tile scheme, and upload tiles to GEE.
(2.2) LakeOccurrenceBatches.ipynb: GEE script to iterate through tiles and produce a lake occurrence image. Works by producing a daily cloud-masked Sentinel-2 mosaic, clipping to the maximum lake extent mask, filtering the collection to remove images below defined coverage threshold, classifies water in each image using an adaptive NDWI thresholding algorithm, and exports a composite of the water classifications.
(2.3) OccurrenceProcessing.py: Post-processing algorithm using a watershed segmentation method to clean up the GEE lake occurrence raster. Allows custom water occurrence thresholds to define lakes.

## Step 3: Merge results and vectorize
(3.1) zeros.py: converts data formats of the lake occurrence rasters to enable merging.
(3.2) merge.py: combine lake occurrence rasters by utm zone and export. binarize the occurrence raster and export.
(3.3) Manually vectorize the results in QGIS using raster conversion toolbox.
(3.4) Merge utm zone shapefiles in QGIS. Manually dissolve lakes spanning utm zones.

## Step 4: Intersect ancillary datasets
