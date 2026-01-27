import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtLocation 6.2
import QtPositioning 6.2

Rectangle {
    id: root
    property var theme
    property string localTileUrl: ""
    property var navCoordinate
    property var trackPath
    property string signalkStatus: ""
    property string nmeaStatus: ""
    property string aadsLogoPath: ""
    property bool showCameraMain: false
    signal cameraViewRequested(bool useCamera)
    property bool showCompass: true
    property var headingText
    property var normalizeDegrees
    property real navHeading: 0
    property string naviStatus: ""
    property var naviPreview
    property var sendNaviMessage

    radius: theme.radiusMd
    color: theme.panelSoft
    border.color: theme.panelEdge
    border.width: 1

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 12
        spacing: 8

        Rectangle {
            Layout.fillWidth: true
            height: 120
            radius: 14
            color: theme.panel
            border.color: theme.panelEdge
            border.width: 1

            RowLayout {
                anchors.fill: parent
                anchors.margins: 10
                spacing: 12

                Rectangle {
                    Layout.preferredWidth: parent.width * 0.22
                    Layout.fillHeight: true
                    radius: 12
                    color: theme.panel
                    border.color: theme.panelEdge
                    border.width: 1

                    Rectangle {
                        anchors.fill: parent
                        anchors.margins: 6
                        radius: 10
                        color: "transparent"
                        border.color: theme.accent
                        border.width: 1
                        opacity: 0.35
                    }

                    Item {
                        anchors.fill: parent
                        anchors.margins: 10

                        Image {
                            anchors.centerIn: parent
                            source: aadsLogoPath
                            fillMode: Image.PreserveAspectFit
                            width: parent.width * 0.7
                            height: parent.height * 0.7
                            smooth: true
                            visible: aadsLogoPath !== ""
                        }

                        Label {
                            anchors.centerIn: parent
                            text: "AADS"
                            color: theme.text
                            font.pixelSize: 16
                            font.bold: true
                            visible: aadsLogoPath === ""
                        }
                    }
                }

                Rectangle {
                    Layout.preferredWidth: parent.width * 0.45
                    Layout.fillHeight: true
                    radius: 12
                    color: theme.panel
                    border.color: theme.panelEdge
                    border.width: 1

                    Rectangle {
                        anchors.fill: parent
                        anchors.margins: 6
                        radius: 10
                        color: "transparent"
                        border.color: theme.accent
                        border.width: 1
                        opacity: 0.35
                    }

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 12
                        spacing: 6
                        Label {
                            text: "VAKTEN FEED"
                            color: theme.muted
                            font.pixelSize: 11
                            font.letterSpacing: 1.1
                        }
                        Label {
                            text: "Camera feed placeholder"
                            color: theme.text
                            font.pixelSize: 12
                        }
                    }
                }

                Rectangle {
                    Layout.preferredWidth: parent.width * 0.30
                    Layout.fillHeight: true
                    radius: 12
                    color: theme.panel
                    border.color: theme.panelEdge
                    border.width: 1

                    Rectangle {
                        anchors.fill: parent
                        anchors.margins: 6
                        radius: 10
                        color: "transparent"
                        border.color: theme.accent
                        border.width: 1
                        opacity: 0.35
                    }

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 12
                        spacing: 6
                        Label {
                            text: "AUTOPILOT"
                            color: theme.muted
                            font.pixelSize: 11
                            font.letterSpacing: 1.1
                        }
                        RowLayout {
                            spacing: 8
                            Label { text: "MODE"; color: theme.muted; font.pixelSize: 10 }
                            Label { text: "HEADING"; color: theme.text; font.pixelSize: 10 }
                        }
                        RowLayout {
                            spacing: 8
                            Label { text: "COURSE"; color: theme.muted; font.pixelSize: 10 }
                            Label { text: "090°"; color: theme.text; font.pixelSize: 10 }
                        }
                        RowLayout {
                            spacing: 8
                            Label { text: "STATUS"; color: theme.muted; font.pixelSize: 10 }
                            Label { text: "ENGAGED"; color: theme.accent; font.pixelSize: 10 }
                        }
                    }
                }
            }
        }

        ColumnLayout {
            Layout.fillWidth: true
            spacing: 6

            RowLayout {
                Layout.fillWidth: true
                spacing: 10
                Label {
                    text: "S-57 ENC (MBTiles)"
                    color: theme.text
                    font.pixelSize: 16
                    font.bold: true
                    Layout.fillWidth: true
                    elide: Text.ElideRight
                }
                Rectangle {
                    width: 70
                    height: 20
                    radius: 10
                    color: signalkStatus === "ready" ? theme.accent : theme.warn
                    Label {
                        anchors.centerIn: parent
                        text: "SignalK"
                        color: theme.bg
                        font.pixelSize: 10
                    }
                }
                Rectangle {
                    width: 70
                    height: 20
                    radius: 10
                    color: nmeaStatus === "ready" ? theme.accent : theme.warn
                    Label {
                        anchors.centerIn: parent
                        text: "NMEA"
                        color: theme.bg
                        font.pixelSize: 10
                    }
                }
                Label {
                    text: "TRACK " + (trackPath ? trackPath.length : 0)
                    color: theme.muted
                    font.pixelSize: 11
                }
            }

            RowLayout {
                Layout.fillWidth: true
                spacing: 6
                Item { Layout.fillWidth: true }
                Button {
                    height: 26
                    padding: 10
                    text: "MAP"
                    background: Rectangle {
                        radius: 10
                        color: root.showCameraMain ? theme.panel : theme.accent
                        border.color: theme.accent
                        border.width: 1
                    }
                    contentItem: Text {
                        text: parent.text
                        color: root.showCameraMain ? theme.text : theme.bg
                        font.pixelSize: 10
                        font.bold: true
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                    onClicked: root.cameraViewRequested(false)
                }
                Button {
                    height: 26
                    padding: 10
                    text: "CAM"
                    background: Rectangle {
                        radius: 10
                        color: root.showCameraMain ? theme.accent : theme.panel
                        border.color: theme.accent
                        border.width: 1
                    }
                    contentItem: Text {
                        text: parent.text
                        color: root.showCameraMain ? theme.bg : theme.text
                        font.pixelSize: 10
                        font.bold: true
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                    onClicked: root.cameraViewRequested(true)
                }
            }
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            radius: theme.radiusSm
            color: "#060f16"
            border.color: theme.panelEdge
            border.width: 1

            Plugin {
                id: osmPlugin
                name: "osm"
                PluginParameter {
                    name: "osm.mapping.custom.host"
                    value: localTileUrl
                }
            }

            Item {
                anchors.fill: parent

                Map {
                    id: navMap
                    anchors.fill: parent
                    plugin: osmPlugin
                    zoomLevel: 8
                    center: navCoordinate
                    visible: !root.showCameraMain

                    MapPolyline {
                        line.width: 2
                        line.color: theme.accent
                        path: trackPath
                    }

                    MapQuickItem {
                        coordinate: navCoordinate
                        anchorPoint.x: 8
                        anchorPoint.y: 8
                        sourceItem: Rectangle {
                            width: 16
                            height: 16
                            radius: 8
                            color: theme.accent
                            border.color: theme.ice
                            border.width: 1
                        }
                    }
                }

                Rectangle {
                    anchors.fill: parent
                    color: "#050910"
                    visible: root.showCameraMain
                    border.color: theme.panelEdge
                    border.width: 1

                    Label {
                        anchors.centerIn: parent
                        text: "LIVE CAMERA FEED"
                        color: theme.muted
                        font.pixelSize: 14
                    }
                }

                Rectangle {
                    width: 200
                    height: 120
                    radius: 10
                    anchors.right: parent.right
                    anchors.top: parent.top
                    anchors.margins: 12
                    color: theme.panel
                    border.color: theme.panelEdge
                    border.width: 1
                    opacity: 0.9
                    visible: root.showCameraMain

                    Label {
                        anchors.centerIn: parent
                        text: "MAP INSET"
                        color: theme.text
                        font.pixelSize: 11
                    }
                }

                Rectangle {
                    width: 200
                    height: 120
                    radius: 10
                    anchors.right: parent.right
                    anchors.top: parent.top
                    anchors.margins: 12
                    color: theme.panel
                    border.color: theme.panelEdge
                    border.width: 1
                    opacity: 0.9
                    visible: !root.showCameraMain

                    Label {
                        anchors.centerIn: parent
                        text: "CAM INSET"
                        color: theme.text
                        font.pixelSize: 11
                    }
                }

                Rectangle {
                    id: compassCard
                    width: 170
                    height: 170
                    radius: 18
                    anchors.left: parent.left
                    anchors.top: parent.top
                    anchors.margins: 12
                    color: theme.panel
                    border.color: theme.panelEdge
                    border.width: 1
                    opacity: 0.92
                    visible: root.showCompass

                    Rectangle {
                        anchors.fill: parent
                        anchors.margins: 6
                        radius: 16
                        color: "transparent"
                        border.color: theme.accent
                        border.width: 1
                        opacity: 0.35
                    }

                    Item {
                        anchors.fill: parent
                        anchors.margins: 12

                        Rectangle {
                            id: compassRing
                            width: 120
                            height: 120
                            radius: 60
                            anchors.horizontalCenter: parent.horizontalCenter
                            anchors.verticalCenter: parent.verticalCenter
                            color: "transparent"
                            border.color: theme.ice
                            border.width: 2
                        }

                        Rectangle {
                            width: 2
                            height: 90
                            color: theme.panelEdge
                            anchors.centerIn: compassRing
                        }
                        Rectangle {
                            width: 90
                            height: 2
                            color: theme.panelEdge
                            anchors.centerIn: compassRing
                        }

                        Rectangle {
                            width: 3
                            height: 54
                            radius: 2
                            color: theme.accent
                            anchors.centerIn: compassRing
                            visible: normalizeDegrees(navHeading) !== null
                            transform: Rotation {
                                origin.x: 1.5
                                origin.y: 48
                                angle: normalizeDegrees(navHeading)
                            }
                        }

                        ColumnLayout {
                            anchors.horizontalCenter: compassRing.horizontalCenter
                            anchors.verticalCenter: compassRing.verticalCenter
                            spacing: 2
                            Label {
                                text: headingText(navHeading)
                                color: theme.text
                                font.pixelSize: 16
                                font.bold: true
                                horizontalAlignment: Text.AlignHCenter
                            }
                            Label {
                                text: "COMPASS"
                                color: theme.muted
                                font.pixelSize: 9
                                horizontalAlignment: Text.AlignHCenter
                            }
                        }
                    }
                }

                Repeater {
                    model: 28
                    Rectangle {
                        width: parent.width
                        height: 1
                        y: index * (parent.height / 28)
                        color: theme.grid
                        opacity: 0.08
                    }
                }

                Repeater {
                    model: 28
                    Rectangle {
                        width: 1
                        height: parent.height
                        x: index * (parent.width / 28)
                        color: theme.grid
                        opacity: 0.08
                    }
                }

                Rectangle {
                    id: logFeedBox
                    width: 220
                    height: 110
                    radius: 12
                    anchors.right: parent.right
                    anchors.top: parent.top
                    anchors.topMargin: 140
                    anchors.rightMargin: 12
                    color: theme.panel
                    border.color: theme.panelEdge
                    border.width: 1
                    opacity: 0.92

                    Rectangle {
                        anchors.fill: parent
                        anchors.margins: 6
                        radius: 10
                        color: "transparent"
                        border.color: theme.accent
                        border.width: 1
                        opacity: 0.35
                    }

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 10
                        spacing: 6
                        Label {
                            text: "LOG FEED"
                            color: theme.muted
                            font.pixelSize: 11
                            font.letterSpacing: 1.1
                        }
                        Text {
                            text: "606-AB 12:05\n602-AB 12:02\nICE WARNING\nLOW VIS"
                            color: theme.text
                            font.pixelSize: 10
                            wrapMode: Text.Wrap
                        }
                    }
                }

                Rectangle {
                    id: chatHud
                    width: Math.min(Math.max(300, parent.width * 0.28), Math.max(0, parent.width - 28))
                    height: Math.min(Math.max(180, parent.height * 0.24), Math.max(0, parent.height - 28))
                    anchors.left: parent.left
                    anchors.bottom: parent.bottom
                    anchors.margins: 14
                    radius: theme.radiusMd
                    color: theme.panel
                    border.color: theme.panelEdge
                    border.width: 1
                    opacity: 0.92

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 10
                        spacing: 6

                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 8
                            Label {
                                text: "AMUNDSEN CHAT"
                                color: theme.text
                                font.pixelSize: 12
                                font.bold: true
                            }
                            Rectangle {
                                width: 70
                                height: 18
                                radius: 9
                                color: root.naviStatus === "ready" ? theme.accent : theme.warn
                                Label {
                                    anchors.centerIn: parent
                                    text: root.naviStatus === "" ? "unknown" : root.naviStatus
                                    color: theme.bg
                                    font.pixelSize: 9
                                }
                            }
                        }

                        ListView {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            model: root.naviPreview
                            clip: true
                            spacing: 4
                            delegate: ColumnLayout {
                                width: ListView.view ? ListView.view.width : 0
                                spacing: 2
                                Label {
                                    text: (modelData.role || "navi").toUpperCase()
                                    color: theme.muted
                                    font.pixelSize: 9
                                }
                                Text {
                                    text: modelData.content || ""
                                    color: theme.text
                                    font.pixelSize: 11
                                    wrapMode: Text.Wrap
                                    width: ListView.view ? ListView.view.width : 0
                                }
                            }
                        }

                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 6
                            TextField {
                                id: chatInput
                                Layout.fillWidth: true
                                placeholderText: "Ask Navi..."
                                color: theme.text
                                placeholderTextColor: theme.muted
                                background: Rectangle {
                                    radius: 6
                                    color: theme.panelSoft
                                    border.color: theme.panelEdge
                                    border.width: 1
                                }
                            }
                            Button {
                                text: "Send"
                                onClicked: {
                                    if (root.sendNaviMessage && chatInput.text.trim() !== "") {
                                        root.sendNaviMessage(chatInput.text);
                                        chatInput.text = "";
                                    }
                                }
                                background: Rectangle {
                                    radius: 6
                                    color: theme.accent
                                }
                                contentItem: Text {
                                    text: parent.text
                                    color: theme.bg
                                    font.bold: true
                                    horizontalAlignment: Text.AlignHCenter
                                    verticalAlignment: Text.AlignVCenter
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
