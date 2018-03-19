import arcpy
from arcpy import env
from arcpy.sa import *

#import pandas as pd
import os.path
import glob

# --- PARAMS AND SETUP ---------------------------------------------------------
# Parameters
_irrigatedPath = os.path.join("Working","CDL_2007-2017_Irrigated_AlgorithmicIrrigated.tif")
_workingDirName = "WorkingTemp"
_resultDirName = "Results"
tempFolderName = "temp"
shouldSaveIntermediateLayers = True

# Environment Parameters
arcpy.env.workspace = r"C:\OneDrive - Washington State University (email.wsu.edu)\Projects\CafModelingAgroecosystemClasses\2018\Working\ArcGIS"
arcpy.env.overwriteOutput = True
arcpy.env.snapRaster = arcpy.env.workspace + os.path.sep + _irrigatedPath
tempFolder = arcpy.env.workspace + os.path.sep + tempFolderName
arcpy.CreateFolder_management(arcpy.env.workspace, tempFolderName)
arcpy.env.scratchWorkspace = tempFolder
#tmpFC = arcpy.CreateScratchNames(...., "in_memory") #from: https://geonet.esri.com/thread/89289

_coordinateSystem = arcpy.SpatialReference("WGS 1984 UTM Zone 11N")

years = [
    2017,
    2016,
    2015,
    2014,
    2013,
    2012,
    2011,
    2010,
    2009,
    2008,
    2007]
# //- PARAMS AND SETUP ---------------------------------------------------------


# --- FUNCTIONS ----------------------------------------------------------------
# The following get<Category>() functions return a ESRI map algebra expression which is generated from another script found in ScriptRasterCalculator\scriptCreateArgumentsForRasterCalculator

def getIrrigated(rasterIn):
    return Con((rasterIn == 1) | (rasterIn == 2) | (rasterIn == 3) | (rasterIn == 4) | (rasterIn == 5) | (rasterIn == 10) | (rasterIn == 11) | (rasterIn == 12) | (rasterIn == 13) | (rasterIn == 14) | (rasterIn == 26) | (rasterIn == 41) | (rasterIn == 43) | (rasterIn == 45) | (rasterIn == 46) | (rasterIn == 47) | (rasterIn == 48) | (rasterIn == 49) | (rasterIn == 50) | (rasterIn == 54) | (rasterIn == 56) | (rasterIn == 57) | (rasterIn == 60) | (rasterIn == 92) | (rasterIn == 206) | (rasterIn == 207) | (rasterIn == 208) | (rasterIn == 209) | (rasterIn == 213) | (rasterIn == 214) | (rasterIn == 216) | (rasterIn == 219) | (rasterIn == 221) | (rasterIn == 222) | (rasterIn == 224) | (rasterIn == 225) | (rasterIn == 226) | (rasterIn == 227) | (rasterIn == 229) | (rasterIn == 230) | (rasterIn == 231) | (rasterIn == 232) | (rasterIn == 233) | (rasterIn == 236) | (rasterIn == 237) | (rasterIn == 238) | (rasterIn == 239) | (rasterIn == 240) | (rasterIn == 241) | (rasterIn == 243) | (rasterIn == 244) | (rasterIn == 245) | (rasterIn == 246) | (rasterIn == 247) | (rasterIn == 248) | (rasterIn == 249) | (rasterIn == 254),14)

def getAg(rasterIn):
    return Con((rasterIn == 6) | (rasterIn == 21) | (rasterIn == 22) | (rasterIn == 23) | (rasterIn == 24) | (rasterIn == 25) | (rasterIn == 27) | (rasterIn == 28) | (rasterIn == 29) | (rasterIn == 30) | (rasterIn == 31) | (rasterIn == 32) | (rasterIn == 33) | (rasterIn == 34) | (rasterIn == 35) | (rasterIn == 36) | (rasterIn == 37) | (rasterIn == 38) | (rasterIn == 39) | (rasterIn == 42) | (rasterIn == 44) | (rasterIn == 51) | (rasterIn == 52) | (rasterIn == 53) | (rasterIn == 58) | (rasterIn == 59) | (rasterIn == 61) | (rasterIn == 205) | (rasterIn == 234) | (rasterIn == 235),99)

