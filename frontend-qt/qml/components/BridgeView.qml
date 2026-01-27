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
            text: "Analog Bridge"
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
                spacing: 10

                Label {
                    text: "Bridge Signals"
                    color: theme.muted
                    font.pixelSize: 16
                }

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 12
                    Label {
                        text: "Source: " + (aadsClient.bridgeSource === "" ? "unknown" : aadsClient.bridgeSource)
                        color: theme.text
                        font.pixelSize: 12
                    }
                    Label {
                        text: "Timestamp: " + (aadsClient.bridgeTimestamp === "" ? "none" : aadsClient.bridgeTimestamp)
                        color: theme.muted
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
                            radius: theme.radiusSm
                            color: "#0b131b"
                            border.color: theme.grid
                            border.width: 1
                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: 8
                                spacing: 2
                                Label {
                                    text: modelData.name
                                    color: theme.muted
                                    font.pixelSize: 11
                                }
                                Label {
                                    text: modelData.value
                                    color: theme.text
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
                    radius: theme.radiusSm
                    color: "#0b131b"
                    border.color: theme.grid
                    border.width: 1

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 12
                        spacing: 6
                        Label {
                            text: "Latest WS message"
                            color: theme.muted
                            font.pixelSize: 12
                        }
                        TextArea {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            readOnly: true
                            wrapMode: Text.Wrap
                            text: aadsClient.lastWsMessage
                            font.pixelSize: 12
                            color: theme.text
                        }
                    }
                }
            }
        }
    }
}
