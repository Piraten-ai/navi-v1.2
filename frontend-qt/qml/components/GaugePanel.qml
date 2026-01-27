import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: root
    property var theme
    property var gaugeGrid
    property var gaugeCatalog
    property var gaugeMeta
    property var resolveSignal
    property var isDirectionKey
    property var headingText
    property var gaugeText
    property int navtexWarningCount: 0
    property string navtexSummary: ""

    radius: theme.radiusMd
    color: theme.panelSoft
    border.color: theme.panelEdge
    border.width: 1

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 12
        spacing: 10

        Label {
            text: "NAVIGATION & CONTROLS"
            color: theme.muted
            font.pixelSize: 12
            font.letterSpacing: 1.2
        }

        Rectangle {
            Layout.fillWidth: true
            height: 4
            radius: 2
            color: theme.accentSoft
            border.color: theme.accent
            border.width: 1
            opacity: 0.7
        }

        Rectangle {
            Layout.fillWidth: true
            height: 36
            radius: theme.radiusSm
            color: theme.panel
            border.color: theme.panelEdge
            border.width: 1

            RowLayout {
                anchors.fill: parent
                anchors.margins: 8
                spacing: 8
                Label {
                    text: "VAKTEN ALERTS"
                    color: theme.muted
                    font.pixelSize: 11
                    font.letterSpacing: 1.1
                }
                Rectangle {
                    width: 60
                    height: 18
                    radius: 9
                    color: navtexWarningCount > 0 ? theme.warn : theme.accent
                    Label {
                        anchors.centerIn: parent
                        text: navtexWarningCount > 0 ? "WARN" : "OK"
                        color: theme.bg
                        font.pixelSize: 9
                    }
                }
                Label {
                    Layout.fillWidth: true
                    text: navtexSummary === "" ? "No active alerts." : navtexSummary
                    color: theme.text
                    font.pixelSize: 11
                    elide: Text.ElideRight
                }
            }
        }

        GridLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            columns: gaugeGrid.cols
            rowSpacing: 12
            columnSpacing: 12

            Repeater {
                model: gaugeGrid.cells

                delegate: Rectangle {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    radius: theme.radiusMd
                    color: theme.panel
                    border.color: theme.panelEdge
                    border.width: 1

                    property var meta: gaugeMeta(modelData)
                    property var value: resolveSignal(modelData)
                    property double numericValue: Number(value)
                    property double minValue: meta.min
                    property double maxValue: meta.max
                    property bool validValue: !isNaN(numericValue) && meta.key !== "" && maxValue > minValue
                    property double clampedValue: Math.max(minValue, Math.min(maxValue, numericValue))

                    Item {
                        anchors.fill: parent
                        anchors.margins: 12

                        Rectangle {
                            anchors.fill: parent
                            anchors.margins: 2
                            radius: theme.radiusMd - 2
                            color: "transparent"
                            border.color: theme.accent
                            border.width: 1
                            opacity: 0.2
                            visible: meta.key !== ""
                        }

                        Label {
                            id: gaugeLabel
                            text: meta.label
                            color: theme.muted
                            font.pixelSize: 12
                        }

                        Rectangle {
                            id: gaugeCircle
                            width: Math.max(110, Math.min(parent.width, parent.height) - 36)
                            height: width
                            radius: width / 2
                            anchors.horizontalCenter: parent.horizontalCenter
                            anchors.verticalCenter: parent.verticalCenter
                            color: "transparent"
                            border.color: theme.ice
                            border.width: 2
                            visible: meta.key !== ""
                        }

                        Rectangle {
                            width: 3
                            height: Math.max(36, gaugeCircle.width * 0.35)
                            radius: 2
                            color: theme.accent
                            anchors.centerIn: gaugeCircle
                            visible: validValue
                            transform: Rotation {
                                origin.x: 1.5
                                origin.y: Math.max(30, gaugeCircle.width * 0.3)
                                angle: -135 + (clampedValue - minValue) / (maxValue - minValue) * 270
                            }
                        }

                        ColumnLayout {
                            anchors.horizontalCenter: gaugeCircle.horizontalCenter
                            anchors.verticalCenter: gaugeCircle.verticalCenter
                            spacing: 2
                            Label {
                                text: meta.key === ""
                                      ? "Velg maler"
                                      : (isDirectionKey(meta.key)
                                         ? headingText(value)
                                         : gaugeText(value, meta.unit))
                                color: theme.text
                                font.pixelSize: 18
                                font.bold: true
                                horizontalAlignment: Text.AlignHCenter
                            }
                            Label {
                                text: meta.key === ""
                                      ? ""
                                      : (isDirectionKey(meta.key) ? "" : (meta.unit === "" ? "" : meta.unit))
                                color: theme.muted
                                font.pixelSize: 10
                                horizontalAlignment: Text.AlignHCenter
                            }
                        }
                    }
                }
            }
        }
    }
}
