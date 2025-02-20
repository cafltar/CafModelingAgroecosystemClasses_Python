import pandas as pd
import os.path
import errno
import sys
import math

# --- FUNCTIONS ----------------------------------------------------------------
def getRasterCalcArgument(df, categories, rasterValue,
                          gisDataLayerName, valuesToExclude = None,
                          shoulSetNoDataToZero = False):
    
    data = df.loc[df['Category'] == str(categories[0])]
    headerTitle = str(categories[0])

    if len(categories) > 1:
        for i in range(1, len(categories)):
            data = data.append(df.loc[df['Category'] == str(categories[i])])
            headerTitle += str(categories[i])
        
    result = "==== " + headerTitle + " ====\n"

    if valuesToExclude != None:
        for i in range(0, len(valuesToExclude)):
            data = data[data['Value'] != valuesToExclude[i]]
    
    result += "Con("

    count = len(data.index)

    for i in range(0, count):
        result += "(" + gisDataLayerName + " == "
        result += str(data.iloc[i]['Value'])
        result += ")"
        if i < count - 1:
            result += " | "

    result += "," + str(rasterValue)
    
    if shoulSetNoDataToZero:
        result += ",0"
    
    result += ")\n"

    return result


# --- MAIN ---------------------------------------------------------------------

# Parameters
# Extension for output files
outFileExtension = ".txt"
# File to read pixel values, names, categories
inFile  = "Input\\RasterValueCategories.csv"
# Output file path where Raster Calculator arguments will be written (to be copy/pasted into ArcMap)
outFile = "Output\\RasterCalculatorArgsAecScript" + outFileExtension
# Output file path for writing Raster Calculator arguments to be copy/pasted into ArcMap
outFileHistoricBaseName = "Output\\RasterCalculatorHistoric" 
# Output file path for writing Raster Calculator arguments to be copy/pasted into ArcMap
outFileAlgorithmicIrrigationLayer = "Output\\RasterCalculatorAlgorithmicIrr" + outFileExtension
# Name and path of CDL layers in ArcMap - this will be used for Raster Calc
layerBaseName = "rasterIn"
# Group layer name and name of precip data in ArcMap - this will be used for Raster Calc
layerNamePrecipitationData = "Input\\prism_utm800"
layerNameAgIrrigatedBaseName = "AgIrrigated\\CDL_"
layerNameAgIrrigatedSuffix = "_AgIrrigated"
# Most recent year of CDL data to be analyzed, this is used to generate RasterCalculatorArgs.txt
layerCurrentYear = 2019
# Extension for output from Raster Calculator
layerFileExtension = ""

historicYears = [
    2019,
    2018,
    2017,
    2016,
    2015,
    2014,
    2013,
    2012,
    2011,
    2010]
pixelValueAgIrrigatedLayer = 1
pricipitationCutOff = 311
pixelValueAlgorithmicIrrLayer = 1
proportionCroppedCutoff = 0.7

# Constants
PIXEL_VALUE_FALLOW = 61



# Associate category with raster Value
mapCategoryToRasterValue = {
    "Urban"         : 1,
    "Range"         : 3,
    "Forest"        : 4,
    "Water"         : 5,
    "Wetland"       : 6,
    "Barren"        : 7,
    "Wilderness"    : 9,
    "Irrigated"     : 14,
    "Orchard"       : 15,
    "Ag"            : 99,
}

# Delete file if already exists
if os.path.isfile(outFile):
    os.remove(outFile)

# Read in map attributes
try:
    df = pd.read_csv(inFile)
except Exception as e:
    sys.stderr.write('ERROR: %sn' % str(e))

# Get unique categories in the data
categories = df.Category.unique()

# Write argument strings to output file to generate category layers
with open(outFile, 'a') as oFile:
    for cat in categories:
        oFile.write(
            getRasterCalcArgument(df, 
                                  [cat], 
                                  mapCategoryToRasterValue[cat], 
                                  layerBaseName))