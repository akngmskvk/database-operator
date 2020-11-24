import QtQuick 2.13
import QtQuick.Window 2.13

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

    LoginScreen {
        width: 400
        height: 300
        anchors.centerIn: parent
    }

}
