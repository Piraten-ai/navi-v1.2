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

        MapQuickItem {
            coordinate: root.navCoordinate || map.center
            anchorPoint.x: 16
            anchorPoint.y: 16
            sourceItem: Item {
                width: 32
                height: 32

                Rectangle {
                    width: 16
                    height: 24
                    anchors.centerIn: parent
                    color: "transparent"
                    border.color: Theme.accent
                    border.width: 2

                    Rectangle {
                        width: 2
                        height: 16
                        color: Theme.accent
                        anchors.bottom: parent.top
                        anchors.horizontalCenter: parent.horizontalCenter
                    }
                }

                transform: Rotation {
                    origin.x: 16
                    origin.y: 16
                    angle: aadsClient ? aadsClient.navHeading : 0
                }
            }
        }

        MapPolyline {
            line.width: 2
            line.color: Theme.indicator
            path: root.trackPath || []
        }

        Rectangle {
            anchors.fill: parent
            color: "#600000"
            opacity: Theme.redMode ? 0.35 : 0.0
            visible: Theme.redMode
        }
    }

    Canvas {
        anchors.fill: parent
        opacity: 0.2
        onPaint: {
            var ctx = getContext("2d");
            ctx.clearRect(0, 0, width, height);
            ctx.strokeStyle = Qt.rgba(Theme.accent.r, Theme.accent.g, Theme.accent.b, 0.25);
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

    Rectangle {
        color: Qt.rgba(Theme.panel.r, Theme.panel.g, Theme.panel.b, 0.8)
        radius: 4
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.margins: 10
        width: coordsCol.width + 20
        height: coordsCol.height + 10
        border.color: Theme.panelBorder

        Column {
            id: coordsCol
            anchors.centerIn: parent
            Text {
                text: qsTr("POS: ") + (root.navCoordinate
                      ? root.navCoordinate.latitude.toFixed(4) + qsTr(" N  ") + root.navCoordinate.longitude.toFixed(4) + qsTr(" E")
                      : qsTr("NO GPS"))
                color: Theme.textMain
                font.pixelSize: 12
                font.family: Theme.fontMono
                font.bold: true
            }
            Text {
                text: qsTr("SOG: ") + (aadsClient ? aadsClient.navSpeed.toFixed(1) : "0.0") + qsTr(" kn")
                color: Theme.textMuted
                font.pixelSize: 10
                font.family: Theme.fontMono
            }
        }
    }
}
