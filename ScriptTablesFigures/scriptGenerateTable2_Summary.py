import csv
import glob
import pandas as pd

import os.path

# Parameters
workingPath = r"Working"

# Environment Parameters

dfs = []
# Garbs = Chick Peas + Dry bean
columnsToKeep = [   'Year', 'VALUE',        'VALUE_24',    'VALUE_23',     'VALUE_21', 'VALUE_52', 'VALUE_53', 'VALUE_51',     'VALUE_42',  'VALUE_31', 'VALUE_61', 'VALUE_36', 'VALUE_43', 'VALUE_1', 'AEC area']
columnNames = [     'Year', 'AEC class',    'Winter Wheat', 'Spring Wheat', 'Barley',  'Lentils',  'Peas',     'Chick Peas',   'Dry Beans', 'Canola',   'Fallow',   'Alfalfa',  'Potatoes', 'Corn', 'AEC area']
columnsNotAg = [ 'VALUE_63', 'VALUE_82', 'VALUE_87', 'VALUE_111', 'VALUE_112', 'VALUE_121', 'VALUE_122', 'VALUE_123', 'VALUE_124', 'VALUE_131', 'VALUE_141', 'VALUE_142', 'VALUE_143', 'VALUE_152', 'VALUE_176', 'VALUE_190', 'VALUE_195']

# AEC values: annual (11), transition (12), grain-fallow (13), irrigated (14), orchard (15)
rowsToKeep = [11,12,13,14,15]
rowNames = ['Annual', 'Transition', 'Grain-Fallow', 'Irrigated', 'Orchard']

# read csvs
csvFiles = glob.glob(os.path.join(workingPath, "Table2_*.csv"))

for f in csvFiles:
    
    # Assumes file ends with YYYY.csv
    year = f[-8:-4]
    df = pd.read_csv(f)

    # Keep only wanted rows and rename to AEC class names
    df = df.loc[df['VALUE'].isin(rowsToKeep)]
    df['VALUE'] = df['VALUE'].replace(rowsToKeep, rowNames)

    # Sum across rows to get total area per AEC before removing any columns
    sumAecArea = df.iloc[:,2:].sum(axis=1)
    
    # Remove non-ag columns
    cols = [c for c in columnsNotAg if c in df.columns]
    df = df.drop(cols, 1)

    # output for calculating DI via Table2_details.xlsx
    df.to_csv(os.path.join(workingPath, "forTable2_detailsXlsxDI_" + str(year) + ".csv"))

    # Now add summed aec column
    df['AEC area'] = sumAecArea

    # Add a year column to the start and append to df list
    df.insert(0,'Year', year)
    dfs.append(df)

data = pd.concat(dfs, ignore_index=True)
data = data.filter(columnsToKeep)
data.columns = columnNames
data = data.fillna(0)

# Combine chick peas and dry Beans
data['Dry Beans'] = data[['Chick Peas','Dry Beans']].sum(axis=1)
data = data.drop('Chick Peas', 1)

# Sum across rows to get total area per AEC
#data['AEC area'] = data.iloc[:,2:].sum(axis=1)

data.to_csv(os.path.join(workingPath, "forTable2_detailsXlsx_Cross_tab_ASEC_CDL.csv"))

print("Done")