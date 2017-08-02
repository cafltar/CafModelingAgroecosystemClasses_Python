import pandas as pd
import os.path
import errno
import sys
import math

# --- FUNCTIONS ----------------------------------------------------------------

# Purpose: Outputs an argument string for the Raster Calculator in ArcMap that 
#   extracts pixels of a certain value - filters pixels that belong to a certain 
#   category
# df = Pandas dataframe, with headers = Value, Name, Category
# category = "Irrigated, Ag, Forest, etc"
# rasterValue = The raster value to give the extracted pixels
# gisDataLayerName = The name of the datalayer in ArcMap
#TODO Update documentation for revision
#def XgetRasterCalcArgument(df, category, rasterValue, 
#                          gisDataLayerName = "Working\\CDL_2015.tif"):
#    
#    data = df.loc[df['Category'] == str(category)]
#
#    result = "---- " + str(category) + " ----\n"
#
#    result += "Con("
#
#    count = len(data.index)
#
#    for i in range(0, count):
#        result += "(\"" + gisDataLayerName + "\" == "
#        result += str(data.iloc[i]['Value'])
#        result += ")"
#        if i < count - 1:
#            result += " | "
#
#    result += ", " + str(rasterValue) + ")\n"
#    
#    return result

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
        #result += "(\"" + gisDataLayerName + "\" == " ##remove quotes for creating map algebra statement for scriptGenerateAec.py
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
outFileExtension = ".txt"
inFile  = "RasterValueCategories.csv"
outFile = "RasterCalculatorArgs" + outFileExtension
outFileHistoricBaseName = "RasterCalculatorHistoric" 
outFileAlgorithmicIrrigationLayer = "RasterCalculatorAlgorithmicIrr" + outFileExtension
#layerBaseName = "Working\\CDL_"
layerBaseName = "rasterIn"
layerNamePrecipitationData = "Working\prism_utm800"
layerNameAgIrrigatedBaseName = "AgIrrigated\\CDL_"
layerNameAgIrrigatedSuffix = "_AgIrrigated"
layerCurrentYear = 2016
#layerFileExtension = ".tif"
layerFileExtension = ""

pixelValueAgIrrigatedLayer = 1
pricipitationCutOff = 311
pixelValueAlgorithmicIrrLayer = 1
proportionCroppedCutoff = 6/9

# Constants
PIXEL_VALUE_FALLOW = 61

historicYears = [
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
    df = pd.read_csv("RasterValueCategories.csv")
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
                                  #layerBaseName + str(layerCurrentYear) + ## remove year from name for scriptGenerateAec.py
                                  layerBaseName + 
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