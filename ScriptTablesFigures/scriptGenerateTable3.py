import arcpy
from arcpy import env
from arcpy.sa import *
import os.path
import glob
import csv

# --- PARAMS AND SETUP ---------------------------------------------------------
workingTempDirName = "WorkingTemp"
workingDirName = "Working"
resultDirName = "Results"
tempFolderName = "temp"
inputFolderName = "Input"

arcpy.env.workspace = r"C:\OneDrive - Washington State University (email.wsu.edu)\Projects\CafModelingAgroecosystemClasses\2017\Methods\GIS"
arcpy.env.overwriteOutput = True

tempFolder = arcpy.env.workspace + os.path.sep + tempFolderName
arcpy.CreateFolder_management(arcpy.env.workspace, tempFolderName)
arcpy.env.scratchWorkspace = tempFolder

pathToMajorityAnthrome = os.path.join(arcpy.env.workspace, workingTempDirName, "majorityRaster.tif")
pathToSoilsLayer = os.path.join(arcpy.env.workspace, inputFolderName, "SoilOrders", "reacchs_utm")
pathToAnnualPrecipLayer = os.path.join(arcpy.env.workspace, inputFolderName, "prism_utm800") 
pathToTemperatureLayer = os.path.join(arcpy.env.workspace, inputFolderName, "temp_utm800") 

# //- PARAMS AND SETUP ---------------------------------------------------------

# --- FUNCTIONS ----------------------------------------------------------------
# from: https://geonet.esri.com/thread/110894
def TableToCSV(fc,CSVFile):  
    fields = [f.name for f in arcpy.ListFields(fc) if f.type <> 'Geometry']  
    with open(CSVFile, 'w') as f:  
        f.write(','.join(fields)+'\n') #csv headers  
        with arcpy.da.SearchCursor(fc, fields) as cursor:  
            for row in cursor:  
                f.write(','.join([str(r) for r in row])+'\n')  
    print("Created file: " + str(CSVFile)) 

def ConvertTableToCsv(pathToTable):
    pathToCsv = pathToTable[:-3] + "csv"
    open(pathToCsv, 'a').close()

    TableToCSV(pathToTable, pathToCsv)

    arcpy.Delete_management(pathToTable)

def createMajorityRaster(
    dirPathToAnthromeMaps, 
    workingTempDirName):

    print("Creating majority raster...")

    # Get annual anthrome maps
    anthromePaths = glob.glob(
        os.path.join(dirPathToAnthromeMaps, "anthrome*n.tif"))
    anthromes = []

    # Create rasters for each
    for anthromePath in anthromePaths:
        anthromes.append(Raster(anthromePath))
    
    print("... running cell statistics")
    majorityRasterTempPath = os.path.join(
        workingTempDirName, "majorityRasterTemp.tif")
    majorityPath = pathToMajorityAnthrome
    # Create MAJORITY Cell Statistic layer
    majorityRasterTemp = arcpy.gp.CellStatistics_sa(anthromes, 
        majorityRasterTempPath,
        "MAJORITY", "DATA")
    
    # Returns largest YYYY in list of anthromeYYYYn.tif
    anthromePathCurrYearPath = sorted(anthromePaths, reverse=True)[0]

    # The MAJORITY function in Cell Statistics returns NoData if a tie for majority, so fill these with current year's value'
    majorityRaster = Con(IsNull(majorityRasterTempPath), anthromePathCurrYearPath, majorityRasterTempPath)
    majorityRaster.save(majorityPath)

# Uses Arcpy's Tabulate Area function then converts the outputted dbf file to csv file
def createCrossTabulatedData(
    pathToZoneData, zoneField, 
    pathToFeatureClassData, classField, 
    pathToOutputDbf):

    zoneRaster = Raster(pathToZoneData)

    # Check if the raster is int, if not, convert (+0.5 is to round)
    if(zoneRaster.isInteger == False):
        zoneRaster = Int(zoneRaster + 0.5)

    # Create dbf file using tabulate area
    arcpy.gp.TabulateArea_sa(
            zoneRaster, zoneField,
            Raster(pathToFeatureClassData), classField,
            pathToOutputDbf,
            "30")

    ConvertTableToCsv(pathToOutputDbf)

    #pathToCsv = pathToOutputDbf[:-3] + "csv"
