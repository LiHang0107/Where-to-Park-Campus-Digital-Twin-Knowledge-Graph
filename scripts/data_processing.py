import geopandas as gpd
import os


def process_building(building_geojson_path, output_dir, output_filename):
    building_gdf = gpd.read_file(building_geojson_path)
    building_attributes = building_gdf[['OBJECTID', 'BldgName', 'Bldg_Number', 'Address', 'YearBuilt', 'NumFloors', 'geometry']]
    building_attributes.to_file(os.path.join(output_dir, output_filename), driver='GeoJSON')
    print(f"{output_filename} has been saved")


def process_parking(parking_geojson_path, output_dir):
    parking_gdf = gpd.read_file(parking_geojson_path, on_invalid='ignore')
    parking_gdf = parking_gdf[parking_gdf.is_valid]
    parking_attributes = parking_gdf[['GIS.TS.ParkingLots.OBJECTID', 'GIS.TS.ParkingLots.LotName', 'GIS.TS.ParkingLots.Name',
                                      'GIS.TS.ParkingLots.LotType', 'GIS.TS.ParkingLots.Shape_STArea__',
                                      'GIS.TS.ParkingLots.Shape_STLength__', 'geometry']]
    parking_attributes = parking_attributes.rename(columns={
        'GIS.TS.ParkingLots.OBJECTID': 'OBJECTID',
        'GIS.TS.ParkingLots.LotName': 'LotName',
        'GIS.TS.ParkingLots.Name': 'Name',
        'GIS.TS.ParkingLots.LotType': 'LotType',
        'GIS.TS.ParkingLots.Shape_STArea__': 'Shape_STArea',
        'GIS.TS.ParkingLots.Shape_STLength__': 'Shape_STLength'
    })
    parking_attributes.to_file(os.path.join(output_dir, 'Parking_Lots.geojson'), driver='GeoJSON')
    print("Parking_Lots.geojson has been saved")


def process_geojson_files():
    building_geojson_paths = [
        ('./data/University_Building.geojson', 'University_Buildings.geojson'),
        ('./data/Non-University_Building.geojson', 'Non_University_Buildings.geojson')
    ]
    parking_geojson_path = './data/Parking_Lots.geojson'

    output_dir = './processed_data'
    os.makedirs(output_dir, exist_ok=True)

    for geojson_path, output_filename in building_geojson_paths:
        process_building(geojson_path, output_dir, output_filename)

    process_parking(parking_geojson_path, output_dir)

    print("all data has been processed")


if __name__ == '__main__':
    process_geojson_files()