def getOrchard(rasterIn):
    return Con((rasterIn == 55) | (rasterIn == 66) | (rasterIn == 67) | (rasterIn == 68) | (rasterIn == 69) | (rasterIn == 70) | (rasterIn == 71) | (rasterIn == 72) | (rasterIn == 74) | (rasterIn == 75) | (rasterIn == 76) | (rasterIn == 77) | (rasterIn == 204) | (rasterIn == 210) | (rasterIn == 211) | (rasterIn == 212) | (rasterIn == 217) | (rasterIn == 218) | (rasterIn == 220) | (rasterIn == 223) | (rasterIn == 242) | (rasterIn == 250),15)

def getForest(rasterIn):
    return Con((rasterIn == 63) | (rasterIn == 141) | (rasterIn == 142) | (rasterIn == 143),4)

def getWetland(rasterIn):
    return Con((rasterIn == 87) | (rasterIn == 190) | (rasterIn == 195),6)

def getWater(rasterIn):
    return Con((rasterIn == 83) | (rasterIn == 111),5)

def getUrban(rasterIn):
    return Con((rasterIn == 82) | (rasterIn == 121) | (rasterIn == 122) | (rasterIn == 123) | (rasterIn == 124),1)

def getBarren(rasterIn):
    return Con((rasterIn == 65) | (rasterIn == 81) | (rasterIn == 88) | (rasterIn == 131),7)

def getRange(rasterIn):
    return Con((rasterIn == 62) | (rasterIn == 64) | (rasterIn == 152) | (rasterIn == 176),3)

def getWilderness(rasterIn):
    return Con((rasterIn == 112),9)

