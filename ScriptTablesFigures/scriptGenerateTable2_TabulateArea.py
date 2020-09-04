import arcpy
import csv
from arcpy.sa import *

#import pandas as pd
import os.path

# Parameters
workingDirName = "Working"
resultDirName = "Results"
tempFolderName = "temp"

# Environment Parameters
arcpy.env.workspace = r"G:\My Drive\Projects\CafModelingAgroecologicalClasses\2020\Working\ArcGIS"
arcpy.env.overwriteOutput = True
tempFolder = arcpy.env.workspace + os.path.sep + tempFolderName
arcpy.CreateFolder_management(arcpy.env.workspace, tempFolderName)
arcpy.env.scratchWorkspace = tempFolder

years = [
    2010,
    2011,
    2012,
    2013,
    2014,
    2015,
    2016,
    2017,
    2018,
    2019]

# from: https://geonet.esri.com/thread/110894
def TableToCSV(fc,CSVFile):  
    #fields = [f.name for f in arcpy.ListFields(fc) if f.type <> 'Geometry']  
    fields = []
    for f in arcpy.ListFields(fc):
        if f.type != 'Geometry':
            fields.append(f.name)

    with open(CSVFile, 'w') as f:  
        f.write(','.join(fields)+'\n') #csv headers  
        with arcpy.da.SearchCursor(fc, fields) as cursor:  
            for row in cursor:  
                f.write(','.join([str(r) for r in row])+'\n')  
    print("Created file: " + str(CSVFile))

arcpy.CheckOutExtension("spatial")

for i in range(len(years)):
    #aecRaster = Raster(resultDirName + os.path.sep + "anthrome" + str(years[i]) + "n.tif")
    aecRaster = Raster(resultDirName + os.path.sep + "aec" + str(years[i]) + ".tif")
    cdlRaster = Raster(arcpy.env.workspace + os.path.sep + workingDirName + os.path.sep + "CDL_" + str(years[i]) + ".tif")
    dbfPath = resultDirName + os.path.sep + "Table2_" + str(years[i]) + ".dbf"
    csvPath = dbfPath[:-4]+".csv"

    # snap raster
    arcpy.env.snapRaster = cdlRaster
    
    # Create dbf file
    try:
        arcpy.gp.TabulateArea_sa(
            aecRaster, "Value",
            cdlRaster, "Value",
            dbfPath,
            "30")
    except Exception as e:
        print(str(e))
    
    # Convert dbf to csv
    try:
        csvFullPath = arcpy.env.workspace + os.path.sep + csvPath
        dbfFullPath = arcpy.env.workspace + os.path.sep + dbfPath

        open(csvFullPath, 'a').close()

        TableToCSV(dbfFullPath, csvFullPath)

    except Exception as e:
        print(str(e))

    # Delete dbf file
    try:
        #os.remove(dbfFullPath)
        arcpy.Delete_management(dbfPath)
    except Exception as e:
        print(str(e))

arcpy.CheckInExtension("spatial")

# Cleanup
arcpy.Delete_management(tempFolder)