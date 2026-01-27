import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import ".."

Item {
    id: root
    property var aadsClient

    function loadHistory() {
        chatModel.clear();
        var history = aadsClient && aadsClient.naviHistory ? aadsClient.naviHistory : [];
        if (history.length === 0) {
            chatModel.append({sender: qsTr("Navi"), text: qsTr("System online. Local charts loaded."), timestamp: qsTr("00:00")});
            return;
        }
        for (var i = 0; i < history.length; i++) {
            var item = history[i];
            chatModel.append({
                sender: item.role === "user" ? qsTr("User") : qsTr("Navi"),
                text: item.content || "",
                timestamp: item.timestamp || qsTr("--:--")
            });
        }
    }

    Component.onCompleted: loadHistory()

    Connections {
        target: aadsClient
        function onNaviHistoryChanged() {
            loadHistory();
        }
    }

    ListModel {
        id: chatModel
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        ListView {
            id: chatList
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.margins: 16
            spacing: 12
            clip: true
            model: chatModel
            onCountChanged: positionViewAtEnd()

            delegate: Column {
                width: ListView.view.width

                property bool isMe: model.sender === qsTr("User")

                Rectangle {
                    width: Math.min(parent.width * 0.8, textLabel.implicitWidth + 24)
                    height: textLabel.implicitHeight + 16
                    anchors.right: isMe ? parent.right : undefined
                    anchors.left: isMe ? undefined : parent.left

                    color: isMe
                           ? Qt.rgba(Theme.accent.r, Theme.accent.g, Theme.accent.b, 0.15)
                           : Qt.rgba(Theme.panel.r, Theme.panel.g, Theme.panel.b, 0.6)

                    border.color: isMe ? Theme.accent : Theme.panelBorder
                    border.width: 1
                    radius: isMe ? 2 : 12

                    Rectangle {
                        width: 3
                        height: parent.height
                        color: isMe ? Theme.accent : Theme.indicator
                        anchors.right: isMe ? parent.right : undefined
                        anchors.left: isMe ? undefined : parent.left
                        opacity: 0.8
                    }

                    Text {
                        id: textLabel
                        anchors.centerIn: parent
                        text: model.text
                        color: Theme.textMain
                        width: parent.width - 24
                        wrapMode: Text.Wrap
                        font.pixelSize: 14
                        font.family: Theme.fontBody
                    }
                }

                Text {
                    text: model.sender + " - " + model.timestamp
                    color: Theme.textMuted
                    font.pixelSize: 10
                    font.family: Theme.fontMono
                    anchors.right: isMe ? parent.right : undefined
                    anchors.left: isMe ? undefined : parent.left
                    anchors.margins: 4
                }
            }
        }

        Rectangle {
            Layout.fillWidth: true
            height: 60
            color: Theme.panel
            border.color: Theme.panelBorder
            border.width: 1

            RowLayout {
                anchors.fill: parent
                anchors.margins: 12
                spacing: 12

                TextField {
                    id: inputField
                    Layout.fillWidth: true
                    placeholderText: qsTr("Enter command or query...")
                    color: Theme.textMain
                    font.pixelSize: 14
                    font.family: Theme.fontBody
                    background: Rectangle {
                        color: Theme.bg
                        border.color: Theme.panelBorder
                        radius: 4
                    }
                    onAccepted: sendBtn.clicked()
                }

                Button {
                    id: sendBtn
                    text: qsTr("SEND")
                    Layout.preferredWidth: 80
                    background: Rectangle {
                        color: parent.down ? Theme.accent : "transparent"
                        border.color: Theme.accent
                        radius: 4
                    }
                    contentItem: Text {
                        text: parent.text
                        color: parent.down ? Theme.bg : Theme.accent
                        font.bold: true
                        font.family: Theme.fontMono
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                    onClicked: {
                        if (inputField.text === "") return;
                        var now = new Date().toTimeString().slice(0, 5);
                        chatModel.append({sender: qsTr("User"), text: inputField.text, timestamp: now});
                        if (aadsClient && aadsClient.sendNaviMessage) {
                            aadsClient.sendNaviMessage(inputField.text);
                        }
                        inputField.text = "";
                    }
                }
            }
        }
    }
}