def createAecLayer(currYear, irrigatedPath, resultDirName, workingDirName, coordinateSystem):
    print("Starting year: "+str(currYear))

    rasterCdl=Raster("Working" + os.path.sep + "CDL_"+str(currYear) + ".tif")
    rasterIrrMaster=Raster(irrigatedPath)

    # Create category layers
    print("... Generating layer categories")
    rasterOrchard=      getOrchard(rasterCdl)
    rasterForest=       getForest(rasterCdl)
    rasterWetland=      getWetland(rasterCdl)
    rasterWater=        getWater(rasterCdl)
    rasterUrban=        getUrban(rasterCdl)
    rasterBarren=       getBarren(rasterCdl)
    rasterRange=        getRange(rasterCdl)
    rasterAg=           getAg(rasterCdl) 
    rasterWilderness=   getWilderness(rasterCdl)   

    # Create AgNoIrrigated layer
    print("... Generating AgNoIrrigated layer")
    rasterAgNoIrrigated=Con((rasterAg == 99) & (IsNull(rasterIrrMaster)),1)

    # Create Dryland layer
    print("... Generating Dryland layer")
    rasterDryland = ExtractByMask(rasterCdl, rasterAgNoIrrigated)

    # Create DrylandFallow layer
    print("... Generating DrylandFallow layer")
    rasterDrylandFallow = Con((rasterDryland == 61),1,0)

    # Generate focal statistic layer
    print("... Generating focal statistic")
    rasterFocalStatistic = FocalStatistics(rasterDrylandFallow, NbrRectangle(400,400,"CELL"),"MEAN","DATA")


    # General AECs
    print("... Generating AECs")
    rasterAnnual = Con((rasterFocalStatistic <= 0.1)&(rasterAgNoIrrigated==1),11)
    rasterTransition = Con((rasterFocalStatistic > 0.1)&(rasterFocalStatistic<=0.4)&(rasterAgNoIrrigated==1),12)
    rasterGrainFallow = Con((rasterFocalStatistic > 0.4)&(rasterAgNoIrrigated==1),13)

    # Combine all layers
    print("... Generating mosaic")
    arcpy.MosaicToNewRaster_management([rasterIrrMaster,rasterAnnual,rasterTransition,rasterGrainFallow,rasterOrchard,rasterForest,rasterWetland,rasterWater,rasterUrban,rasterBarren,rasterRange],
    resultDirName,"aec"+str(currYear)+".tif",coordinateSystem,"8_BIT_UNSIGNED",30,1,"FIRST","FIRST")


    if(shouldSaveIntermediateLayers == True):
        print("... Saving intermediate layers")
        rasterAg        .save(arcpy.env.workspace + os.path.sep + workingDirName +  os.path.sep + "CDL_"+str(currYear)+ "_Ag.tif")
        rasterOrchard   .save(arcpy.env.workspace + os.path.sep + workingDirName +  os.path.sep + "CDL_"+str(currYear)+ "_Orchard.tif")
        rasterForest    .save(arcpy.env.workspace + os.path.sep + workingDirName +  os.path.sep + "CDL_"+str(currYear)+ "_Forest.tif")
        rasterWetland   .save(arcpy.env.workspace + os.path.sep + workingDirName +  os.path.sep + "CDL_"+str(currYear)+ "_Wetland.tif")
        rasterWater     .save(arcpy.env.workspace + os.path.sep + workingDirName +  os.path.sep + "CDL_"+str(currYear)+ "_Water.tif")
        rasterUrban     .save(arcpy.env.workspace + os.path.sep + workingDirName +  os.path.sep + "CDL_"+str(currYear)+ "_Urban.tif")
        rasterBarren    .save(arcpy.env.workspace + os.path.sep + workingDirName +  os.path.sep + "CDL_"+str(currYear)+ "_Barren.tif")
        rasterRange     .save(arcpy.env.workspace + os.path.sep + workingDirName +  os.path.sep + "CDL_"+str(currYear)+ "_Range.tif")
        rasterWilderness.save(arcpy.env.workspace + os.path.sep + workingDirName +  os.path.sep + "CDL_"+str(currYear)+ "_Wilderness.tif")

        rasterAgNoIrrigated .save(arcpy.env.workspace + os.path.sep + workingDirName + os.path.sep + "CDL_"+str(currYear)+"_AgNoIrrigated.tif")
        rasterDryland       .save(arcpy.env.workspace + os.path.sep + workingDirName + os.path.sep + "CDL_"+str(currYear)+"_Dryland.tif")
        rasterDrylandFallow .save(arcpy.env.workspace + os.path.sep + workingDirName + os.path.sep + "CDL_"+str(currYear)+"_DrylandFallow.tif")
        rasterFocalStatistic.save(arcpy.env.workspace + os.path.sep + workingDirName + os.path.sep + str(currYear)+"_FocalStatistic.tif")
        rasterAnnual        .save(arcpy.env.workspace + os.path.sep + workingDirName + os.path.sep + "CDL_"+str(currYear)+"_Annual.tif")
        rasterTransition    .save(arcpy.env.workspace + os.path.sep + workingDirName + os.path.sep + "CDL_"+str(currYear)+"_Transition.tif")
        rasterGrainFallow   .save(arcpy.env.workspace + os.path.sep + workingDirName + os.path.sep + "CDL_"+str(currYear)+"_GrainFallow.tif")
    
    # Clean temperary files
    #print("... cleaning up temperary files")
    #if arcpy.Exists("in_memory"):
    #    arcpy.Delete_management("in_memory")

