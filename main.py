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

mainNodeName = "chinook_DMM"
mainNodeType = "Database"
tableNodeType = "Table"
columnNodeType = "Column"
dbToTableRelationship = "hasTable"
tableToColumnRelationship = "hasColumn"
columnToColumnForeignKeyRelationship = "FK"

neo4j.create_node(mainNodeName, mainNodeType)

for table_name in table_names_list:
    # add table names to neo4j
    neo4j.create_node(table_name, tableNodeType)
    neo4j.create_relationship(mainNodeName, mainNodeType, table_name, tableNodeType, dbToTableRelationship)

for table_name in table_names_list:
    # add column names and their types to neo4j
    rows = dbOperations.select_all_column_names_and_types(table_name)
    for row in rows:
        column_name = str(row[1])
        column_type = str(row[2])
        neo4j.create_column_node(column_name, table_name, column_type)
        neo4j.create_relationship_table_to_column(table_name, tableNodeType, column_name, table_name,
                                                  tableToColumnRelationship)

for table_name in table_names_list:
    # add foreign key relationship between column names to neo4j
    rows = dbOperations.select_all_foreign_keys(table_name)
    for row in rows:
        from_column_name = str(row[3])
        from_table_name = table_name
        to_column_name = str(row[4])
        to_table_name = str(row[2])

        neo4j.create_relationship_column_to_column_fk(from_column_name, from_table_name, to_column_name,
                                                      to_table_name, columnToColumnForeignKeyRelationship)

neo4j.close()
# End of Neo4j operations

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
