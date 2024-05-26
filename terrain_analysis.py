import pandas as pd
import geopandas as gpd
import argparse
import sklearn
from sklearn.ensemble import RandomForestClassifier

def convert_to_rasterio(raster_data, template_raster):
    ''' Assign the data in the array from band 1 to band1
    '''
    band1 = template_raster.read(1)

    ''' Copy the values into raster_data using [:]
    '''
    raster_data[:] = band1
    
    ''' Return the file
    '''
    return template_raster


def extract_values_from_raster(raster, shape_object):
    ''' https://gis.stackexchange.com/questions/317391/extracting-raster-values-at-point-locations-using-python
    '''
    ''' https://geopandas.org/en/stable/gallery/geopandas_rasterio_sample.html
        https://blog.hubspot.com/website/python-zip#:~:text=The%20%60zip%60%20function%20in%20Python,from%20all%20the%20input%20iterables.
    ''' 
    gt = raster.transform

    #coord_list = [(x, y) for x, y in zip(shape_object["geometry"].x, shape_object["geometry"].y)]
    #coord_list = [(340467.5710219807, 3843321.793904966)]
    #print(coord_list)
    vls = raster.sample((340467.5710219807, 3843321.793904966)) 
    for current_vl in vls:
        print(current_vl)
    
    return vls


def make_classifier(x, y, verbose=False):
    ''' Create the forest classifier
    '''
    rf = RandomForestClassifier(verbose=verbose)
    
    ''' Train the ForestClassifier on the data
    '''
    rf.fit(x,y) 
    
    ''' Return the RandomForestClassifier
    '''
    return rf

def make_prob_raster_data(topo, geo, lc, dist_fault, slope, classifier):

    return

def create_dataframe(topo, geo, lc, dist_fault, slope, shape, landslides):
    ''' https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoDataFrame.html
        flatten to change from multimentional ND to 1d
    '''
    print(shape)

    print("ENTRY create_dataframe")
    d = {'elev':topo.read(1).flatten(),
         'fault':geo.read(1).flatten(),
         'slope':slope.read(1).flatten(),
         'LC':lc.read(1).flatten(),
         'Geol':geo.read(1).flatten(),
         'ls':landslides}
 
    print(d)
    df = pd.DataFrame(d)
    print(df)
    gf = gpd.geodataframe.GeoDataFrame(df)

    print("EXIT create_dataframe")    
    return(gf)

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


if __name__ == '__main__':
    main()
