import geopandas as gpd
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, XSD, OWL
import random
from datetime import datetime
import os
import pandas as pd  # 不要忘记引入 pandas


def process_geojson_and_create_ontology():
    # path
    building_geojson_paths = {
        './processed_data/University_Buildings.geojson': 'University',
        './processed_data/Non_University_Buildings.geojson': 'Non_University'
    }
    parking_geojson_path = './processed_data/Parking_Lots.geojson'

    parking_gdf = gpd.read_file(parking_geojson_path)
    parking_gdf = parking_gdf.to_crs(epsg=3857)  # 统一坐标系为 EPSG:3857 (以米为单位)

    # define Namespace
    GEO = Namespace('http://www.opengis.net/ont/geosparql#')
    TAMU_ONTO = Namespace('http://tamu.edu/ontologies/tamu_ont#')
    SOSA = Namespace('http://www.w3.org/ns/sosa/')

    # RDF
    g = Graph()
    g.bind('geo', GEO)
    g.bind('tamu_ont', TAMU_ONTO)
    g.bind('sosa', SOSA)

    # Class
    g.add((TAMU_ONTO.Building, RDF.type, OWL.Class))
    g.add((TAMU_ONTO.Building, RDFS.subClassOf, GEO.SpatialObject))
    g.add((TAMU_ONTO.ParkingLot, RDF.type, OWL.Class))
    g.add((TAMU_ONTO.ParkingLot, RDFS.subClassOf, GEO.SpatialObject))

    # nearby
    g.add((TAMU_ONTO.nearby, RDF.type, OWL.ObjectProperty))
    g.add((TAMU_ONTO.nearby, RDFS.domain, GEO.SpatialObject))
    g.add((TAMU_ONTO.nearby, RDFS.range, GEO.SpatialObject))

    # dict for instances
    building_instances = {}
    parking_instances = {}

    all_buildings_gdf = []

    def process_buildings(building_geojson_path, building_type):
        building_gdf = gpd.read_file(building_geojson_path)
        building_gdf = building_gdf.to_crs(epsg=3857)
        all_buildings_gdf.append(building_gdf)

        for idx, row in building_gdf.iterrows():
            building_id = f"{building_type}_Building_{row['OBJECTID']}"
            building_instance = URIRef(f"http://tamu.edu/ontologies/tamu_ont#{building_id}")
            building_instances[row['OBJECTID']] = building_instance  # save instance
            g.add((building_instance, RDF.type, TAMU_ONTO.Building))
            g.add((building_instance, RDFS.label, Literal(row['BldgName'], datatype=XSD.string)))
            g.add((building_instance, TAMU_ONTO.hasAddress, Literal(row['Address'], datatype=XSD.string)))
            g.add((building_instance, TAMU_ONTO.yearBuilt, Literal(row['YearBuilt'], datatype=XSD.string)))
            g.add((building_instance, TAMU_ONTO.numFloors, Literal(row['NumFloors'], datatype=XSD.integer)))

            # geometric
            g.add((building_instance, GEO.hasGeometry, Literal(row['geometry'].wkt, datatype=GEO.wktLiteral)))

    # building
    for geojson_path, building_type in building_geojson_paths.items():
        process_buildings(geojson_path, building_type)

    # combine_building
    combined_buildings_gdf = gpd.GeoDataFrame(pd.concat(all_buildings_gdf, ignore_index=True))

    # instance for parking lot
    for idx, row in parking_gdf.iterrows():
        parking_id = f"ParkingLot_{row['OBJECTID']}"
        parking_instance = URIRef(f"http://tamu.edu/ontologies/tamu_ont#{parking_id}")
        parking_instances[row['OBJECTID']] = parking_instance
        g.add((parking_instance, RDF.type, TAMU_ONTO.ParkingLot))
        g.add((parking_instance, RDFS.label, Literal(row['Name'], datatype=XSD.string)))
        g.add((parking_instance, TAMU_ONTO.lotType, Literal(row['LotType'], datatype=XSD.string)))
        g.add((parking_instance, TAMU_ONTO.area, Literal(row['Shape_STArea'], datatype=XSD.double)))
        g.add((parking_instance, TAMU_ONTO.length, Literal(row['Shape_STLength'], datatype=XSD.double)))

        g.add((parking_instance, GEO.hasGeometry, Literal(row['geometry'].wkt, datatype=GEO.wktLiteral)))

    # ObservableProperty
    occupancy_property = URIRef(f"http://tamu.edu/ontologies/tamu_ont#OccupancyRate")
    g.add((occupancy_property, RDF.type, SOSA.ObservableProperty))
    g.add((occupancy_property, RDFS.label, Literal('Occupancy Rate', datatype=XSD.string)))

    # Sensor
    sensor = URIRef(f"http://tamu.edu/ontologies/tamu_ont#ParkingSensor")
    g.add((sensor, RDF.type, SOSA.Sensor))
    g.add((sensor, RDFS.label, Literal('Parking Occupancy Sensor', datatype=XSD.string)))

    # Observation for every parking lot
    for parking_id, parking_instance in parking_instances.items():
        observation_id = f"Observation_{parking_id}"
        observation = URIRef(f"http://tamu.edu/ontologies/tamu_ont#{observation_id}")
        g.add((observation, RDF.type, SOSA.Observation))

        g.add((observation, SOSA.madeBySensor, sensor))
        g.add((observation, SOSA.hasFeatureOfInterest, parking_instance))
        g.add((observation, SOSA.observedProperty, occupancy_property))

        # simulating the occupancy
        occupancy_value = random.randint(0, 100)
        g.add((observation, SOSA.hasSimpleResult, Literal(occupancy_value, datatype=XSD.integer)))

        # time
        timestamp = datetime.now().isoformat()
        g.add((observation, SOSA.resultTime, Literal(timestamp, datatype=XSD.dateTime)))

        print(f"Added observation for {parking_id}: Occupancy = {occupancy_value}% at {timestamp}")

    # building nearby parking lot
    for _, building in combined_buildings_gdf.iterrows():
        building_point = building['geometry']
        building_instance = building_instances[building['OBJECTID']]

        for _, parking in parking_gdf.iterrows():
            parking_point = parking['geometry']
            parking_instance = parking_instances[parking['OBJECTID']]

            # 300 meters
            distance = building_point.distance(parking_point)

            if distance <= 300:
                g.add((building_instance, TAMU_ONTO.nearby, parking_instance))
                print(f"Added nearby relation between Building {building['OBJECTID']} and ParkingLot {parking['OBJECTID']} with distance: {distance} meters")

    # save to owl
    output_owl_path = './rdf_data/tamu_ont.owl'

    # Create the directory if it doesn't exist
    os.makedirs(os.path.dirname(output_owl_path), exist_ok=True)

    # Save to OWL
    with open(output_owl_path, 'wb') as f:
        f.write(g.serialize(format='xml', encoding='utf-8'))

    print(f'Ontology has been created and saved as "{output_owl_path}".')


