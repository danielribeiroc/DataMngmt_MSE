import pandas as pd
from neo4j import GraphDatabase


class GenerateTrainNetwork:

    def __init__(self, uri):
        self.driver = GraphDatabase.driver(uri)

    def close(self):
        self.driver.close()

    def create_cities(self):
        cities = pd.read_csv('data/cities.csv', sep=';')
        for index, row in cities.iterrows():
            with self.driver.session() as session:
                session.execute_write(
                    self._create_city,
                    row['name'],
                    row['latitude'],
                    row['longitude'],
                    row['population']
                )

    @staticmethod
    def _create_city(tx, name, latitude, longitude, population):
        query = (
            """
            CREATE (c:City { name: $name, latitude: $latitude, longitude: $longitude, population: $population })
            RETURN c
            """
        )
        result = tx.run(query, name=name, latitude=latitude, longitude=longitude, population=population)
        city_created = result.single()['c']
        print("Created City: {name}".format(name=city_created['name']))

    def create_railway_lines(self):
        lines = pd.read_csv('data/lines.csv', sep=';')
        for index, row in lines.iterrows():
            with self.driver.session() as session:
                session.execute_write(
                    self._create_railway_line,
                    row['city1'],
                    row['city2'],
                    row['km'],
                    row['time'],
                    row['nbTracks']
                )

    @staticmethod
    def _create_railway_line(tx, city1, city2, km, time, nbTracks):
        query = (
            """
            MATCH (c1:City {name: $city1}), (c2:City {name: $city2})
            CREATE (c1)-[:RAILWAY {km: $km, time: $time, nbTracks: $nbTracks}]->(c2)
            RETURN c1, c2
            """
        )
        result = tx.run(query, city1=city1, city2=city2, km=km, time=time, nbTracks=nbTracks)
        print(f"Created Railway Line from {city1} to {city2}")


if __name__ == "__main__":
    uri = "neo4j://localhost:7687"
    generate_train_network = GenerateTrainNetwork(uri)

    # create all city nodes
    generate_train_network.create_cities()

    # create all railway lines
    generate_train_network.create_railway_lines()
