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
        result += "(\"" + gisDataLayerName + "\" == "
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
outFile = "Output\\RasterCalculatorArgs" + outFileExtension
# Output file path for writing Raster Calculator arguments to be copy/pasted into ArcMap
outFileHistoricBaseName = "Output\\RasterCalculatorHistoric" 
# Output file path for writing Raster Calculator arguments to be copy/pasted into ArcMap
outFileAlgorithmicIrrigationLayer = "Output\\RasterCalculatorAlgorithmicIrr" + outFileExtension
# Name and path of CDL layers in ArcMap - this will be used for Raster Calc
layerBaseName = "Working\\CDL_"
# Group layer name and name of precip data in ArcMap - this will be used for Raster Calc
layerNamePrecipitationData = "Input\\prism_utm800"
layerNameAgIrrigatedBaseName = "AgIrrigated\\CDL_"
layerNameAgIrrigatedSuffix = "_AgIrrigated"
# Most recent year of CDL data to be analyzed, this is used to generate RasterCalculatorArgs.txt
layerCurrentYear = 2017
# Extension for output from Raster Calculator
layerFileExtension = ".tif"

historicYears = [
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
pixelValueAgIrrigatedLayer = 1
pricipitationCutOff = 311
pixelValueAlgorithmicIrrLayer = 1
#proportionCroppedCutoff = 7/float(len(historicYears))
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
                                  layerBaseName + str(layerCurrentYear) +
                                                  layerFileExtension))


# Write arugment strings to ouput file to generate agricultural + irrig layers
for year in historicYears:
    outFileName = outFileHistoricBaseName + str(year) + outFileExtension
    layerName = layerBaseName + str(year) + layerFileExtension

    # delete file if exists
    if os.path.isfile(outFileName):
        os.remove(outFileName)

    #write files
    categoriesToWrite = ["Irrigated", "Ag"]

    with open(outFileName, 'a') as oFile:
        oFile.write(
            getRasterCalcArgument(df, 
                                  categoriesToWrite, 
                                  pixelValueAgIrrigatedLayer, 
                                  layerName, 
                                  [PIXEL_VALUE_FALLOW],
                                  True)
        )

# Write argument string to ouptu file to generate algorithmic irrigation layer
# delete file if exists
if os.path.isfile(outFileAlgorithmicIrrigationLayer):
    os.remove(outFileAlgorithmicIrrigationLayer)

# Create and write output
with open(outFileAlgorithmicIrrigationLayer, 'a') as oFile:
    resultString = ("Con(((\"" + layerNamePrecipitationData + 
                    "\"<" + str(pricipitationCutOff) + 
                    ") & ((")

    for i in range(0, len(historicYears)):
        layerName = (layerNameAgIrrigatedBaseName + 
                    str(historicYears[i]) + 
                    layerNameAgIrrigatedSuffix + 
                    layerFileExtension)
        resultString += "\"" + layerName + "\""

        if i != len(historicYears) - 1:
            resultString += "+"
    
    resultString += ")>=" + str(math.ceil(len(historicYears) * proportionCroppedCutoff)) + ")),14)"
    oFile.write(
        resultString
    )