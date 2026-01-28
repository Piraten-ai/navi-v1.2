import QtQuick 2.15
import QtQuick.Controls 2.15
import QtLocation 6.2
import QtPositioning 6.2
import ".."

Item {
    id: root

    property var aadsClient
    property var navCoordinate
    property var trackPath
    property bool showMap: true
    property string tileUrl: "http://localhost:8080/tiles/"

    Plugin {
        id: offlineMapPlugin
        name: "osm"

        PluginParameter { name: "osm.mapping.custom.host"; value: root.tileUrl }
        PluginParameter { name: "osm.mapping.providersrepository.disabled"; value: true }
        PluginParameter { name: "osm.mapping.cache.disk.cost_strategy"; value: "unitary" }
        PluginParameter { name: "osm.mapping.cache.disk.size"; value: "0" }
    }

    Map {
        id: map
        anchors.fill: parent
        plugin: offlineMapPlugin
        center: navCoordinate || QtPositioning.coordinate(78.22, 15.63)
        zoomLevel: 12
        copyrightsVisible: false

        // Vessel marker
        MapQuickItem {
            coordinate: root.navCoordinate || map.center
            anchorPoint.x: vesselMarker.width / 2
            anchorPoint.y: vesselMarker.height / 2

            sourceItem: Item {
                id: vesselMarker
                width: Theme.px(40)
                height: Theme.px(40)

                // Outer glow ring
                Rectangle {
                    anchors.centerIn: parent
                    width: Theme.px(36)
                    height: Theme.px(36)
                    radius: width / 2
                    color: "transparent"
                    border.color: Qt.rgba(Theme.accent.r, Theme.accent.g, Theme.accent.b, 0.3)
                    border.width: Math.max(1, Theme.px(3))

                    SequentialAnimation on border.color {
                        running: true
                        loops: Animation.Infinite
                        ColorAnimation {
                            from: Qt.rgba(Theme.accent.r, Theme.accent.g, Theme.accent.b, 0.3)
                            to: Qt.rgba(Theme.accent.r, Theme.accent.g, Theme.accent.b, 0.6)
                            duration: 1500
                        }
                        ColorAnimation {
                            from: Qt.rgba(Theme.accent.r, Theme.accent.g, Theme.accent.b, 0.6)
                            to: Qt.rgba(Theme.accent.r, Theme.accent.g, Theme.accent.b, 0.3)
                            duration: 1500
                        }
                    }
                }

                // Vessel shape (boat icon)
                Canvas {
                    anchors.centerIn: parent
                    width: Theme.px(24)
                    height: Theme.px(32)

                    onPaint: {
                        var ctx = getContext("2d");
                        ctx.clearRect(0, 0, width, height);

                        // Boat hull shape
                        ctx.fillStyle = Theme.accent;
                        ctx.strokeStyle = Theme.accentBright;
                        ctx.lineWidth = 2;

                        ctx.beginPath();
                        ctx.moveTo(width / 2, 0);          // Bow (top)
                        ctx.lineTo(width - 2, height * 0.7); // Starboard
                        ctx.lineTo(width / 2, height - 2);   // Stern
                        ctx.lineTo(2, height * 0.7);         // Port
                        ctx.closePath();

                        ctx.fill();
                        ctx.stroke();

                        // Center line
                        ctx.strokeStyle = Theme.bg;
                        ctx.lineWidth = 1;
                        ctx.beginPath();
                        ctx.moveTo(width / 2, 4);
                        ctx.lineTo(width / 2, height * 0.6);
                        ctx.stroke();
                    }

                    Component.onCompleted: requestPaint()
                }

                transform: Rotation {
                    origin.x: vesselMarker.width / 2
                    origin.y: vesselMarker.height / 2
                    angle: aadsClient ? aadsClient.navHeading : 0

                    Behavior on angle {
                        RotationAnimation {
                            direction: RotationAnimation.Shortest
                            duration: 300
                        }
                    }
                }
            }
        }

        // Track polyline
        MapPolyline {
            line.width: 3
            line.color: Theme.indicator
            path: root.trackPath || []
        }

        // Night mode overlay
        Rectangle {
            anchors.fill: parent
            color: Theme.mapOverlay
            visible: Theme.redMode
        }
    }

    // Grid overlay
    Canvas {
        anchors.fill: parent
        // Grid overlay tends to make the map look "busy" – keep it off by default.
        visible: false
        opacity: 0.08

        onPaint: {
            var ctx = getContext("2d");
            ctx.clearRect(0, 0, width, height);
            ctx.strokeStyle = Qt.rgba(Theme.accent.r, Theme.accent.g, Theme.accent.b, 0.3);
            ctx.lineWidth = 1;
            var step = 80;

            for (var x = 0; x < width; x += step) {
                ctx.beginPath();
                ctx.moveTo(x, 0);
                ctx.lineTo(x, height);
                ctx.stroke();
            }
            for (var y = 0; y < height; y += step) {
                ctx.beginPath();
                ctx.moveTo(0, y);
                ctx.lineTo(width, y);
                ctx.stroke();
            }
        }

        onWidthChanged: requestPaint()
        onHeightChanged: requestPaint()
    }

    // Coordinates panel (bottom right)
    Rectangle {
        color: Qt.rgba(Theme.panel.r, Theme.panel.g, Theme.panel.b, 0.9)
        radius: Theme.radiusSm
        anchors.right: parent.right
        anchors.bottom: parent.bottom
            anchors.margins: Theme.px(10)
        width: coordsCol.width + 24
        height: coordsCol.height + 14
        border.color: Theme.panelEdge
        border.width: 1

        Column {
            id: coordsCol
            anchors.centerIn: parent
            spacing: 4

            Row {
                spacing: 6

                Rectangle {
                    width: 8
                    height: 8
                    radius: 4
                    color: root.navCoordinate ? Theme.success : Theme.warning
                    anchors.verticalCenter: parent.verticalCenter
                }

                Text {
                    text: root.navCoordinate
                          ? root.navCoordinate.latitude.toFixed(5) + "\u00B0N  " + root.navCoordinate.longitude.toFixed(5) + "\u00B0E"
                          : qsTr("NO GPS FIX")
                    color: Theme.textMain
                    font.pixelSize: Theme.px(11)
                    font.family: Theme.fontMono
                    font.bold: true
                }
            }

            Row {
                spacing: 8

                Text {
                    text: qsTr("SOG:")
                    color: Theme.textMuted
                    font.pixelSize: Theme.px(9)
                    font.family: Theme.fontMono
                }

                Text {
                    text: (aadsClient ? aadsClient.navSpeed.toFixed(1) : "0.0") + " kn"
                    color: Theme.accent
                    font.pixelSize: Theme.px(10)
                    font.family: Theme.fontMono
                    font.bold: true
                }

                Text {
                    text: qsTr("HDG:")
                    color: Theme.textMuted
                    font.pixelSize: Theme.px(9)
                    font.family: Theme.fontMono
                }

                Text {
                    text: (aadsClient ? Math.round(aadsClient.navHeading) : "0") + "\u00B0"
                    color: Theme.accent
                    font.pixelSize: Theme.px(10)
                    font.family: Theme.fontMono
                    font.bold: true
                }
            }
        }
    }

    // Zoom controls (bottom left)
    Column {
        anchors.left: parent.left
        anchors.bottom: parent.bottom
        anchors.margins: Theme.px(10)
        spacing: Theme.px(4)

        Rectangle {
            width: Theme.px(32)
            height: Theme.px(32)
            radius: 6
            color: Qt.rgba(Theme.panel.r, Theme.panel.g, Theme.panel.b, 0.9)
            border.color: Theme.panelEdge

            Text {
                anchors.centerIn: parent
                text: "+"
                color: Theme.textMain
                font.pixelSize: Theme.px(18)
                font.bold: true
            }

            MouseArea {
                anchors.fill: parent
                cursorShape: Qt.PointingHandCursor
                onClicked: map.zoomLevel = Math.min(map.zoomLevel + 1, 18)
            }
        }

        Rectangle {
            width: Theme.px(32)
            height: Theme.px(32)
            radius: 6
            color: Qt.rgba(Theme.panel.r, Theme.panel.g, Theme.panel.b, 0.9)
            border.color: Theme.panelEdge

            Text {
                anchors.centerIn: parent
                text: "-"
                color: Theme.textMain
                font.pixelSize: Theme.px(18)
                font.bold: true
            }

            MouseArea {
                anchors.fill: parent
                cursorShape: Qt.PointingHandCursor
                onClicked: map.zoomLevel = Math.max(map.zoomLevel - 1, 2)
            }
        }
    }

    // Scale indicator (top right)
    Rectangle {
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.margins: Theme.px(10)
        width: scaleLabel.width + 16
        height: Theme.px(22)
        radius: 4
        color: Qt.rgba(Theme.panel.r, Theme.panel.g, Theme.panel.b, 0.8)
        border.color: Theme.panelEdge

        Text {
            id: scaleLabel
            anchors.centerIn: parent
            text: qsTr("ZOOM: ") + Math.round(map.zoomLevel)
            color: Theme.textMuted
            font.pixelSize: Theme.px(9)
            font.family: Theme.fontMono
        }
    }
}
