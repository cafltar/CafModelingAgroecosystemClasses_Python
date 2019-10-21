#%%
import pathlib
import rasterio
import numpy as np
from rasterio.plot import show
from rasterio.warp import calculate_default_transform, reproject, Resampling

#%%
input_path = pathlib.Path.cwd() / "PercentFallowInAnnualAec" / "input"
daec_path = input_path / "aec" / "dynamicAec_20180307.tif"
cdl2007_path = input_path / "cdl" / "CDL_2007_clip_20180307153820_1352280378.tif"
cdl2010_path = input_path / "cdl" / "CDL_2010_clip_20180307153359_1188745125.tif"

#%%
daec = rasterio.open(daec_path)
cdl = rasterio.open(cdl2010_path)

# Read the dataset's valid data mask as a ndarray.
#mask = aec.dataset_mask(1)
daec_band = daec.read(1, masked=True)
cdl_band = cdl.read(1, masked=True)
#rasterio.plot.show(aec)

#%%
# These need to be the same
daec.bounds
cdl.bounds

# Before subtracting two rasters, need ensure they cover same area
# are the bounds the same?
print("Are the spatial extents the same?", daec.bounds == cdl.bounds), 

## is the resolution the same ??
print("Are the resolutions the same?", daec.res == cdl.res)

transform, width, heigh = calculate_default_transform(
    daec.crs, "epsg:32611", daec.width, daec.height, *daec.bounds)
kwargs = daec.meta.copy()

#reproject(
#    source = rasterio.band(cdl, 1),
#    destination = rasterio.band(cdl, 1)
#    src_transform=daec.transform
#)

#%%
# pixel value 11 = stable annual aec, 111 = dynamic annual aec
is_annual = np.logical_or(daec_band == 11, daec_band == 111)

# pixel value 61 = Fallow/Idle Cropland
is_fallow = (cdl_band == 61)


is_annual_and_fallow = is_annual * is_fallow

show(is_annual_and_fallow)
#annual = aec_band[aec == 11]
#show(annual)



#%%
