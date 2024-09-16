import sys
import os

# Adjust the path to import modules from the 'scripts' directory
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))

# Import scripts from the 'scripts' directory
from scripts import data_acquisition
from scripts import data_processing
from scripts import knowledge_graph_building
from scripts import knowledge_graph_updating

# Main
if __name__ == '__main__':
    print("Starting data acquisition...")
    data_acquisition.main()
    print("Data acquisition completed.")

    print("Starting data processing...")
    data_processing.process_geojson_files()
    print("Data processing completed.")

    print("Building knowledge graph...")
    knowledge_graph_building.process_geojson_and_create_ontology()
    print("Knowledge graph created.")

    print("Starting knowledge graph updating...")
    update_interval_minutes = 5  # Set the interval for updates in minutes
    knowledge_graph_updating.schedule_updates(update_interval_minutes)