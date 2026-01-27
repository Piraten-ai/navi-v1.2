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
    readonly property var grid: (gaugeGrid && gaugeGrid.rows && gaugeGrid.cols && gaugeGrid.cells)
                               ? gaugeGrid
                               : ({ rows: 3, cols: 3, cells: [] })

    color: Qt.rgba(Theme.panel.r, Theme.panel.g, Theme.panel.b, Theme.glassOpacity)
    border.color: Theme.panelBorder
    border.width: 1
    radius: Theme.radiusMd

    Rectangle {
        id: header
        height: 28
        width: parent.width
        color: Qt.rgba(Theme.panelBorder.r, Theme.panelBorder.g, Theme.panelBorder.b, 0.16)
        radius: Theme.radiusMd

        Rectangle {
            height: 15
            width: parent.width
            color: parent.color
            anchors.bottom: parent.bottom
        }

        Text {
            text: root.title
            color: Theme.accent
            font.pixelSize: 10
            font.bold: true
            font.letterSpacing: 2
            font.family: Theme.fontDisplay
            anchors.centerIn: parent

            OpacityAnimator on opacity {
                running: !Theme.redMode
                from: 0.6
                to: 1.0
                duration: 2000
                loops: Animation.Infinite
            }
        }
    }

    ColumnLayout {
        anchors.top: header.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.margins: 12
        spacing: 12

        RowLayout {
            Layout.fillWidth: true
            Layout.preferredHeight: 90
            spacing: 10
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

        GridLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            columns: root.grid.cols
            rowSpacing: 12
            columnSpacing: 12

            Repeater {
                model: root.grid.cells
                delegate: Rectangle {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    color: "transparent"
                    border.color: Qt.rgba(Theme.mutedText.r, Theme.mutedText.g, Theme.mutedText.b, 0.3)
                    border.width: 1
                    radius: Theme.radiusSm

                    CircularGauge {
                        anchors.fill: parent
                        anchors.margins: 8
                        metaData: Logic.getGaugeMeta(modelData)
                        value: Logic.resolve(modelData, root.aadsClient, root.aadsClient ? root.aadsClient.bridgeSignals : null)
                    }
                }
            }
        }
    }
}
