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

arcpy.env.workspace = r"G:\My Drive\Projects\CafModelingAgroecologicalClasses\2020\Working\ArcGIS"
arcpy.env.overwriteOutput = True

tempFolder = arcpy.env.workspace + os.path.sep + tempFolderName
arcpy.CreateFolder_management(arcpy.env.workspace, tempFolderName)
arcpy.env.scratchWorkspace = tempFolder

pathToDouglasZones = os.path.join(arcpy.env.workspace, inputFolderName, "Dzones", "Dzones.shp")
pathToEcoregions = os.path.join(arcpy.env.workspace, inputFolderName, "ecoregions", "ecoregions.shp") 
pathToMLRAs = os.path.join(arcpy.env.workspace, inputFolderName, "MLRAs", "MLRAs.shp") 

# //- PARAMS AND SETUP ---------------------------------------------------------

# --- FUNCTIONS ----------------------------------------------------------------
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
        #os.path.join(dirPathToAnthromeMaps, "anthrome*n.tif"))
        os.path.join(dirPathToAnthromeMaps, "aec*.tif"))
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
            pathToFeatureClassData, classField,
            pathToOutputDbf,
            "30")

    ConvertTableToCsv(pathToOutputDbf)

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

def createCrossTabulatedDataAllAnthromes(
    dirPathToAnthromeMaps,
    pathToFeatureClassData, classField,
    dirPathToOutputDbf):

    print("dirPathToAnthromeMaps: " + dirPathToAnthromeMaps)
    print("pathToFeatureClassData: " + pathToFeatureClassData)
    print("classField: " + classField)

    # Get annual anthrome maps
    anthromePaths = glob.glob(os.path.join(dirPathToAnthromeMaps, "aec*.tif"))

    for p in anthromePaths:
        anthromeFilename = os.path.basename(p)
        classFilename = os.path.basename(pathToFeatureClassData)

        # remove extension
        anthromeName = os.path.splitext(anthromeFilename)[0]
        className = os.path.splitext(classFilename)[0]

        createCrossTabulatedData(
            p, "Value",
            pathToFeatureClassData, classField,
            os.path.join(dirPathToOutputDbf, "Table4_" + className + "_" + anthromeName + ".dbf"))
    



# //-- FUNCTIONS ---------------------------------------------------------------


# --- MAIN ---------------------------------------------------------------------
arcpy.CheckOutExtension("spatial")

print("Creating DouglasZones cross tabulation...")
try:
    createCrossTabulatedDataAllAnthromes(
        os.path.join(arcpy.env.workspace, resultDirName),
        pathToDouglasZones, "Zone",
        #os.path.join(arcpy.env.workspace, resultDirName)
        os.path.join(resultDirName)
    )
except Exception as e:
    print(str(e))

# Ecoregions
print("Creating ecoregion cross tabulation...")
try:
    createCrossTabulatedDataAllAnthromes(
        os.path.join(arcpy.env.workspace, resultDirName),
        pathToEcoregions, "L4_KEY",
        #os.path.join(arcpy.env.workspace, resultDirName)
        os.path.join(resultDirName)
    )
except Exception as e:
    print(str(e))

# MLRAs
print("Creating MLRA cross tabulation...")
try:
    createCrossTabulatedDataAllAnthromes(
        os.path.join(arcpy.env.workspace, resultDirName),
        pathToMLRAs, "MLRA_NAME",
        #os.path.join(arcpy.env.workspace, resultDirName)
        os.path.join(resultDirName)
    )
except Exception as e:
    print(str(e))


arcpy.CheckInExtension("spatial")

# Cleanup
arcpy.Delete_management(tempFolder)

print("DONE")