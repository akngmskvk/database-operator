# This Python file uses the following encoding: utf-8
import sys
import os
import sqlite3
from sqlite3 import Error

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtQml import *

from neo4joperations import *


class Authentication(QObject):
    def __init__(self):
        QObject.__init__(self)
        self._isAuth = False

    adminUsername = str("admin")
    adminPassword = str("admin")

    def setAuth(self, value):
        self._isAuth = value

    @Slot(result=bool)
    def isAuth(self):
        return self._isAuth

    @Slot(str, str)
    def authenticate(self, username, password):
        if (username == self.adminUsername) and (password == self.adminPassword):
            isAuth = True
        else:
            isAuth = False
        self.setAuth(isAuth)


class DatabaseOperations(QObject):
    def __init__(self, databaseName):
        QObject.__init__(self)
        self.databaseName = databaseName
        self.conn = self.create_connection(self.databaseName)

    def create_connection(self, db_file):
        """ create a database connection to the SQLite database
            specified by the db_file
        :param db_file: database file
        :return: Connection object or None
        """
        conn = None
        try:
            conn = sqlite3.connect(db_file)
        except Error as e:
            print(e)

        return conn

    def select_all_table_names(self):
        cur = self.conn.cursor()
        cur.execute(""" SELECT name FROM sqlite_master WHERE type IN ('table') AND name NOT LIKE 'sqlite_%' """)

        rows = cur.fetchall()

        return rows

    def show_all_table_names(self):
        rows = self.select_all_table_names()

        for row in rows:
            name = self.remove_unwanted_characters(row)
            table_names_list.append(name)

    def select_all_column_names_and_types(self, tableName):
        cur = self.conn.cursor()
        cur.execute(""" PRAGMA table_info(%s) """ % tableName)

        rows = cur.fetchall()

        return rows

    def show_all_column_names_and_types(self, tableName):
        rows = self.select_all_column_names_and_types(tableName)

        column_names_list.clear()
        for row in rows:
            column_name_and_type = str(row[1]) + " - " + str(row[2])
            column_names_list.append(column_name_and_type)
        column_model.setStringList(column_names_list)

    def select_all_foreign_keys(self, tableName):
        cur = self.conn.cursor()
        cur.execute(""" PRAGMA foreign_key_list(%s) """ % tableName)

        rows = cur.fetchall()

        return rows

    def show_all_foreign_keys(self, tableName):
        rows = self.select_all_foreign_keys(tableName)

        foreign_key_names_list.clear()
        for row in rows:
            foreign_key_name = str(row[2] + " : " + str(row[3]) + " -> " + str(row[4]))
            foreign_key_names_list.append(foreign_key_name)
        foreign_key_model.setStringList(foreign_key_names_list)

    def remove_unwanted_characters(self, text):
        unwanted_characters = ["'", "(", ")", ","]
        for character in unwanted_characters:
            text = str(text).replace(character, "")
        return text

    @Slot(str)
    def get_column_infos(self, tableName):
        self.show_all_column_names_and_types(tableName)

    @Slot(str)
    def get_foreign_key_infos(self, tableName):
        self.show_all_foreign_keys(tableName)


table_names_list = []
column_names_list = []
foreign_key_names_list = []

database = r"chinook.db"
dbOperations = DatabaseOperations(database)

dbOperations.show_all_table_names()

table_model = QStringListModel()
table_model.setStringList(table_names_list)
column_model = QStringListModel()
foreign_key_model = QStringListModel()


# convert Chinook RDBMS to DMMM in Neo4j
# Beginning of Neo4j operations
neo4j = Neo4jOperations("bolt://localhost:7687", "neo4j", "123456")

neo4j.create_node("Chinook", "DATA_MODEL")

for entity_name in table_names_list:
    # create entity to neo4j
    neo4j.create_node(entity_name, "ENTITY")
    # create relationship between data model and entity
    neo4j.create_relationship("Chinook", "DATA_MODEL", entity_name, "ENTITY", "HAS_ENTITY")

for entity_name in table_names_list:
    rows = dbOperations.select_all_column_names_and_types(entity_name)
    for row in rows:
        attribute_name = str(row[1])
        attribute_type = str(row[2])
        is_attribute_pk = int(row[5])

        # create attribute with attr type and its related entity
        neo4j.create_attribute_node(attribute_name, attribute_type, entity_name)
        # create relationship between entity and its attribute
        query = """
                MATCH (a:ENTITY), (b:ATTRIBUTE)
                WHERE a.name='%s' AND b.entity='%s'
                MERGE  (a)-[:%s]->(b)
                """ % (entity_name, entity_name, "HAS_ATTRIBUTE")
        neo4j.run_custom_query(query)

        if is_attribute_pk:
            # create key attribute with its related entity
            neo4j.create_key_attribute_node(attribute_name, entity_name)
            # create relationship between attribute and key attribute
            query = """
                    MATCH (a:KEY_ATTRIBUTE), (b:ATTRIBUTE)
                    WHERE a.name=b.name AND a.entity=b.entity
                    MERGE  (a)-[:IS_AN]->(b)
                    """
            neo4j.run_custom_query(query)

    # find foreign identifier attributes
    rows = dbOperations.select_all_foreign_keys(entity_name)
    for row in rows:
        from_entity = entity_name
        to_entity = str(row[2])
        from_attribute = str(row[3])
        to_attribute = str(row[4])

        # create foreign identifier attribute with from-to entity name and from-to attr name
        neo4j.create_fia_node(from_attribute, from_entity, to_entity, from_attribute, to_attribute)
        # create relationship between attribute and foreign identifier attribute
        query = """
                MATCH (a:ATTRIBUTE), (b:FOREIGN_IDENTIFIER_ATTRIBUTE)
                WHERE a.name=b.name AND a.entity=b.from_entity
                MERGE  (a)-[:DEFINES_FOREIGN_KEY]->(b)
                """
        neo4j.run_custom_query(query)

