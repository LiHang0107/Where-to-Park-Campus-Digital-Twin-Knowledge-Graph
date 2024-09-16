import sys
import os

# Adjust the path to import ontology_updater
sys.path.append(os.path.join(os.path.dirname(__file__), '../scripts'))

import data_acquisition
import data_processing
import knowledge_graph_building
import knowledge_graph_updating  # Import the ontology_updater script

# Main
if __name__ == '__main__':
    # print("Starting data acquisition...")
    # data_acquisition.main()
    # print("Data acquisition completed.")
    #
    # print("Starting data processing...")
    # data_processing.process_geojson_files()
    # print("Data processing completed.")
    #
    print("Building knowledge graph...")
    knowledge_graph_building.process_geojson_and_create_ontology()
    print("Knowledge graph created.")

    print("Starting knowledge graph updating...")
    update_interval_minutes = 5  # Set the interval for updates in minutes
    knowledge_graph_updating.schedule_updates(update_interval_minutes)