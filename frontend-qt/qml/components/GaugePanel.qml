import QtQuick 2.15
import QtQuick.Layouts 1.15
import ".."
import "../utils/SignalLogic.js" as Logic

Rectangle {
    id: root
    property var gaugeGrid
    property var aadsClient
    property string title: qsTr("TACTICAL GAUGES")
    property bool showHistory: false

    // Parse grid with fallback to defaults
    readonly property int gridRows: (gaugeGrid && gaugeGrid.rows) ? gaugeGrid.rows : 3
    readonly property int gridCols: (gaugeGrid && gaugeGrid.cols) ? gaugeGrid.cols : 3
    readonly property var gridCells: (gaugeGrid && gaugeGrid.cells && gaugeGrid.cells.length > 0)
                                     ? gaugeGrid.cells
                                     : defaultCells()

    function defaultCells() {
        return [
            "engine.rpm", "engine.temperature", "battery.house.voltage",
            "tanks.fuel.level", "nav.depth", "nav.speed_over_ground",
            "nav.heading", "environment.wind.speed", "environment.air.pressure"
        ];
    }

    color: Qt.rgba(Theme.panel.r, Theme.panel.g, Theme.panel.b, Theme.glassOpacity)
    border.color: Theme.panelBorder
    border.width: 1
    radius: Theme.radiusMd

    // Header
    Rectangle {
        id: header
        height: 32
        width: parent.width
        color: Qt.rgba(Theme.panelBorder.r, Theme.panelBorder.g, Theme.panelBorder.b, 0.12)
        radius: Theme.radiusMd

        Rectangle {
            height: 16
            width: parent.width
            color: parent.color
            anchors.bottom: parent.bottom
        }

        RowLayout {
            anchors.fill: parent
            anchors.margins: 10
            spacing: 8

            Text {
                text: root.title
                color: Theme.accent
                font.pixelSize: 11
                font.bold: true
                font.letterSpacing: 2
                font.family: Theme.fontDisplay

                OpacityAnimator on opacity {
                    running: !Theme.redMode
                    from: 0.7
                    to: 1.0
                    duration: 2500
                    loops: Animation.Infinite
                }
            }

            Item { Layout.fillWidth: true }

            Text {
                text: gridRows + " x " + gridCols
                color: Theme.muted
                font.pixelSize: 9
                font.family: Theme.fontMono
            }
        }
    }

    ColumnLayout {
        anchors.top: header.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.margins: 10
        spacing: 10

        // History graphs (optional)
        RowLayout {
            Layout.fillWidth: true
            Layout.preferredHeight: 80
            spacing: 8
            visible: root.showHistory

            HistoryGraph {
                Layout.fillWidth: true
                Layout.fillHeight: true
                label: qsTr("ENGINE TEMP")
                unit: qsTr("C")
                min: 60
                max: 110
                value: Logic.resolve("engine.temperature", root.aadsClient, root.aadsClient ? root.aadsClient.bridgeSignals : null)
            }

            HistoryGraph {
                Layout.fillWidth: true
                Layout.fillHeight: true
                label: qsTr("RPM TREND")
                unit: qsTr("rpm")
                min: 0
                max: 4000
                value: Logic.resolve("engine.rpm", root.aadsClient, root.aadsClient ? root.aadsClient.bridgeSignals : null)
            }
        }

        // Gauge grid
        GridLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            columns: root.gridCols
            rowSpacing: 10
            columnSpacing: 10

            Repeater {
                model: root.gridCells

                delegate: Rectangle {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    color: "transparent"
                    border.color: Qt.rgba(Theme.mutedText.r, Theme.mutedText.g, Theme.mutedText.b, 0.2)
                    border.width: 1
                    radius: Theme.radiusSm

                    // Subtle background gradient
                    Rectangle {
                        anchors.fill: parent
                        radius: parent.radius
                        gradient: Gradient {
                            GradientStop { position: 0.0; color: Qt.rgba(Theme.panelSoft.r, Theme.panelSoft.g, Theme.panelSoft.b, 0.3) }
                            GradientStop { position: 1.0; color: "transparent" }
                        }
                    }

                    // Choose gauge type based on key
                    Loader {
                        anchors.fill: parent
                        anchors.margins: 6

                        sourceComponent: {
                            var key = modelData || "";
                            if (Logic.isDirectionKey(key)) {
                                return compassGaugeComponent;
                            }
                            return circularGaugeComponent;
                        }

                        property string gaugeKey: modelData || ""
                    }

                    Component {
                        id: circularGaugeComponent

                        CircularGauge {
                            metaData: Logic.getGaugeMeta(gaugeKey)
                            value: Logic.resolve(gaugeKey, root.aadsClient, root.aadsClient ? root.aadsClient.bridgeSignals : null)
                        }
                    }

                    Component {
                        id: compassGaugeComponent

                        CompassGauge {
                            metaData: Logic.getGaugeMeta(gaugeKey)
                            value: Logic.resolve(gaugeKey, root.aadsClient, root.aadsClient ? root.aadsClient.bridgeSignals : null)
                            mode: {
                                if (gaugeKey === "nav.heading" || gaugeKey === "nav.course_over_ground") {
                                    return "compass";
                                }
                                if (gaugeKey.indexOf("wind") !== -1) {
                                    return gaugeKey.indexOf("true") !== -1 ? "wind_true" : "wind_relative";
                                }
                                return "compass";
                            }
                        }
                    }
                }
            }
        }
    }
}
