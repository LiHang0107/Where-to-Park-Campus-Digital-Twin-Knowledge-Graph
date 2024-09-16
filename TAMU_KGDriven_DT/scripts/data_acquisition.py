import requests
import os
import json


def download_geojson(map_url, layer_id, output_directory):
    # URL
    layer_metadata_url = f"{map_url}{layer_id}?f=pjson"
    geojson_url = f"{map_url}{layer_id}/query?where=1=1&outFields=*&f=geojson&&returnGeometry=true"

    # define name
    metadata_response = requests.get(layer_metadata_url)
    if metadata_response.status_code == 200:
        metadata = metadata_response.json()
        layer_name = metadata.get('name', 'default_name').replace(" ", "_")
    else:
        print(f"Failed to get layer metadata for layer {layer_id}. Status code: {metadata_response.status_code}")
        return

    # data acquisition
    response = requests.get(geojson_url)
    if response.status_code == 200:
        geojson_data = response.json()
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)
        output_path = os.path.join(output_directory, f"{layer_name}.geojson")
        with open(output_path, 'w') as file:
            json.dump(geojson_data, file)
        print(f"GeoJSON data has been saved to {output_path}")
    else:
        print(f"Failed to download GeoJSON data for layer {layer_id}. Status code: {response.status_code}")


def main():
    output_directory = "./data/"

    # define URL
    map_url = 'https://gis.tamu.edu/arcgis/rest/services/FCOR/TAMU_BaseMap/MapServer/'
    ts_url = 'https://gis.tamu.edu/arcgis/rest/services/TS/TS_Main/MapServer/'

    for layer_id in [2, 3]:
        download_geojson(map_url, layer_id, output_directory)

    download_geojson(ts_url, 6, output_directory)


# 如果直接运行此脚本，则执行 main()
if __name__ == '__main__':
    main()
