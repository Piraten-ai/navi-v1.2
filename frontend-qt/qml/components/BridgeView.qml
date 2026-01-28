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

        // Header
        RowLayout {
            Layout.fillWidth: true
            spacing: 12

            Text {
                text: qsTr("ANALOG BRIDGE")
                color: Theme.accent
                font.pixelSize: 18
                font.bold: true
                font.family: Theme.fontDisplay
                font.letterSpacing: 2
            }

            Item { Layout.fillWidth: true }

            // Connection status
            Rectangle {
                width: statusRow.width + 16
                height: 24
                radius: 12
                color: aadsClient && aadsClient.wsConnected
                       ? Qt.rgba(Theme.success.r, Theme.success.g, Theme.success.b, 0.2)
                       : Qt.rgba(Theme.danger.r, Theme.danger.g, Theme.danger.b, 0.2)
                border.color: aadsClient && aadsClient.wsConnected ? Theme.success : Theme.danger
                border.width: 1

                Row {
                    id: statusRow
                    anchors.centerIn: parent
                    spacing: 6

                    Rectangle {
                        width: 8
                        height: 8
                        radius: 4
                        color: aadsClient && aadsClient.wsConnected ? Theme.success : Theme.danger
                        anchors.verticalCenter: parent.verticalCenter

                        SequentialAnimation on opacity {
                            running: aadsClient && aadsClient.wsConnected
                            loops: Animation.Infinite
                            NumberAnimation { from: 1.0; to: 0.4; duration: 1000 }
                            NumberAnimation { from: 0.4; to: 1.0; duration: 1000 }
                        }
                    }

                    Text {
                        text: aadsClient && aadsClient.wsConnected ? qsTr("CONNECTED") : qsTr("DISCONNECTED")
                        color: aadsClient && aadsClient.wsConnected ? Theme.success : Theme.danger
                        font.pixelSize: 9
                        font.family: Theme.fontMono
                        font.bold: true
                    }
                }
            }
        }

        // Main content area
        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 12

            // Left column - Bridge Signals
            Rectangle {
                Layout.preferredWidth: parent.width * 0.45
                Layout.fillHeight: true
                radius: Theme.radiusMd
                color: Qt.rgba(Theme.panel.r, Theme.panel.g, Theme.panel.b, 0.5)
                border.color: Theme.panelEdge
                border.width: 1

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 16
                    spacing: 12

                    // Section header
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 8

                        Text {
                            text: qsTr("BRIDGE SIGNALS")
                            color: Theme.muted
                            font.pixelSize: 10
                            font.family: Theme.fontMono
                            font.bold: true
                            font.letterSpacing: 1
                        }

                        Item { Layout.fillWidth: true }

                        Text {
                            text: aadsClient && aadsClient.bridgeSignals ? aadsClient.bridgeSignals.length + qsTr(" signals") : qsTr("0 signals")
                            color: Theme.accent
                            font.pixelSize: 9
                            font.family: Theme.fontMono
                        }
                    }

                    // Source/Timestamp info
                    Rectangle {
                        Layout.fillWidth: true
                        height: 32
                        radius: Theme.radiusSm
                        color: Qt.rgba(Theme.bg.r, Theme.bg.g, Theme.bg.b, 0.4)

                        RowLayout {
                            anchors.fill: parent
                            anchors.margins: 8
                            spacing: 16

                            Text {
                                text: qsTr("SRC: ") + (aadsClient && aadsClient.bridgeSource !== "" ? aadsClient.bridgeSource : qsTr("--"))
                                color: Theme.textMain
                                font.pixelSize: 10
                                font.family: Theme.fontMono
                            }

                            Text {
                                text: qsTr("TS: ") + (aadsClient && aadsClient.bridgeTimestamp !== "" ? aadsClient.bridgeTimestamp : qsTr("--"))
                                color: Theme.muted
                                font.pixelSize: 10
                                font.family: Theme.fontMono
                            }
                        }
                    }

                    // Signals grid
                    ScrollView {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        clip: true

                        Flow {
                            width: parent.width
                            spacing: 8

                            Repeater {
                                model: aadsClient ? aadsClient.bridgeSignals : []

                                delegate: Rectangle {
                                    width: 160
                                    height: 60
                                    radius: Theme.radiusSm
                                    color: Qt.rgba(Theme.panelSoft.r, Theme.panelSoft.g, Theme.panelSoft.b, 0.6)
                                    border.color: Theme.panelEdge
                                    border.width: 1

                                    // Gradient overlay
                                    Rectangle {
                                        anchors.fill: parent
                                        radius: parent.radius
                                        gradient: Gradient {
                                            GradientStop { position: 0.0; color: Qt.rgba(Theme.accent.r, Theme.accent.g, Theme.accent.b, 0.05) }
                                            GradientStop { position: 1.0; color: "transparent" }
                                        }
                                    }

                                    ColumnLayout {
                                        anchors.fill: parent
                                        anchors.margins: 10
                                        spacing: 4

                                        Text {
                                            text: modelData.name || qsTr("UNKNOWN")
                                            color: Theme.muted
                                            font.pixelSize: 9
                                            font.family: Theme.fontMono
                                            font.bold: true
                                            elide: Text.ElideRight
                                            Layout.fillWidth: true
                                        }

                                        Text {
                                            text: modelData.value !== undefined ? String(modelData.value) : qsTr("--")
                                            color: Theme.accent
                                            font.pixelSize: 18
                                            font.bold: true
                                            font.family: Theme.fontMono
                                        }
                                    }
                                }
                            }
                        }
                    }

                    // Empty state
                    Item {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        visible: !aadsClient || !aadsClient.bridgeSignals || aadsClient.bridgeSignals.length === 0

                        Column {
                            anchors.centerIn: parent
                            spacing: 8

                            Text {
                                text: qsTr("NO SIGNALS")
                                color: Theme.muted
                                font.pixelSize: 14
                                font.family: Theme.fontDisplay
                                font.bold: true
                                anchors.horizontalCenter: parent.horizontalCenter
                            }

                            Text {
                                text: qsTr("Waiting for Arduino bridge data...")
                                color: Qt.rgba(Theme.muted.r, Theme.muted.g, Theme.muted.b, 0.6)
                                font.pixelSize: 10
                                font.family: Theme.fontBody
                                anchors.horizontalCenter: parent.horizontalCenter
                            }
                        }
                    }
                }
            }

            // Right column - WebSocket messages
            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                radius: Theme.radiusMd
                color: Qt.rgba(Theme.panel.r, Theme.panel.g, Theme.panel.b, 0.5)
                border.color: Theme.panelEdge
                border.width: 1

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 16
                    spacing: 12

                    // Section header
                    Text {
                        text: qsTr("WEBSOCKET FEED")
                        color: Theme.muted
                        font.pixelSize: 10
                        font.family: Theme.fontMono
                        font.bold: true
                        font.letterSpacing: 1
                    }

                    // Message display
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        radius: Theme.radiusSm
                        color: Qt.rgba(Theme.bg.r, Theme.bg.g, Theme.bg.b, 0.5)
                        border.color: Theme.panelEdge
                        border.width: 1

                        ScrollView {
                            anchors.fill: parent
                            anchors.margins: 12
                            clip: true

                            TextArea {
                                id: wsMessageArea
                                readOnly: true
                                wrapMode: Text.Wrap
                                text: aadsClient ? aadsClient.lastWsMessage : ""
                                color: Theme.textMain
                                font.pixelSize: 11
                                font.family: Theme.fontMono
                                selectByMouse: true
                                selectionColor: Qt.rgba(Theme.accent.r, Theme.accent.g, Theme.accent.b, 0.3)

                                background: Rectangle {
                                    color: "transparent"
                                }
                            }
                        }

                        // Empty state overlay
                        Item {
                            anchors.fill: parent
                            visible: !aadsClient || !aadsClient.lastWsMessage || aadsClient.lastWsMessage === ""

                            Column {
                                anchors.centerIn: parent
                                spacing: 6

                                Text {
                                    text: qsTr("NO MESSAGES")
                                    color: Theme.muted
                                    font.pixelSize: 12
                                    font.family: Theme.fontDisplay
                                    font.bold: true
                                    anchors.horizontalCenter: parent.horizontalCenter
                                }

                                Text {
                                    text: qsTr("WebSocket messages will appear here")
                                    color: Qt.rgba(Theme.muted.r, Theme.muted.g, Theme.muted.b, 0.6)
                                    font.pixelSize: 9
                                    font.family: Theme.fontBody
                                    anchors.horizontalCenter: parent.horizontalCenter
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
