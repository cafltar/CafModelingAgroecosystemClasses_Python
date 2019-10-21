#%%
import arcpy
from arcpy import env
from arcpy.sa import *

import os.path
import glob
import pathlib
import shutil

def create_majority_raster(
    aecs, 
    aecPaths, 
    outputDirWorking):

    print("Creating majority raster...")

    print("... running cell statistics on {} rasters".format(len(aecs)))
    majorityRasterTempPath = os.path.join(
        outputDirWorking, "majorityRasterTemp.tif")
    majorityPath = os.path.join(
        outputDirWorking, "majorityRaster.tif")
     #majorityPath = os.path.join(outputDirPathResult, "majorityRaster.tif")
    # Create MAJORITY Cell Statistic layer
    majorityRasterTemp = arcpy.gp.CellStatistics_sa(
        aecs, majorityRasterTempPath, "MAJORITY", "DATA")

    # Returns largest YYYY in list of aecYYYY.tif
    aecPathCurrYearPath = sorted(aecPaths, reverse=True)[0]

    # The MAJORITY function in Cell Statistics returns NoData if a tie for majority, so fill these with current year's value'
    majorityRaster = Con(
        IsNull(majorityRasterTempPath), 
        aecPathCurrYearPath, 
        majorityRasterTempPath)

    majorityRaster.save(majorityPath)

    return majorityPath

def create_variety_raster(
    aecs, 
    outputDirWorking):

    print("Creating variety raster...")

    varietyRaster = arcpy.gp.CellStatistics_sa(aecs, 
        os.path.join(outputDirWorking, "varietyRaster.tif"),
        "VARIETY", "DATA")
    varietyPath = os.path.join(outputDirWorking, "varietyRaster.tif")

    return varietyPath

def create_stable_raster(
    varietyPath, 
    majorityPath, 
    outputDirPathResult):

    print("Creating stable raster...")

    stableRaster = Con(varietyPath, majorityPath, "", "Value = 1")
    stableRaster.save(os.path.join(outputDirPathResult, "dynamicAecStable.tif"))
    
    return stableRaster

def create_dynamic_raster(
    varietyPath, 
    majorityPath, 
    dynamicUnstableCuttoff, 
    outputDirPathResult):

    print("Creating dynamic raster...")

    dynamicRaster = Con(
        varietyPath, 
        Raster(majorityPath) + 100, "", 
        "Value > 1 AND Value <= " + str(dynamicUnstableCuttoff))
    dynamicRaster.save(
        os.path.join(outputDirPathResult, "dynamicAecDynamic.tif"))

    return dynamicRaster

def create_unstable_raster(
    varietyPath, 
    majorityPath, 
    dynamicUnstableCuttoff, 
    outputDirPathResult):

    print("Creating unstable raster...")

    unstableRaster = Con(
        varietyPath, 
        Raster(majorityPath) + 200, "", 
        "Value > " + str(dynamicUnstableCuttoff))
    unstableRaster.save(
        os.path.join(outputDirPathResult, "dynamicAecUnstable.tif"))

    return unstableRaster

#%%
def create_dynamic_aec_map(
    dirPathToAecMaps, 
    outputDirWorking, 
    outputDirPathResult, 
    shouldSaveIntermediateLayers = False):
    
    print("__Creating dynamic aec map__")

    # Get annual anthrome maps
    glob_path = pathlib.PureWindowsPath(dirPathToAecMaps, "aec*.tif")
    aecPaths = glob.glob(str(glob_path))
    #print("aecPaths: {}".format(aecPaths))
    aecs = []

    # Create rasters for each
    for aecPath in aecPaths:
        aecs.append(Raster(aecPath))
        
    print("__Generating majority and variety rasters__")
    majorityPath = create_majority_raster(aecs, aecPaths, outputDirWorking)
    varietyPath = create_variety_raster(aecs, outputDirWorking)
    
    # Get cutoff value, should be greater than 50%
    dynamicUnstableCuttoff = int((len(aecPaths)/2) + 0.5)

    print("__Generating stable, dynamic, and unstable rasters__")
    clear_locked_files(outputDirWorking)
    stableRaster = create_stable_raster(
        varietyPath, 
        majorityPath, 
        outputDirPathResult)
    
    clear_locked_files(outputDirWorking)
    dynamicRaster = create_dynamic_raster(
        varietyPath, 
        majorityPath, 
        dynamicUnstableCuttoff, 
        outputDirPathResult)
    
    clear_locked_files(outputDirWorking)
    unstableRaster = create_unstable_raster(
        varietyPath, 
        majorityPath, 
        dynamicUnstableCuttoff, 
        outputDirPathResult)
    
    print("__Compressing rasters__")
    arcpy.MosaicToNewRaster_management(
        [stableRaster, dynamicRaster, unstableRaster],
        outputDirPathResult,"dynamicAec.tif",
        arcpy.SpatialReference("WGS 1984 UTM Zone 11N"),
        "8_BIT_UNSIGNED",30,1,"FIRST","FIRST")

def clear_locked_files(folder_path):
    time.sleep(5)
    lock_files = glob.glob(os.path.join(folder_path, "*.lock"))
    
    if(len(lock_files) > 0):
        print("Awaiting locked files...")

    while len(lock_files) > 0:
        print(".")
        time.sleep(1)
        lock_files = glob.glob(os.path.join(folder_path, "*.lock"))

def delete_files(folder_path):
    files_to_delete = glob.glob(os.path.join(folder_path, "*.*"))
    for f in files_to_delete:
        os.remove(f)

#%%
input_path = pathlib.PureWindowsPath(
    pathlib.Path.cwd(), 
    "PercentFallowInAnnualAec", "input")

aec_glob_filter = pathlib.PureWindowsPath(
    input_path, "aec2007-*")

aec_paths = glob.glob(str(aec_glob_filter))

working_path = pathlib.PureWindowsPath(
    pathlib.Path.cwd(), 
    "PercentFallowInAnnualAec", "working")

output_path = pathlib.PureWindowsPath(
    pathlib.Path.cwd(), 
    "PercentFallowInAnnualAec", "output")

results_path = pathlib.PureWindowsPath(
    pathlib.Path.cwd(), 
    "PercentFallowInAnnualAec", "results")

arcpy.CheckOutExtension("spatial")

# Environment Parameters
arcpy.env.overwriteOutput = True

for aec_path in aec_paths:
    print("processing: {}".format(aec_path))

    try:
        create_dynamic_aec_map(
            aec_path, 
            str(working_path), 
            str(output_path))

        # Above function creates a geotif file named "dynamicAec.tif", move and rename so it's not overwritten by next iteration
        tif_src_path = pathlib.PureWindowsPath(output_path, "dynamicAec.tif")
        
        tif_dst_path = pathlib.PureWindowsPath(
            results_path, 
            pathlib.Path(aec_path).name + ".tif")

        shutil.copy2(str(tif_src_path), str(tif_dst_path))

        # Now clean up folders
        delete_files(str(output_path))
        delete_files(str(working_path))

    except Exception, e:
        import gc
        gc.collect()
        import traceback
        arcpy.AddError(traceback.format_exc())
        sys.exit(e)
    
arcpy.CheckOutExtension("spatial")