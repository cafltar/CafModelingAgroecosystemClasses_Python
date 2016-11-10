== Introduction ==
This script takes Cropland Data Layer (CDL) raster files (geoTIFF) and derives agroecosystem classes (AEC) for specified years in geoTIFF format and creates an aggregated layer that specifies dynamic and stable AECs, also in geoTIFF.

An ArcGIS license with Spatial Analyst is required.

The CDL layers used as input require some preparation.  Also, a common "Irrigation" layer needs to be generated outside of this project.  Instructions for this can be found here: <TODO: Link to data source>

== Basic program flow ==
For each year
	Create agroecosystem layer
		Set base Cropland Data Layer
		Set irrigation layer
		Create Anderson classification layers using map algebra (http://landcover.usgs.gov/pdf/anderson.pdf)
			Create Orchard layer
			Create Forest layer
			Create Wetland layer
			Create Water layer
			Create Urban layer
			Create Barren layer
			Create Range layer
			Create Ag layer
		Create Ag layer with Irrigation pixels removed using Raster Calculator
		Create Dryland layer using Extract By Mask tool
			ExtractByMask(rasterCdl, rasterAgNoIrrigated)
		Create Dryland Fallow layer using Raster Calculator
		Generate focal statistics using Focal Statistics tool
			FocalStatistics(rasterDrylandFallow, NbrRectangle(400,400,"CELL"),"MEAN","DATA")
		Use focal statistics to create annual, transition, grain-fallow layers
			rasterAnnual = Con((rasterFocalStatistic <= 0.1)&(rasterAgNoIrrigated==1),11)
			rasterTransition = Con((rasterFocalStatistic > 0.1)&(rasterFocalStatistic<=0.4)&(rasterAgNoIrrigated==1),12)
			rasterGrainFallow = Con((rasterFocalStatistic > 0.4)&(rasterAgNoIrrigated==1),13)
		Combine all layers using Mosaic To New Raster tool to create final aec layer
			arcpy.MosaicToNewRaster_management([rasterIrrMaster,rasterAnnual,rasterTransition,rasterGrainFallow,rasterOrchard,rasterForest,rasterWetland,rasterWater,rasterUrban,rasterBarren,rasterRange],resultDirName,"anthrome"+str(currYear)+"n.tif",coordinateSystem,"8_BIT_UNSIGNED",30,1,"FIRST","FIRST")
		Save intermediate layers if specified, otherwise delete

Create "anthrome" map with dynamic and stable AECs
	Find and set all paths to aec layers
	Create majority raster using Cell Statistics
		arcpy.gp.CellStatistics_sa(anthromes, majorityRasterTempPath,"MAJORITY", "DATA")
	Fill NoData values of majority raster with value of current year
		Con(IsNull(majorityRasterTempPath), anthromePathCurrYearPath, majorityRasterTempPath)
	Create variety raster using Cell Statistics
		arcpy.gp.CellStatistics_sa(anthromes, os.path.join(outputDirWorking, "varietyRaster.tif"),"VARIETY", "DATA")
	Set cutoff value for dynamic and unstable
	Determine stable, dynamic, unstable values using Raster Calculator
		stableRaster = Con(varietyPath, majorityPath, "", "Value = 1")
		dynamicRaster = Con(varietyPath, Raster(majorityPath) + 100, "", "Value > 1 AND Value < " + str(dynamicUnstableCuttoff))
		unstableRaster = Con(varietyPath, Raster(majorityPath) + 200, "", "Value >= " + str(dynamicUnstableCuttoff))
	Combine layers using Mosaic To New Raster tool
		arcpy.MosaicToNewRaster_management([stableRaster, dynamicRaster, unstableRaster],outputDirPathResult,"anthrome.tif",arcpy.SpatialReference("WGS 1984 UTM Zone 11N"),"8_BIT_UNSIGNED",30,1,"FIRST","FIRST")
	Save intermediate layers if specified, otherwise delete