def createDynamicAecMap(dirPathToAecMaps, outputDirWorking, outputDirPathResult, shouldSaveIntermediateLayers = False):
    print("Creating dynamic aec map...")

    # Get annual anthrome maps
    aecPaths = glob.glob(os.path.join(dirPathToAecMaps, "aec*.tif"))
    aecs = []
    
    # Create rasters for each
    for aecPath in aecPaths:
        aecs.append(Raster(aecPath))
    
    print("... running cell statistics")
    majorityRasterTempPath = os.path.join(outputDirWorking, "majorityRasterTemp.tif")
    majorityPath = os.path.join(outputDirWorking, "majorityRaster.tif")
    # Create MAJORITY Cell Statistic layer
    majorityRasterTemp = arcpy.gp.CellStatistics_sa(aecs, 
        majorityRasterTempPath,
        "MAJORITY", "DATA")
    
    # Returns largest YYYY in list of aecYYYY.tif
    aecPathCurrYearPath = sorted(aecPaths, reverse=True)[0]

    # The MAJORITY function in Cell Statistics returns NoData if a tie for majority, so fill these with current year's value'
    majorityRaster = Con(IsNull(majorityRasterTempPath), aecPathCurrYearPath, majorityRasterTempPath)
    majorityRaster.save(majorityPath)
    
    varietyRaster = arcpy.gp.CellStatistics_sa(aecs, 
        os.path.join(outputDirWorking, "varietyRaster.tif"),
        "VARIETY", "DATA")
    
    
    varietyPath = os.path.join(outputDirWorking, "varietyRaster.tif")

    # Get cutoff value, should be greater than 50%
    dynamicUnstableCuttoff = int((len(aecPaths)/2) + 0.5)

    # Not using the {where_clause} sets NoData to 0, no idea why
    #stableRaster = Con((Raster(varietyPath) == 1), Raster(majorityPath))
    #dynamicRaster = Con((Raster(varietyRaster) > 1) & (Raster(varietyRaster) < dynamicUnstableCuttoff), Raster(majorityRaster), Raster(majorityRaster))
    #unstableRaster = Con((Raster(varietyRaster) >= dynamicUnstableCuttoff), Raster(majorityRaster), Raster(majorityRaster))

    print("... generating stable, dynamic, and unstable rasters")
    stableRaster = Con(varietyPath, majorityPath, "", "Value = 1")
    dynamicRaster = Con(varietyPath, Raster(majorityPath) + 100, "", "Value > 1 AND Value <= " + str(dynamicUnstableCuttoff))
    unstableRaster = Con(varietyPath, Raster(majorityPath) + 200, "", "Value > " + str(dynamicUnstableCuttoff))

    stableRaster.save(os.path.join(outputDirPathResult, "dynamicAecStable.tif"))
    dynamicRaster.save(os.path.join(outputDirPathResult, "dynamicAecDynamic.tif"))
    unstableRaster.save(os.path.join(outputDirPathResult, "dynamicAecUnstable.tif"))

    print("... compressing rasters")
    arcpy.MosaicToNewRaster_management(
        [stableRaster, dynamicRaster, unstableRaster],
        outputDirPathResult,"dynamicAec.tif",
        arcpy.SpatialReference("WGS 1984 UTM Zone 11N"),
        "8_BIT_UNSIGNED",30,1,"FIRST","FIRST")

    print("... cleaning up")
    # Cleanup
    if(shouldSaveIntermediateLayers == False):
        #arcpy.Delete_management(stableRaster)
        #arcpy.Delete_management(dynamicRaster)
        arcpy.Delete_management(majorityRaster)
        arcpy.Delete_management(majorityRasterTemp)
        arcpy.Delete_management(varietyRaster)

# //-- FUNCTIONS ---------------------------------------------------------------


# --- MAIN ---------------------------------------------------------------------
arcpy.CheckOutExtension("spatial")

#TODO: Function to create a new Irrigated layer, sets irrigatedPath

# Uses static irrigation layer to create an AEC map for each year in years
for year in years:
    try:
        createAecLayer(year, _irrigatedPath, _resultDirName, _workingDirName, _coordinateSystem)   
    except Exception as e:
        print(e)

# Finds all anthrome maps in Results directory and creates aggregate Anthrome
try:
    createDynamicAecMap(os.path.join(arcpy.env.workspace, _resultDirName),
        os.path.join(arcpy.env.workspace, _workingDirName),
        os.path.join(arcpy.env.workspace, _resultDirName),
        shouldSaveIntermediateLayers)
except Exception as e:
    print(str(e))


arcpy.CheckInExtension("spatial")

# Cleanup
arcpy.Delete_management(tempFolder)
#if arcpy.Exists("in_memory"):
#    arcpy.Delete_management("in_memory")

print("DONE")