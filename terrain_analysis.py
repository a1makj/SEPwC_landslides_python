''' Copyright 2024. CC-BY-SA.
'''

import argparse
import pandas as pd
import geopandas as gpd
from sklearn.ensemble import RandomForestClassifier
import rasterio
from rasterio import features
import gemgis as gg
from proximity import proximity


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
    ''' Creates a list with data from the raster template, associated with
        provided geometries

    Input: raster = an opened raster .tif file
           shape_object = geometries associated with two test points

    Output = a list containing two raster values associated
             with the test points
    '''

    coords_list = []

    for i, shape in enumerate(shape_object):
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


def make_classifier(x_data, y_data, verbose=False):
    ''' Create the forest classifier

    Input: x_data = two columns with test and train data
           y_data = column with 0s and 1s for classification

    Output: Random forest classifier
    '''
    rand_forest = RandomForestClassifier(verbose=verbose)

    rand_forest.fit(x_data,y_data)

    return rand_forest


def make_raster_from_shp(template, shapefile, file_name):
    ''' Converts a shapefile to raster, and saves to a file

    Input: topo = an opened raster .tif file
           dist_fault = an opened shapefile (.shp)

    Output: an array (file contents)
    '''

    geom = list(shapefile.geometry)

    rasterized = features.rasterize(geom,
                                    out_shape = template.shape,
                                    fill=0,
                                    transform=(28.55, 0.00, 339253.75,
                                               0.00, -28.55, 3846704.88,
                                               0.00, 0.00, 1.00),
                                    default_value=1,
                                    all_touched=True)
    # https://pygis.io/docs/e_raster_rasterize.html

    save_to_file(template, rasterized, file_name)

    return rasterized


def save_to_file(template, to_save, file_name):
    ''' Saves a dataset to a .tif file
    '''
    with rasterio.open(file_name,"w",
                        driver = "GTiff",
                        crs = template.crs,
                        transform = template.transform,
                        dtype = rasterio.uint8,
                        count = 1,
                        width = template.width,
                        height = template.height) as dst:
        dst.write(to_save,indexes=1)

    return to_save


def create_dist_from_fault_raster(fault_template_raster, topo):
    ''' Creates a "distance from fault" raster
    
    Input: fault_template_rater = ndarray with faultline location data
           topo = template .tif file
           
    Output: "distance from faultline" data for all coordinates in template
    '''

    distance = proximity(topo, fault_template_raster, 1)

    # distance array is normalised between 0-255
    distance *= 255.0/distance.max()
    # https://stackoverflow.com/questions/1735025/how-to-normalize-a-numpy-array-to-within-a-certain-range

    save_to_file(topo, distance, "distance_from_fault.tif")

    return distance


def make_prob_raster_data(topo,
                          geology,
                          land_cover,
                          dist_fault,
                          slope,
                          classifier):
    ''' Creating the landslide probability raster data
    '''

    #extract_values_from_raster(topo, )

    #landslides_gdf = create_dataframe(topo,
                      #geol,
                      #landc,
                      #distance_from_faultlines,
                      #slope_raster,
                      #extracted geometries of the landslides,
                      #landslides_raster)

    #return


def create_dataframe(topo,
                     geo,
                     land_cover,
                     dist_fault,
                     slope,
                     shape,
                     landslides):
    ''' GeoDataFrame created, containing all provided geographical data
        associated with desired geometries

        Input: topo, geo, land_cover, dist_fault, slope = an opened raster
               .tif file
               shape = a list containing geometries of two desired test points
               landslides = the value "0"

        Output: the GeoDataFrame
    '''

    data_dict = {'elev':extract_values_from_raster(topo, shape),
       'fault':extract_values_from_raster(dist_fault, shape),
       'slope':extract_values_from_raster(slope, shape),
       'LC':extract_values_from_raster(land_cover, shape),
       'Geol':extract_values_from_raster(geo, shape),
       'ls':landslides}
    # https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoDataFrame.html

    data_frame = pd.DataFrame(data_dict)

    geodata_frame = gpd.geodataframe.GeoDataFrame(data_frame)

    return geodata_frame


def main():
    ''' Establish argparse module
    '''

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

    topo = rasterio.open(args.topography)
    #geol = rasterio.open(args.geology)
    #landc = rasterio.open(args.landcover)
    faultshapefile = gpd.read_file(args.faults)
    landslideshapefile = gpd.read_file(args.landslides)

    # Create the slope raster
    slope_raster = gg.raster.calculate_slope(topo)
    slope_raster = save_to_file(topo, slope_raster, "slope_temp.tif")

    # Create a faultline raster, where 1=faultline and 0=no faultline
    fault_raster = make_raster_from_shp(topo,
                                        faultshapefile,
                                        "faultlines_temp.tif")

    # Create a "minimum distance from faultline" raster
    distance_from_faultlines = create_dist_from_fault_raster(fault_raster,
                                                             topo)

    # Create a raster where 1=landslide occurance and 0=no landslide occurance
    landslides_raster = make_raster_from_shp(topo,
                                             landslideshapefile,
                                             "landslide_occurance_temp.tif")

    landslide_coords = list(landslideshapefile.geometry)
    #values1 = extract_values_from_raster(topo, landslide_coords)



if __name__ == '__main__':
    main()
    