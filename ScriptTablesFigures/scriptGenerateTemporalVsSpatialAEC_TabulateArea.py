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
arcpy.env.workspace = r"C:\OneDrive - Washington State University (email.wsu.edu)\Projects\CafModelingAgroecosystemClasses\2017\Methods\GIS"
arcpy.env.overwriteOutput = True
tempFolder = arcpy.env.workspace + os.path.sep + tempFolderName
arcpy.CreateFolder_management(arcpy.env.workspace, tempFolderName)
arcpy.env.scratchWorkspace = tempFolder

temporalAecFilename = "CDL_2007-2016_TemporalAecFinal.tif"
# Note that I misused the term "anthrome" to mean "aec"
spatialAecFilename = "anthrome2016n.tif"

# from: https://geonet.esri.com/thread/110894
def TableToCSV(fc,CSVFile):  
      
    fields = [f.name for f in arcpy.ListFields(fc) if f.type <> 'Geometry']  
    with open(CSVFile, 'w') as f:  
        f.write(','.join(fields)+'\n') #csv headers  
        with arcpy.da.SearchCursor(fc, fields) as cursor:  
            for row in cursor:  
                f.write(','.join([str(r) for r in row])+'\n')  
    print("Created file: " + str(CSVFile))

arcpy.CheckOutExtension("spatial")

aecTemporalRaster = Raster(os.path.join(arcpy.env.workspace, workingDirName,temporalAecFilename))
aecSpatialRaster = Raster(os.path.join(arcpy.env.workspace, resultDirName, spatialAecFilename))
dbfPath = os.path.join(workingDirName,"TableTemporalVsSpatialAec.dbf")
csvPath = dbfPath[:-4]+".csv"

# snap raster
#arcpy.env.snapRaster = cdlRaster
    
# Create dbf file
try:
    arcpy.gp.TabulateArea_sa(
        aecSpatialRaster, "Value",
        aecTemporalRaster, "Value",
        dbfPath,
        "30")
except Exception as e:
    print(str(e))

# Convert dbf to csv
try:
    csvFullPath = os.path.realpath(csvPath)
    dbfFullPath = os.path.realpath(dbfPath)

    open(csvFullPath, 'a').close()

    TableToCSV(dbfFullPath, csvFullPath)

except Exception as e:
    print(str(e))

# Delete dbf file
try:
    arcpy.Delete_management(dbfPath)
except Exception as e:
    print(str(e))

arcpy.CheckInExtension("spatial")

# Cleanup
arcpy.Delete_management(tempFolder)