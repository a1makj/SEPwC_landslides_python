import argparse
import pandas as pd
import geopandas as gpd
from sklearn.ensemble import RandomForestClassifier
import rasterio
from rasterio import features
import gemgis as gg

def convert_to_rasterio(raster_data, template_raster):
    ''' Raster file read and converted into numpy array

    Input: raster_data = numpy array, in the same shape as raster file
           template_raster = opened raster .tif file
 
    Output: a raster file and a numpy array containing values represented
            within the raster file
    '''

    band1 = template_raster.read(1)

    # Copy the values into raster_data using [:]
    raster_data[:] = band1

    return template_raster


def extract_values_from_raster(raster, shape_object):
    ''' Creates a list with data contained within the raster template,
    associated with the two provided geometries

    Input: raster = an opened raster .tif file
           shape_object = geometries associated with two test points

    Output = a list containing tworaster values associated with the test points
    '''

    coords_list = []

    #for i, shape in enumerate(shape_object):
    for shape in enumerate(shape_object):
        x_coord = shape.x
        y_coord = shape.y
        coords_list.append((x_coord, y_coord))
    # https://stackoverflow.com/questions/49635436/shapely-point-geometry-in-geopandas-df-to-lat-lon-columns
    # https://pylint.readthedocs.io/en/stable/user_guide/messages/convention/consider-using-enumerate.html

    vals = raster.sample(coords_list)
    # https://gis.stackexchange.com/questions/317391/extracting-raster-values-at-point-locations-using-python

    current_list = []
    for current_vl in vals:
        current_list.append(current_vl)

    return current_list


def make_classifier(x, y, verbose=False):
    ''' Create the forest classifier
    
    '''
    rand_forest = RandomForestClassifier(verbose=verbose)

    # Train the ForestClassifier on the data
    rand_forest.fit(x,y)

    # Return the RandomForestClassifier

    return rand_forest

def make_prob_raster_data(topo, geo, land_cover, dist_fault, slope, classifier):
    ''' Make a raster from the combination of the topography, geology,
    land cover, slope and distance from the fault
    https://pygis.io/docs/e_raster_rasterize.html
    '''
    # convert shape file to raster

    #print(dist_fault)
    geom = set(dist_fault.geometry)
    #geom = [shapes for shapes in dist_fault.geometry]

    #print(geom)
    rasterized = features.rasterize(geom,
                                    out_shape = topo.shape,
                                    fill=1,
                                    default_value=4,
                                    all_touched=True)

    print(rasterized)

    print(topo.transform)

    with rasterio.open("rasterized_dist_fault_temp.tif","w",
                        driver = "GTiff",
                        crs = topo.crs,
                        transform = topo.transform,
                        dtype = rasterio.uint8,
                        count = 1,
                        width = topo.width,
                        height = topo.height) as dst:
        dst.write(rasterized,indexes=1)

    return rasterized

def make_slope_raster_data(topo):
    ''' Make a slope raster from the topography
    
    '''
    slope = gg.raster.calculate_slope(topo)

    return slope

def create_dataframe(topo, geo, land_cover, dist_fault, slope, shape, landslides):
    ''' https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoDataFrame.html
        flatten to change from multimentional ND to 1d
    '''
    data_dict = {'elev':extract_values_from_raster(topo, shape),
       'fault':extract_values_from_raster(dist_fault, shape),
       'slope':extract_values_from_raster(slope, shape),
       'LC':extract_values_from_raster(land_cover, shape),
       'Geol':extract_values_from_raster(geo, shape),
       'ls':landslides}

    data_frame = pd.DataFrame(data_dict)

    geodata_frame = gpd.geodataframe.GeoDataFrame(data_frame)

    return geodata_frame

def main():

    parser = argparse.ArgumentParser(
                     prog="Landslide hazard using ML",
                     description="Calculate landslide hazards using simple ML",
                     epilog="Copyright 2024, Jon Hill"
                     )
    parser.add_argument('--topography',
                    required=True,
                    help="topographic raster file")
    parser.add_argument('--geology',
                    required=True,
                    help="geology raster file")
    parser.add_argument('--landcover',
                    required=True,
                    help="landcover raster file")
    parser.add_argument('--faults',
                    required=True,
                    help="fault location shapefile")
    parser.add_argument("landslides",
                    help="the landslide location shapefile")
    parser.add_argument("output",
                    help="the output raster file")
    parser.add_argument('-v', '--verbose',
                    action='store_true',
                    default=False,
                    help="Print progress")

    args = parser.parse_args()

    print(args)

    topo = rasterio.open(args.topography)
    geol = rasterio.open(args.geology)
    landc = rasterio.open(args.landcover)
    faultshapefile = gpd.read_file(args.faults)
    landslideshapefile = gpd.read_file(args.landslides)

    # create the slope raster
    slope = make_slope_raster_data(topo)

    # create the probability raster
    probability = make_prob_raster_data(topo,
                                        geol,
                                        landc,
                                        faultshapefile,
                                        landslideshapefile,
                                        slope)


if __name__ == '__main__':
    main()
    