neo4j.close()
# End of Neo4j operations


def create_dmmm_outline():
    neo4j = Neo4jOperations("bolt://localhost:7687", "neo4j", "123456")

    neo4j.create_node("DATA MODEL", "DATA_MODEL")
    neo4j.create_node("DATA MODEL ENTITY", "DATA_MODEL_ENTITY")
    neo4j.create_relationship("DATA MODEL", "DATA_MODEL", "DATA MODEL ENTITY", "DATA_MODEL_ENTITY",
                              "DefinesBusinessContextFor")
    neo4j.create_node("ENTITY", "ENTITY")
    neo4j.create_relationship("ENTITY", "ENTITY", "DATA MODEL ENTITY", "DATA_MODEL_ENTITY", "HasItsBusinessContext")
    neo4j.create_node("RELATIONSHIP", "RELATIONSHIP")
    neo4j.create_relationship("ENTITY", "ENTITY", "RELATIONSHIP", "RELATIONSHIP", "RepresentsDominantEnd")
    neo4j.create_relationship("ENTITY", "ENTITY", "RELATIONSHIP", "RELATIONSHIP", "RepresentsDependentEnd")
    neo4j.create_node("ATTRIBUTE", "ATTRIBUTE")
    neo4j.create_relationship("ENTITY", "ENTITY", "ATTRIBUTE", "ATTRIBUTE", "HasItsProperties")
    neo4j.create_node("FOREIGN IDENTIFIER", "FOREIGN_IDENTIFIER")
    neo4j.create_relationship("ATTRIBUTE", "ATTRIBUTE", "FOREIGN IDENTIFIER", "FOREIGN_IDENTIFIER", "ContributesTo")
    neo4j.create_relationship("FOREIGN IDENTIFIER", "FOREIGN_IDENTIFIER", "RELATIONSHIP", "RELATIONSHIP",
                              "ProvidesThePath")
    neo4j.create_node("FOREIGN IDENTIFIER ATTRIBUTE", "FOREIGN_IDENTIFIER_ATTRIBUTE")
    neo4j.create_relationship("FOREIGN IDENTIFIER", "FOREIGN_IDENTIFIER", "FOREIGN IDENTIFIER ATTRIBUTE",
                              "FOREIGN_IDENTIFIER_ATTRIBUTE", "IsMadeUpOf")
    neo4j.create_relationship("ATTRIBUTE", "ATTRIBUTE", "FOREIGN IDENTIFIER ATTRIBUTE",
                              "FOREIGN_IDENTIFIER_ATTRIBUTE", "DefinesForeignKeyRoleOf")
    neo4j.create_node("DOMAIN", "DOMAIN")
    neo4j.create_relationship("ATTRIBUTE", "ATTRIBUTE", "DOMAIN", "DOMAIN", "ConstrainsTheValuesOf")
    neo4j.create_relationship("DOMAIN", "DOMAIN", "ATTRIBUTE", "ATTRIBUTE", "HasTheSetOf")
    neo4j.create_node("ATTRIBUTE TYPE", "ATTRIBUTE_TYPE")
    neo4j.create_relationship("ATTRIBUTE TYPE", "ATTRIBUTE_TYPE", "DOMAIN", "DOMAIN", "ConstrainsTheGenericNatureOf")
    neo4j.create_relationship("ATTRIBUTE TYPE", "ATTRIBUTE_TYPE", "ATTRIBUTE", "ATTRIBUTE",
                              "ConstrainsTheGenericNatureOf")
    neo4j.create_node("IDENTIFIER", "IDENTIFIER")
    neo4j.create_relationship("ATTRIBUTE", "ATTRIBUTE", "IDENTIFIER", "IDENTIFIER", "FormsTheComponent")
    neo4j.create_relationship("ENTITY", "ENTITY", "IDENTIFIER", "IDENTIFIER", "IdentifiedBy")
    neo4j.create_node("KEY ATTRIBUTE", "KEY_ATTRIBUTE")
    neo4j.create_relationship("KEY ATTRIBUTE", "KEY_ATTRIBUTE", "ATTRIBUTE", "ATTRIBUTE", "IsAn")
    neo4j.create_relationship("IDENTIFIER", "IDENTIFIER", "KEY ATTRIBUTE", "KEY_ATTRIBUTE", "IsComposedOf")

    neo4j.close()


# create dmmm outline of chinook database
# create_dmmm_outline()


if __name__ == "__main__":
    app = QGuiApplication(sys.argv)
    qmlRegisterType(Authentication, 'Authentication', 1, 0, 'Authentication')
    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("table_model", table_model)
    engine.rootContext().setContextProperty("column_model", column_model)
    engine.rootContext().setContextProperty("foreign_key_model", foreign_key_model)
    engine.rootContext().setContextProperty("dbOperations", dbOperations)
    engine.load(os.path.join(os.path.dirname(__file__), "main.qml"))

    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec_())
