from neo4j import GraphDatabase
import folium


# display city on the folium map
def display_city_on_map(m, popup, latitude, longitude, radius=1000, color="#3186cc"):
    folium.Circle(
        location=(latitude, longitude),
        radius=radius,
        popup=popup,
        color=color,
        fill=True,
        fill_opacity=0.8,
    ).add_to(m)


# display polyline on the folium map
# locations: (list of points (latitude, longitude)) – Latitude and Longitude of line
def display_polyline_on_map(m, locations, popup=None, color="#3186cc", weight=2.0):
    folium.PolyLine(
        locations,
        popup=popup,
        color=color,
        weight=weight,
        opacity=1
    ).add_to(m)


class DisplayTrainNetwork:

    def __init__(self, uri):
        self.driver = GraphDatabase.driver(uri)

    def close(self):
        self.driver.close()

# ---------------------------------------------------------------------------------------------------------------------

    def display_cities(self):
        map_1 = folium.Map(location=center_switzerland, zoom_start=8)
        with self.driver.session() as session:
            session.execute_read(self._display_cities, map_1)
        map_1.save('out/1.html')

    @staticmethod
    def _display_cities(tx, m):
        query = (
            """
            MATCH (c:City)
            RETURN c
            """
        )
        result = tx.run(query)
        for record in result:
            display_city_on_map(
                m=m,
                popup=record['c']['name'],
                latitude=record['c']['latitude'],
                longitude=record['c']['longitude']
            )
# ---------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def _display_railway_lines_2_1(tx, m): # Exo 2_1
        query = (
            """
            MATCH (c1:City)-[r:RAILWAY]->(c2:City)
            RETURN c1.name, c1.latitude, c1.longitude, c2.name, c2.latitude, c2.longitude
            """
        )
        result = tx.run(query)
        for record in result:
            city1_coords = (record['c1.latitude'], record['c1.longitude']) # get coordinates of city 1
            city2_coords = (record['c2.latitude'], record['c2.longitude']) # get coordinates of city 2
            locations = [city1_coords, city2_coords] # regroup both
            popup_text = f"Railway: {record['c1.name']} to {record['c2.name']}" # text to show
            display_polyline_on_map(m=m, locations=locations, popup=popup_text) # draw line in map

    def display_train_network_2_1(self): # Exo 2_1
        map_1 = folium.Map(location=center_switzerland, zoom_start=8)
        with self.driver.session() as session:
            session.execute_read(self._display_cities, map_1)
            session.execute_read(self._display_railway_lines_2_1, map_1)
        map_1.save('out/2.1.html')

# ---------------------------------------------------------------------------------------------------------------------
    def display_cities_2_2(self): # Exo 2_2
        map_1 = folium.Map(location=center_switzerland, zoom_start=8)
        with self.driver.session() as session:
            session.execute_read(self._display_cities, map_1)
            session.execute_read(self._display_railway_lines_2_1, map_1)
            session.execute_read(self._display_highlighted_cities_2_2, map_1)
        map_1.save('out/2.2.html')
    @staticmethod
    def _display_highlighted_cities_2_2(tx, m):
        query = (
            """
            MATCH (luzern:City {name: "Luzern"})-[:RAILWAY*1..4]-(c:City)
            WHERE c.population > 100000
            RETURN c.name, c.latitude, c.longitude
            """
        )
        result = tx.run(query)
        for record in result:
            display_city_on_map(
                m=m,
                popup=record['c.name'],
                latitude=record['c.latitude'],
                longitude=record['c.longitude'],
                color="#ff0000"  # Different color for highlighted cities
            )

# ---------------------------------------------------------------------------------------------------------------------
    def display_shortest_path_km(self):
        map_1 = folium.Map(location=center_switzerland, zoom_start=8)
        with self.driver.session() as session:
            session.execute_read(self._display_cities, map_1)
            session.execute_read(self._display_railway_lines_2_1, map_1)
            session.execute_read(self._display_shortest_path, map_1, 'km')
        map_1.save('out/2.3.1.html')

    def display_shortest_path_minutes(self):
        map_1 = folium.Map(location=center_switzerland, zoom_start=8)
        with self.driver.session() as session:
            session.execute_read(self._display_cities, map_1)
            session.execute_read(self._display_railway_lines_2_1, map_1)
            session.execute_read(self._display_shortest_path, map_1, "time")
        map_1.save('out/2.3.2.html')
    @staticmethod
    def _display_shortest_path(tx, m, criteria): # done in the neo4j console based on this code  https://neo4j.com/docs/graph-data-science/current/algorithms/dijkstra-source-target/#search
        query = (
                """
                MATCH (start:City {name: "Geneve"}), (end:City {name: "Chur"})
                CALL gds.shortestPath.dijkstra.stream({
                    nodeProjection: 'City',
                    relationshipProjection: {
                        RAILWAY: {
                            type: 'RAILWAY',
                            properties: '"""+ criteria +"""',
                        orientation: 'UNDIRECTED'
                    }
                },
                sourceNode: start,
                targetNode: end,
                relationshipWeightProperty: '"""+ criteria +"""'
            })
            YIELD index, sourceNode, targetNode, totalCost, nodeIds, costs, path
            RETURN 
                index,
                gds.util.asNode(sourceNode).name AS sourceNodeName,
                gds.util.asNode(targetNode).name AS targetNodeName,
                totalCost,
                [nodeId IN nodeIds | gds.util.asNode(nodeId).name] AS nodeNames,
                costs,
                nodes(path) as path
            ORDER BY index
            """
        )
        result = tx.run(query)
        locations = []
        for record in result:

            for node in record['path']: # Iterate through each node in the path (path contains each city to go throw)
                locations.append((node['latitude'], node['longitude']))
                display_city_on_map(
                    m=m,
                    popup=node['name'],
                    latitude=node['latitude'],
                    longitude=node['longitude']
                )

        if len(locations) > 1:
            display_polyline_on_map(m=m, locations=locations, color="#ff0000", weight=3.0) # draw lines
# ---------------------------------------------------------------------------------------------------------------------


if __name__ == "__main__":
    display_train_network = DisplayTrainNetwork("neo4j://localhost:7687")

    center_switzerland = [46.800663464, 8.222665776]

    # display cities on the map
    display_train_network.display_cities()
    display_train_network.display_train_network_2_1()
    display_train_network.display_cities_2_2()
    display_train_network.display_shortest_path_km()
    display_train_network.display_shortest_path_minutes()
    display_train_network.close()
