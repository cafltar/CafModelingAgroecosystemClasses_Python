import arcpy
from arcpy import env

import glob
import pathlib
import os.path

def create_annual_raster(daec_path, write_path):
    """Takes a string path to a dynamic aec raster (produced via generate_dynamic_aecs.py) and outputs a raster with annual pixels (dynamic and stable) only
    """

    daec = arcpy.Raster(daec_path)
    
    # 11 = annual stable, 111 = annual dynamic, 61 = fallow
    annual = arcpy.sa.Con(((daec == 11) | (daec == 111)),1)

    annual.save(write_path)

def create_fallow_in_annual_raster(daec_path, cdl_path, write_path):
    """Takes a string path to a dynamic aec raster (produced via generate_dynamic_aecs.py) and a cropland data layer raster (clipped to CAF region) outputs a raster with fallow pixels within annual (dynamic and stable) only
    """
    
    daec = arcpy.Raster(daec_path)
    cdl = arcpy.Raster(cdl_path)

    # 11 = annual stable, 111 = annual dynamic, 61 = fallow
    fallow_in_annual = arcpy.sa.Con(((daec == 11) | (daec == 111)) & (cdl == 61),1)

    fallow_in_annual.save(write_path)

def get_annual_pixels(annual_raster_path):
    """Takes string path to annual raster (produced by create_annual_raster) and calculates total pixels of value == 1 (annual)
    """

    #annual_pixels = get_raster_pixels(annual)
    #arcpy.BuildRasterAttributeTable_management(annual, "Overwrite")
    annual_pixels = arcpy.SearchCursor(annual_raster_path).next().count

    return annual_pixels

def get_fallow_in_annual_pixels(fallow_in_annual_path):
    """Takes string path to fallow in annual raster (produced by create_fallow_in_annual_raster) and calculates total pixels of value == 1 (fallow in annual)
    """

    fallow_in_annual_pixels = arcpy.SearchCursor(fallow_in_annual_path).next().count

    return fallow_in_annual_pixels

def calculate_percent_follow_in_annual(annual_raster_path, fallow_in_annual_path):
    """Takes string path to fallow in annual raster (produced by create_fallow_in_annual_raster) and string path to annual raster (produced by create_annual_raster) and calculates percent fallow pixels within annual pixels
    """

    annual_pixels = get_annual_pixels(annual_raster_path)
    fallow_in_annual_pixels = get_fallow_in_annual_pixels(fallow_in_annual_path)

    percent_fallow_in_annual = 100 * (fallow_in_annual_pixels / annual_pixels)
    
    return(percent_fallow_in_annual)

def delete_files(folder_path):
    """Deletes all files within a directory
    """

    files_to_delete = glob.glob(os.path.join(folder_path, "*.*"))
    for f in files_to_delete:
        os.remove(f)

if __name__ == "__main__":
    """Calculates percent fallow pixels within annual pixels for all dynamic aecs
    
    Required: Arcpy 10.6 for Python 2.7, ArcGIS Spatial Analysis license
    Note: Run "generate_dynamic_aecs.py" if aec files are not in results

    """

    daec_dir_path = pathlib.PureWindowsPath(
        pathlib.Path.cwd(), 
        "PercentFallowInAnnualAec", "results")
    daec_glob_filter = pathlib.PureWindowsPath(
        daec_dir_path, "aec2007-*.tif")
    daec_paths = glob.glob(str(daec_glob_filter))

    write_path_rasters = pathlib.PureWindowsPath(
        pathlib.Path.cwd(),
        "PercentFallowInAnnualAec", 
        "results")

    # Set path to cropland data layer files
    cdl_dir_path = pathlib.PureWindowsPath(
        pathlib.Path.cwd(),
        "PercentFallowInAnnualAec", "input", "cdl")

    # Environment Parameters
    arcpy.env.overwriteOutput = True
    arcpy.env.workspace = str(
        pathlib.PureWindowsPath(
            pathlib.Path.cwd(),
            "PercentFallowInAnnualAec",
            "working"))

    arcpy.CheckOutExtension("spatial")

    percent_fallow_in_annuals = {}

    for daec_path in daec_paths:
        #print("daec: {}".format(daec_path))

        # Get latest year in daec
        daec_name = pathlib.Path(daec_path).stem
        latest_year = daec_name.split("-")[1]

        # Get corresponding CDL file
        cdl_glob_filter = pathlib.PureWindowsPath(
            cdl_dir_path, "CDL_{}_*.tif".format(latest_year))

        cdl_path = glob.glob(str(cdl_glob_filter))[0]

        write_path_annual_raster = pathlib.PureWindowsPath(
            write_path_rasters,
            "filtered_rasters",
            "annual_{}.tif".format(latest_year))
        write_path_fallow_in_annual_raster = pathlib.PureWindowsPath(
            write_path_rasters,
            "filtered_rasters",
            "fallow_in_annual_{}.tif".format(latest_year))
        
        # Create rasters based on pixel values
        create_annual_raster(
            str(daec_path), 
            str(write_path_annual_raster))
        create_fallow_in_annual_raster(
            str(daec_path), 
            str(cdl_path), 
            str(write_path_fallow_in_annual_raster))

        # Calculate percent fallow pixels within annual pixels
        percent_fallow_in_annual = calculate_percent_follow_in_annual(
            str(write_path_annual_raster), 
            str(write_path_fallow_in_annual_raster))

        print("{}: {}".format(latest_year, percent_fallow_in_annual))
        percent_fallow_in_annuals.update({latest_year : percent_fallow_in_annual})

        #delete_files(arcpy.env.workspace)

        
    print(percent_fallow_in_annuals)

    arcpy.CheckInExtension("spatial")