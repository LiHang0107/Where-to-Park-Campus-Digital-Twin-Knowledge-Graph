import os
import random
import sched
import time
from datetime import datetime
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, XSD

# Initialize the scheduler
scheduler = sched.scheduler(time.time, time.sleep)


def update_ontology_occupancy():
    # File paths
    owl_file_path = './rdf_data/tamu_ont.owl'

    # Check if the OWL file exists
    if not os.path.exists(owl_file_path):
        print(f'Error: The file "{owl_file_path}" does not exist.')
        return

    # Namespaces
    TAMU_ONTO = Namespace('http://tamu.edu/ontologies/tamu_ont#')
    SOSA = Namespace('http://www.w3.org/ns/sosa/')
    OWL_TIME = Namespace('http://www.w3.org/2006/time#')

    # Load the existing OWL file
    g = Graph()
    g.parse(owl_file_path, format='xml')

    # Find all occupancy observations in the graph
    for s in g.subjects(RDF.type, SOSA.Observation):
        # Check if this observation is about occupancy
        if (s, SOSA.observedProperty, URIRef(f"http://tamu.edu/ontologies/tamu_ont#OccupancyRate")) in g:
            # Generate a new random occupancy value
            new_occupancy_value = random.randint(0, 100)
            # Get the current time for the observation
            new_timestamp = datetime.now().isoformat()

            # Remove the old occupancy value
            g.remove((s, SOSA.hasSimpleResult, None))
            # Add the new occupancy value
            g.add((s, SOSA.hasSimpleResult, Literal(new_occupancy_value, datatype=XSD.integer)))

            # Update the observation time
            g.remove((s, SOSA.resultTime, None))
            g.add((s, SOSA.resultTime, Literal(new_timestamp, datatype=XSD.dateTime)))

            print(f"Updated {s}: New occupancy = {new_occupancy_value}% at {new_timestamp}")

    # Save the updated ontology to the OWL file
    with open(owl_file_path, 'wb') as f:
        f.write(g.serialize(format='xml', encoding='utf-8'))

    print(f'Ontology has been updated and saved as "{owl_file_path}".')


def schedule_updates(interval_minutes=5):
    # Schedule the first update
    scheduler.enter(interval_minutes * 60, 1, periodic_update, (interval_minutes,))
    print(f'Scheduled the next update in {interval_minutes} minutes.')
    scheduler.run()


def periodic_update(interval_minutes):
    # Run the ontology update
    update_ontology_occupancy()

    # Schedule the next update
    scheduler.enter(interval_minutes * 60, 1, periodic_update, (interval_minutes,))
    print(f'Scheduled the next update in {interval_minutes} minutes.')


if __name__ == '__main__':
    # Set the interval in minutes for updates
    update_interval_minutes = 5
    schedule_updates(update_interval_minutes)