#
    #open(pathToCsv, 'a').close()

    
    
    # from: https://geonet.esri.com/thread/110894      
    #fields = [f.name for f in arcpy.ListFields(pathToOutputDbf) if f.type <> 'Geometry']  
    #with open(pathToCsv, 'w') as f:  
    #    f.write(','.join(fields)+'\n') #csv headers  
    #    with arcpy.da.SearchCursor(pathToOutputDbf, fields) as cursor:  
    #        for row in cursor:  
    #            f.write(','.join([str(r) for r in row])+'\n')  
    #print("CSV fie created at: " + str(pathToCsv))

    #arcpy.Delete_management(pathToOutputDbf)

def createZonalStatisticsAsTable(
    pathToZoneData, zoneField,
    pathToInputRaster,
    pathToOutputDbf):

    inputRaster = Raster(pathToInputRaster)

    # Check if the raster is int, if not, convert (+0.5 is to round)
    if(inputRaster.isInteger == False):
        inputRaster = Int(inputRaster + 0.5)

    arcpy.gp.ZonalStatisticsAsTable_sa(
        pathToZoneData, 
        zoneField,
        inputRaster,
        pathToOutputDbf,
        "DATA", "ALL")
    
    ConvertTableToCsv(pathToOutputDbf)

# //-- FUNCTIONS ---------------------------------------------------------------


# --- MAIN ---------------------------------------------------------------------
arcpy.CheckOutExtension("spatial")

#try:
#    createMajorityRaster(
#        os.path.join(arcpy.env.workspace, resultDirName),
#        os.path.join(arcpy.env.workspace, workingTempDirName))
#except Exception as e:
#    print(str(e))

# Cross tab for soils
print("Creating soil cross tab...")
try:
    createCrossTabulatedData(
       pathToSoilsLayer, "SUBORDER",
       pathToMajorityAnthrome, "Value",
       #os.path.join(arcpy.env.workspace, resultDirName, "Table3_anthromeSoilTab.dbf"))
       os.path.join(resultDirName, "Table3_anthromeSoilTab.dbf"))
except Exception as e:
    print(str(e))

# Cross tab for annual mean temp
print("Creating temperature zonal statistics...")
try:
    createZonalStatisticsAsTable(
        pathToMajorityAnthrome, "Value",
        pathToTemperatureLayer,
        #os.path.join(arcpy.env.workspace, resultDirName, "Table3_anthromeTempStat.dbf"))
        os.path.join(resultDirName, "Table3_anthromeTempStat.dbf"))

    #createCrossTabulatedData(
    #   pathToTemperatureLayer, "Value",
    #   pathToMajorityAnthrome, "Value",
    #   os.path.join(arcpy.env.workspace, resultDirName, "Table3_anthromeTempTab.dbf"))
except Exception as e:
    print(str(e))

# Cross tab for annual mean precip
print("Creating precipitation zonal statistics...")
try:
    #createCrossTabulatedData(
    #   pathToAnnualPrecipLayer, "Value",
    #   pathToMajorityAnthrome, "Value",
    #   os.path.join(arcpy.env.workspace, resultDirName, "Table3_anthromePrcipTab.dbf"))
    createZonalStatisticsAsTable(
        pathToMajorityAnthrome, "Value",
        pathToAnnualPrecipLayer,
        #os.path.join(arcpy.env.workspace, resultDirName, "Table3_anthromePrecipStat.dbf"))
        os.path.join(resultDirName, "Table3_anthromePrecipStat.dbf"))
except Exception as e:
    print(str(e))



arcpy.CheckInExtension("spatial")

# Cleanup
arcpy.Delete_management(tempFolder)
arcpy.Delete_management(os.path.join(arcpy.env.workspace, workingTempDirName, "majorityRasterTemp.tif"))
#arcpy.Delete_management(os.path.join(arcpy.env.workspace, workingTempDirName, "majorityRaster.tif"))

print("DONE")