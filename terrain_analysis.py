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
    #raster.transform(shape_object)
    print(shape_object[0])
    print(shape_object[1])
    
    return ([0,1])


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
    #d = {['elev','fault', 'slope', 'LC','Geol', 'ls']}
    print("ENTRY create_dataframe")
    d = {'elev':topo.read(1).flatten(),
         'fault':geo.read(1).flatten(),
         'slope':slope.read(1).flatten(),
         'LC':lc.read(1).flatten(),
         'Geol':geo.read(1).flatten(),
         'ls':landslides}
 
    #print(d)
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
