import QtQuick 2.13
import QtQuick.Window 2.13
import QtQuick.Layouts 1.15

import Authentication 1.0

import "ui"

Window {
    width: 1280
    height: 720
    visible: true
    color: "#8c7f69"
    title: qsTr("Database operations")

    Authentication {
        id: authentication
    }

    StackLayout {
        id: slMain
        anchors.fill: parent
        currentIndex: 0
        LoginScreen {
            id: loginScreen
            width: 400
            height: 300
        }
        DatabaseListScreen {
            id: databaseListScreen
        }
    }

}
