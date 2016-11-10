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

arcpy.env.workspace = r"C:\Files\Ars\Projects\AgroecosystemClasses\GIS"
arcpy.env.overwriteOutput = True

tempFolder = arcpy.env.workspace + os.path.sep + tempFolderName
arcpy.CreateFolder_management(arcpy.env.workspace, tempFolderName)
arcpy.env.scratchWorkspace = tempFolder

pathToDouglasZones = os.path.join(arcpy.env.workspace, workingDirName, "Dzones.shp")
pathToEcoregions = os.path.join(arcpy.env.workspace, workingDirName, "ecoregions.shp") 
pathToMLRAs = os.path.join(arcpy.env.workspace, workingDirName, "MLRAs.shp") 

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

    # Get annual anthrome maps
    anthromePaths = glob.glob(os.path.join(dirPathToAnthromeMaps, "anthrome*n.tif"))

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

try:
    createCrossTabulatedDataAllAnthromes(
        os.path.join(arcpy.env.workspace, resultDirName),
        os.path.join(arcpy.env.workspace, workingDirName, "Dzones.shp"), "Zone",
        os.path.join(arcpy.env.workspace, resultDirName)
    )
except Exception as e:
    print(str(e))

# Ecoregions
print("Creating ecoregion cross tabulation...")
try:
    createCrossTabulatedDataAllAnthromes(
        os.path.join(arcpy.env.workspace, resultDirName),
        os.path.join(arcpy.env.workspace, workingDirName, "ecoregions.shp"), "L4_KEY",
        os.path.join(arcpy.env.workspace, resultDirName)
    )
except Exception as e:
    print(str(e))

# MLRAs
print("Creating MLRA cross tabulation...")
try:
    createCrossTabulatedDataAllAnthromes(
        os.path.join(arcpy.env.workspace, resultDirName),
        os.path.join(arcpy.env.workspace, workingDirName, "MLRAs.shp"), "MLRA_NAME",
        os.path.join(arcpy.env.workspace, resultDirName)
    )
except Exception as e:
    print(str(e))


arcpy.CheckInExtension("spatial")

# Cleanup
arcpy.Delete_management(tempFolder)

print("DONE")