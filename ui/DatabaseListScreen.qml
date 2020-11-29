import QtQuick 2.0
import QtQuick.Controls 2.15

Item {
    id: databaseListScreen
    width: 1280
    height: 720

    Row {
        spacing: 30
        anchors.horizontalCenter: parent.horizontalCenter
        Column {
            id: tableNamesColumn
            spacing: 20
            anchors.bottom: parent.bottom
            Text {
                id: tableNamesText
                anchors.horizontalCenter: parent.horizontalCenter
                font.pixelSize: 25
                font.letterSpacing: 2
                text: qsTr("Table names")
            }
            Rectangle {
                id: tableViewRec
                width: databaseListScreen.width / 4
                height: databaseListScreen.height - 100
                color: "transparent"
                border.width: 2
                border.color: "black"

                ListView {
                    id: dbTablesListView
                    anchors.fill: parent
                    currentIndex: -1
                    model: table_model
                    delegate: ItemDelegate {
                        id: tableNameTxt
                        text: model.display
                        font.pointSize: 20
                        highlighted: ListView.isCurrentItem
                        onClicked: {
                            dbTablesListView.currentIndex = index
                            dbOperations.get_column_infos(model.display)
                            dbOperations.get_foreign_key_infos(model.display)
                        }
                    }
                }
            }
        }
        Column {
            id: columnNamesColumn
            spacing: 20
            anchors.bottom: parent.bottom
            Text {
                id: columnNamesText
                anchors.horizontalCenter: parent.horizontalCenter
                font.pixelSize: 25
                font.letterSpacing: 2
                text: qsTr("Column names & types")
            }
            Rectangle {
                width: databaseListScreen.width / 3
                height: databaseListScreen.height - 100
                color: "transparent"
                border.width: 2
                border.color: "black"

                ListView {
                    id: dbColumnsListView
                    anchors.fill: parent
                    model: column_model
                    delegate: Text {
                        id: columnNameTxt
                        width: dbColumnsListView.width - 20
                        verticalAlignment: Text.AlignVCenter
                        height: 30
                        x: 10
                        text: model.display
                        font.pointSize: 15
                    }
                }
            }
        }
        Column {
            id: foreignKeysColumn
            spacing: 20
            anchors.bottom: parent.bottom
            Text {
                id: foreignKeysText
                anchors.horizontalCenter: parent.horizontalCenter
                font.pixelSize: 25
                font.letterSpacing: 2
                text: qsTr("Foreign keys")
            }
            Rectangle {
                width: databaseListScreen.width / 3
                height: databaseListScreen.height - 100
                color: "transparent"
                border.width: 2
                border.color: "black"

                ListView {
                    id: dbForeignKeysListView
                    anchors.fill: parent
                    model: foreign_key_model
                    delegate: Text {
                        id: foreignKeyTxt
                        width: dbForeignKeysListView.width - 20
                        verticalAlignment: Text.AlignVCenter
                        height: 30
                        x: 10
                        text: model.display
                        font.pointSize: 15
                    }
                }
            }
        }
    }
}
