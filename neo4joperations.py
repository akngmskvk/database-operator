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

    def run_custom_query(self, query):
        self.session.run(query)

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

    def create_attribute_node(self, name, attr_type, entity_name):
        query = """
                MERGE (a:ATTRIBUTE {name: '%s', attr_type: '%s', entity: '%s'})
                """ % (name, attr_type, entity_name)
        self.session.run(query)

    def create_key_attribute_node(self, name, entity_name):
        query = """
                MERGE (a:KEY_ATTRIBUTE {name: '%s', entity: '%s'})
                """ % (name, entity_name)
        self.session.run(query)

    def create_fia_node(self, name, from_entity, to_entity, from_attr, to_attr):
        query = """
                MERGE (a:FOREIGN_IDENTIFIER_ATTRIBUTE {name: '%s', from_entity: '%s', to_entity: '%s', from_attr: '%s', 
                to_attr: '%s'})
                """ % (name, from_entity, to_entity, from_attr, to_attr)
        self.session.run(query)

    def create_relationship(self, fromName, fromNodeType, toName, toNodeType, relationName):
        query = """
                MATCH (a:%s), (b:%s)
                WHERE a.name='%s' AND b.name='%s'
                MERGE  (a)-[:%s]->(b)
                """ % (fromNodeType, toNodeType, fromName, toName, relationName)
        self.session.run(query)
