import arcpy
from arcpy.sa import *

import pandas as pd
import os.path

# Parameters
workingDirName = "WorkingTemp"
resultDirName = "Results"
tempFolderName = "temp"

# Environment Parameters
arcpy.env.workspace = r"C:\Drive\Files\Projects\CafModelingAgroecosystemClasses\2017\Methods\GIS"
arcpy.env.overwriteOutput = True
tempFolder = arcpy.env.workspace + os.path.sep + tempFolderName
arcpy.CreateFolder_management(arcpy.env.workspace, tempFolderName)
arcpy.env.scratchWorkspace = tempFolder

years = [
    2007,
    2008,
    2009,
    2010,
    2011,
    2012,
    2013,
    2014,
    2015,
    2016]

# Python snippit
# Replace a layer/table view name with a path to a dataset (which can be a layer file) or create the layer/table view within the script
# The following inputs are layers or table views: "AECs\anthrome2013n.tif", "AECs\anthrome2014n.tif"
#arcpy.gp.TabulateArea_sa("AECs\anthrome2013n.tif", "Value", "AECs\anthrome2014n.tif", "Value", "C:/Files/Ars/Projects/AgroecosystemClasses/GIS/Results/Table1_2013-2014", "30")

arcpy.CheckOutExtension("spatial")

for i in range(len(years)):
    if(i < (len(years)-1)):
        earlyYear = Raster(resultDirName + os.path.sep + "anthrome" + str(years[i]) + "n.tif")
        laterYear = Raster(resultDirName + os.path.sep + "anthrome" + str(years[i+1]) + "n.tif")

        try:
            arcpy.gp.TabulateArea_sa(
                earlyYear, "Value",
                laterYear, "Value",
                resultDirName + os.path.sep + 
                    "Table1_" + str(years[i]) + "-" + str(years[i+1]) + ".dbf",
                "30")
        except Exception as e:
            print(e)

arcpy.CheckInExtension("spatial")

# Cleanup
arcpy.Delete_management(tempFolder)