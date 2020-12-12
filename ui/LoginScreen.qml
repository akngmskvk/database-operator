import QtQuick 2.0
import QtQuick.Controls 2.15
import QtQuick.Controls.Styles 1.4

Item {
    id: loginScreen

    property bool isAuth: false

    onIsAuthChanged: {
        if (isAuth)
            slMain.currentIndex = 1
    }

    Rectangle {
        id: background
        color: "#8c7f69"
        anchors.fill: parent
    }

    Column {
        anchors.centerIn: parent
        spacing: 20
        Text {
            id: loginText
            anchors.horizontalCenter: parent.horizontalCenter
            font.pixelSize: 30
            font.letterSpacing: 2
            text: qsTr("Login")
        }
        TextField {
            id: usernameInput
            width: 200
            height: 40
            placeholderText: "Username(hint: admin)"
        }
        TextField {
            id: passwordInput
            echoMode: TextInput.Password
            width: 200
            height: 40
            placeholderText: "Password(hint: admin)"
        }
        Button {
            id: loginBtn
            opacity: enabled ? 1 : 0.7
            enabled: usernameInput.text && passwordInput.text
            anchors.horizontalCenter: parent.horizontalCenter
            width: 100
            height: 50
            text: "Login"
            onClicked: {
                authentication.authenticate(usernameInput.text, passwordInput.text)
                isAuth = authentication.isAuth()
                if (loginScreen.isAuth == false)
                    failedTxt.visible = true
            }
        }
        Text {
            id: failedTxt
            visible: false
            text: qsTr("Login attempt failed!")
            color: "red"
            anchors.horizontalCenter: parent.horizontalCenter
            font.pixelSize: 20
        }
    }
}
