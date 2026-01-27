import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import ".."

Item {
    id: root
    property var aadsClient

    ColumnLayout {
        anchors.fill: parent
        spacing: 12

        Label {
            text: qsTr("Analog Bridge")
            color: Theme.text
            font.pixelSize: 24
            font.bold: true
            font.family: Theme.fontDisplay
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            radius: Theme.radiusMd
            color: Theme.panelSoft
            border.color: Theme.grid
            border.width: 1

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 16
                spacing: 10

                Label {
                    text: qsTr("Bridge Signals")
                    color: Theme.muted
                    font.pixelSize: 16
                    font.family: Theme.fontMono
                }

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 12
                    Label {
                        text: qsTr("Source: %1").arg(aadsClient.bridgeSource === "" ? qsTr("unknown") : aadsClient.bridgeSource)
                        color: Theme.text
                        font.pixelSize: 12
                    }
                    Label {
                        text: qsTr("Timestamp: %1").arg(aadsClient.bridgeTimestamp === "" ? qsTr("none") : aadsClient.bridgeTimestamp)
                        color: Theme.muted
                        font.pixelSize: 12
                    }
                }

                Flow {
                    Layout.fillWidth: true
                    spacing: 8
                    Repeater {
                        model: aadsClient.bridgeSignals
                        delegate: Rectangle {
                            width: 180
                            height: 54
                            radius: Theme.radiusSm
                            color: "#0b131b"
                            border.color: Theme.grid
                            border.width: 1
                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: 8
                                spacing: 2
                                Label {
                                    text: modelData.name
                                    color: Theme.muted
                                    font.pixelSize: 11
                                }
                                Label {
                                    text: modelData.value
                                    color: Theme.text
                                    font.pixelSize: 18
                                    font.bold: true
                                }
                            }
                        }
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    radius: Theme.radiusSm
                    color: "#0b131b"
                    border.color: Theme.grid
                    border.width: 1

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 12
                        spacing: 6
                        Label {
                            text: qsTr("Latest WS message")
                            color: Theme.muted
                            font.pixelSize: 12
                        }
                        TextArea {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            readOnly: true
                            wrapMode: Text.Wrap
                            text: aadsClient.lastWsMessage
                            font.pixelSize: 12
                            color: Theme.text
                        }
                    }
                }
            }
        }
    }
}
