from neo4j import GraphDatabase


class Neo4jOperations:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.session = self.driver.session()

    def close(self):
        self.driver.close()

    def check_node(self, name, nodeType):
        query = """
            MATCH (a:%s {name: '%s'})
            RETURN (COUNT(a))
            """ % (nodeType, name)
        results = self.session.run(query)

        for result in results:
            count = result[0]

        if count == 0:
            return True  # node does not exist
        else:
            return False  # node exists

    def check_column_node(self, name, tableName, type):
        query = """
            MATCH (a:Column {name: '%s', table: '%s', type: '%s'})
            RETURN (COUNT(a))
            """ % (name, tableName, type)
        results = self.session.run(query)

        for result in results:
            count = result[0]

        if count == 0:
            return True  # node does not exist
        else:
            return False  # node exists

    def create_node(self, name, nodeType):
        if self.check_node(name, nodeType):
            query = """
                    MERGE (a:%s {name: '%s'})
                    """ % (nodeType, name)
            self.session.run(query)
            return True
        else:
            print("Node is already existent")
            return False

    def create_column_node(self, name, tableName, type):
        if self.check_column_node(name, tableName, type):
            query = """
                    MERGE (a:Column {name: '%s', table: '%s', type: '%s'})
                    """ % (name, tableName, type)
            self.session.run(query)
            return True
        else:
            print("Node is already existent")
            return False

    def create_relationship(self, fromName, fromNodeType, toName, toNodeType, relationName):
        query = """
                MATCH (a:%s), (b:%s)
                WHERE a.name='%s' AND b.name='%s'
                MERGE  (a)-[:%s]->(b)
                """ % (fromNodeType, toNodeType, fromName, toName, relationName)
        self.session.run(query)

    def create_relationship_table_to_column(self, fromName, fromNodeType, toName, toTableName, relationName):
        query = """
                MATCH (a:%s), (b:Column)
                WHERE a.name='%s' AND b.name='%s' AND b.table='%s'
                MERGE  (a)-[:%s]->(b)
                """ % (fromNodeType, fromName, toName, toTableName, relationName)
        self.session.run(query)

    def create_relationship_column_to_column_fk(self, fromName, fromTableName, toName, toTableName, relationName):
        query = """
                MATCH (a:Column), (b:Column)
                WHERE a.name='%s' AND a.table='%s' AND b.name='%s' AND b.table='%s'
                MERGE  (a)-[:%s]->(b)
                """ % (fromName, fromTableName, toName, toTableName, relationName)
        self.session.run(query)
