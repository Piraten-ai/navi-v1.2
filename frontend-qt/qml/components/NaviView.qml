import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Item {
    id: root
    property var theme
    property var aadsClient

    ColumnLayout {
        anchors.fill: parent
        spacing: 12

        Label {
            text: "Navi"
            color: theme.text
            font.pixelSize: 24
            font.bold: true
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            radius: theme.radiusMd
            color: theme.panelSoft
            border.color: theme.grid
            border.width: 1

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 16
                spacing: 12

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 12
                    Label {
                        text: "Navi Channel"
                        color: theme.text
                        font.pixelSize: 18
                        font.bold: true
                    }
                    Rectangle {
                        width: 90
                        height: 20
                        radius: 10
                        color: aadsClient.naviStatus === "ready" ? theme.accent : theme.warn
                        Label {
                            anchors.centerIn: parent
                            text: aadsClient.naviStatus === "" ? "unknown" : aadsClient.naviStatus
                            color: theme.bg
                            font.pixelSize: 10
                        }
                    }
                    Item { Layout.fillWidth: true }
                    Button {
                        text: "Clear"
                        onClicked: aadsClient.clearNaviHistory()
                    }
                }

                ListView {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    clip: true
                    model: aadsClient.naviHistory
                    spacing: 10
                    delegate: ColumnLayout {
                        width: ListView.view ? ListView.view.width : 0
                        spacing: 4
                        Label {
                            text: (modelData.role || "navi").toUpperCase()
                            color: theme.muted
                            font.pixelSize: 10
                        }
                        Text {
                            text: modelData.content || ""
                            color: theme.text
                            font.pixelSize: 14
                            wrapMode: Text.Wrap
                            width: ListView.view ? ListView.view.width : 0
                        }
                    }
                }

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 8
                    TextField {
                        id: naviInput
                        Layout.fillWidth: true
                        placeholderText: "Type your message..."
                        onEditingFinished: {
                            if (text.trim().length > 0) {
                                aadsClient.sendNaviMessage(text);
                                text = "";
                            }
                        }
                    }
                    Button {
                        text: aadsClient.naviSending ? "..." : "Send"
                        enabled: !aadsClient.naviSending
                        onClicked: {
                            if (naviInput.text.trim().length > 0) {
                                aadsClient.sendNaviMessage(naviInput.text);
                                naviInput.text = "";
                            }
                        }
                    }
                }
            }
        }
    }
}
