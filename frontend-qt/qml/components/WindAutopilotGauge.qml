import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Shapes 1.15
import ".."

// Garmin-inspired Wind/Autopilot display
Item {
    id: root

    property real heading: 0          // Current heading in degrees
    property real windAngle: 0        // Apparent wind angle (-180 to 180, negative = port)
    property real windSpeed: 0        // Wind speed in m/s or knots
    property string windSpeedUnit: "m/s"
    property real boatSpeed: 0        // Boat speed
    property string mode: "Wind Hold" // Autopilot mode
    property string status: "Standby" // Autopilot status
    property bool autopilotActive: false

    // Computed
    property string windSide: windAngle < 0 ? "P" : "S"  // Port or Starboard
    property real absWindAngle: Math.abs(windAngle)

    Rectangle {
        anchors.fill: parent
        radius: Theme.radiusMd
        color: Qt.rgba(Theme.panelSoft.r, Theme.panelSoft.g, Theme.panelSoft.b, 0.92)
        border.color: Theme.panelEdge
        border.width: 1

        // Outer glow
        Rectangle {
            anchors.fill: parent
            anchors.margins: -2
            radius: parent.radius + 2
            color: "transparent"
            border.color: Qt.rgba(Theme.accent.r, Theme.accent.g, Theme.accent.b, 0.3)
            border.width: 2
            z: -1
        }

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: Theme.px(8)
            spacing: Theme.px(4)

            // Top bar - Mode and status
            Rectangle {
                Layout.fillWidth: true
                height: Theme.px(28)
                radius: 4
                gradient: Gradient {
                    GradientStop { position: 0.0; color: Qt.rgba(Theme.accent.r, Theme.accent.g, Theme.accent.b, 0.4) }
                    GradientStop { position: 1.0; color: Qt.rgba(Theme.accent.r, Theme.accent.g, Theme.accent.b, 0.15) }
                }

                RowLayout {
                    anchors.fill: parent
                    anchors.margins: Theme.px(6)

                    Text {
                        text: root.mode
                        color: Theme.accent
                        font.pixelSize: Theme.px(14)
                        font.family: Theme.fontDisplay
                        font.bold: true
                    }

                    Item { Layout.fillWidth: true }

                    // Compass indicator
                    Rectangle {
                        width: Theme.px(24)
                        height: Theme.px(24)
                        radius: 12
                        color: Qt.rgba((root.autopilotActive ? Theme.success : Theme.warn).r,
                                       (root.autopilotActive ? Theme.success : Theme.warn).g,
                                       (root.autopilotActive ? Theme.success : Theme.warn).b, 0.25)
                        border.color: root.autopilotActive ? Theme.success : Theme.warn
                        border.width: 1

                        Text {
                            anchors.centerIn: parent
                            text: root.autopilotActive ? "A" : "S"
                            color: root.autopilotActive ? Theme.success : Theme.warn
                            font.pixelSize: Theme.px(12)
                            font.bold: true
                            font.family: Theme.fontMono
                        }
                    }
                }
            }

            // Main gauge area
            RowLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                spacing: Theme.px(8)

                // Left side - Heading
                ColumnLayout {
                    Layout.preferredWidth: Theme.px(80)
                    spacing: Theme.px(2)

                    Text {
                        text: qsTr("Heading")
                        color: Theme.muted
                        font.pixelSize: Theme.px(10)
                        font.family: Theme.fontMono
                    }

                    Text {
                        text: Math.round(root.heading).toString().padStart(3, '0')
                        color: Theme.textBright
                        font.pixelSize: Theme.px(36)
                        font.family: Theme.fontMono
                        font.bold: true

                        Text {
                            anchors.left: parent.right
                            anchors.top: parent.top
                            anchors.topMargin: Theme.px(4)
                            text: "°M"
                            color: Theme.muted
                            font.pixelSize: Theme.px(14)
                            font.family: Theme.fontMono
                        }
                    }
                }

                // Center - Wind gauge (circular)
                Item {
                    Layout.fillWidth: true
                    Layout.fillHeight: true

                    // Main circular gauge
                    Item {
                        id: windGauge
                        anchors.centerIn: parent
                        width: Math.max(0, Math.min(parent.width, parent.height) - Theme.px(10))
                        height: width

                        // Outer ring with gradient
                        Shape {
                            anchors.fill: parent
                            layer.enabled: true
                            layer.samples: 8

                            ShapePath {
                                strokeWidth: Theme.px(8)
                                strokeColor: Qt.rgba(0.3, 0.3, 0.3, 0.8)
                                fillColor: "transparent"
                                capStyle: ShapePath.RoundCap

                                PathAngleArc {
                                    centerX: windGauge.width / 2
                                    centerY: windGauge.height / 2
                                    radiusX: windGauge.width / 2 - 6
                                    radiusY: windGauge.height / 2 - 6
                                    startAngle: 0
                                    sweepAngle: 360
                                }
                            }
                        }

                        // Color sectors (green-yellow-red for close hauled to running)
                        Shape {
                            anchors.fill: parent
                            layer.enabled: true
                            layer.samples: 8

                            // Green sector (close hauled - optimal)
                            ShapePath {
                                strokeWidth: Theme.px(6)
                                strokeColor: Theme.success
                                fillColor: "transparent"
                                capStyle: ShapePath.FlatCap

                                PathAngleArc {
                                    centerX: windGauge.width / 2
                                    centerY: windGauge.height / 2
                                    radiusX: windGauge.width / 2 - 6
                                    radiusY: windGauge.height / 2 - 6
                                    startAngle: -60
                                    sweepAngle: 30
                                }
                            }

                            // Yellow sector
                            ShapePath {
                                strokeWidth: Theme.px(6)
                                strokeColor: Theme.warn
                                fillColor: "transparent"
                                capStyle: ShapePath.FlatCap

                                PathAngleArc {
                                    centerX: windGauge.width / 2
                                    centerY: windGauge.height / 2
                                    radiusX: windGauge.width / 2 - 6
                                    radiusY: windGauge.height / 2 - 6
                                    startAngle: -30
                                    sweepAngle: 60
                                }
                            }

                            // Green sector (starboard)
                            ShapePath {
                                strokeWidth: Theme.px(6)
                                strokeColor: Theme.success
                                fillColor: "transparent"
                                capStyle: ShapePath.FlatCap

                                PathAngleArc {
                                    centerX: windGauge.width / 2
                                    centerY: windGauge.height / 2
                                    radiusX: windGauge.width / 2 - 6
                                    radiusY: windGauge.height / 2 - 6
                                    startAngle: 30
                                    sweepAngle: 30
                                }
                            }
                        }

                        // Tick marks
                        Repeater {
                            model: 12

                            Rectangle {
                                property real angle: index * 30 - 90
                                x: windGauge.width / 2 + Math.cos(angle * Math.PI / 180) * (windGauge.width / 2 - 20) - width / 2
                                y: windGauge.height / 2 + Math.sin(angle * Math.PI / 180) * (windGauge.height / 2 - 20) - height / 2
                                width: Math.max(1, Theme.px(2))
                                height: Theme.px(index % 3 === 0 ? 12 : 6)
                                color: index % 3 === 0 ? Theme.textBright : Qt.rgba(Theme.textMuted.r, Theme.textMuted.g, Theme.textMuted.b, 0.8)
                                rotation: angle + 90
                                transformOrigin: Item.Center
                            }
                        }

                        // Degree labels
                        Repeater {
                            model: [0, 30, 60, 90, 120, 150, 180]

                            Text {
                                property real angle: (modelData - 90) * Math.PI / 180
                                property real labelAngle: (-modelData - 90) * Math.PI / 180
                                x: windGauge.width / 2 + Math.cos(angle) * (windGauge.width / 2 - 32) - width / 2
                                y: windGauge.height / 2 + Math.sin(angle) * (windGauge.height / 2 - 32) - height / 2
                                text: modelData.toString()
                                color: Theme.textMuted
                                font.pixelSize: Theme.px(9)
                                font.family: Theme.fontMono
                            }
                        }

                        // Mirror for port side
                        Repeater {
                            model: [30, 60, 90, 120, 150]

                            Text {
                                property real angle: (-modelData - 90) * Math.PI / 180
                                x: windGauge.width / 2 + Math.cos(angle) * (windGauge.width / 2 - 32) - width / 2
                                y: windGauge.height / 2 + Math.sin(angle) * (windGauge.height / 2 - 32) - height / 2
                                text: modelData.toString()
                                color: Theme.textMuted
                                font.pixelSize: Theme.px(9)
                                font.family: Theme.fontMono
                            }
                        }

                        // Wind direction pointer (boat-shaped arrow)
                        Item {
                            anchors.centerIn: parent
                            width: parent.width
                            height: parent.height
                            rotation: root.windAngle

                            Behavior on rotation {
                                NumberAnimation { duration: 300; easing.type: Easing.OutQuad }
                            }

                            // Arrow/boat shape pointing up
                            Shape {
                                anchors.centerIn: parent
                                width: Theme.px(30)
                                height: Math.max(0, windGauge.height / 2 - Theme.px(15))

                                ShapePath {
                                    strokeWidth: Math.max(1, Theme.px(2))
                                    strokeColor: Theme.accent
                                    fillGradient: LinearGradient {
                                        x1: 15; y1: 0
                                        x2: 15; y2: 60
                                        GradientStop { position: 0; color: Theme.accent }
                                        GradientStop { position: 1; color: Qt.rgba(Theme.accent.r, Theme.accent.g, Theme.accent.b, 0.3) }
                                    }

                                    startX: 15; startY: 0
                                    PathLine { x: 25; y: 40 }
                                    PathLine { x: 15; y: 35 }
                                    PathLine { x: 5; y: 40 }
                                    PathLine { x: 15; y: 0 }
                                }
                            }

                            // Glow behind arrow
                            Rectangle {
                                anchors.horizontalCenter: parent.horizontalCenter
                                y: Theme.px(10)
                                width: Theme.px(20)
                                height: Theme.px(40)
                                radius: 10
                                color: Theme.accent
                                opacity: 0.3

                                // Pulsing glow
                                SequentialAnimation on opacity {
                                    loops: Animation.Infinite
                                    NumberAnimation { to: 0.5; duration: 1000 }
                                    NumberAnimation { to: 0.2; duration: 1000 }
                                }
                            }
                        }

                        // Center display - Wind speed
                        Rectangle {
                            anchors.centerIn: parent
                            width: Theme.px(70)
                            height: Theme.px(50)
                            radius: 8
                            color: Qt.rgba(0, 0, 0, 0.8)
                            border.color: Qt.rgba(Theme.accent.r, Theme.accent.g, Theme.accent.b, 0.5)
                            border.width: 1

                            Column {
                                anchors.centerIn: parent
                                spacing: 0

                                Text {
                                    anchors.horizontalCenter: parent.horizontalCenter
                                    text: root.windSpeed.toFixed(1)
                                    color: Theme.textBright
                                    font.pixelSize: Theme.px(22)
                                    font.family: Theme.fontMono
                                    font.bold: true

                                    Text {
                                        anchors.left: parent.right
                                        anchors.baseline: parent.baseline
                                        text: root.windSpeedUnit
                                        color: Theme.muted
                                        font.pixelSize: Theme.px(10)
                                        font.family: Theme.fontMono
                                    }
                                }

                                Text {
                                    anchors.horizontalCenter: parent.horizontalCenter
                                    text: "AWS"
                                    color: Theme.muted
                                    font.pixelSize: Theme.px(10)
                                    font.family: Theme.fontMono
                                }
                            }
                        }
                    }
                }

                // Right side - Wind Angle
                ColumnLayout {
                    Layout.preferredWidth: Theme.px(80)
                    spacing: Theme.px(2)
                    Layout.alignment: Qt.AlignRight

                    Text {
                        text: qsTr("Wind Angle")
                        color: Theme.muted
                        font.pixelSize: Theme.px(10)
                        font.family: Theme.fontMono
                        Layout.alignment: Qt.AlignRight
                    }

                    Row {
                        Layout.alignment: Qt.AlignRight
                        spacing: Theme.px(2)

                        Text {
                            text: Math.round(root.absWindAngle).toString().padStart(3, '0')
                            color: Theme.textBright
                            font.pixelSize: Theme.px(36)
                            font.family: Theme.fontMono
                            font.bold: true
                        }

                        Text {
                            text: "°" + root.windSide
                            color: root.windSide === "P" ? Theme.danger : Theme.success
                            font.pixelSize: Theme.px(18)
                            font.family: Theme.fontMono
                            font.bold: true
                            anchors.top: parent.top
                            anchors.topMargin: Theme.px(4)
                        }
                    }
                }
            }

            // Maneuver buttons
            RowLayout {
                Layout.fillWidth: true
                height: Theme.px(36)
                spacing: Theme.px(4)

                Rectangle {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    radius: 4
                    color: Qt.rgba(Theme.panel.r, Theme.panel.g, Theme.panel.b, 0.65)
                    border.color: Theme.panelEdge

                    Text {
                        anchors.centerIn: parent
                        text: qsTr("Gybe Port")
                        color: Theme.textMain
                        font.pixelSize: Theme.px(11)
                        font.family: Theme.fontMono
                    }

                    MouseArea {
                        anchors.fill: parent
                        cursorShape: Qt.PointingHandCursor
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    radius: 4
                    color: Qt.rgba(Theme.panel.r, Theme.panel.g, Theme.panel.b, 0.65)
                    border.color: Theme.panelEdge

                    Text {
                        anchors.centerIn: parent
                        text: qsTr("Tack Starboard")
                        color: Theme.textMain
                        font.pixelSize: Theme.px(11)
                        font.family: Theme.fontMono
                    }

                    MouseArea {
                        anchors.fill: parent
                        cursorShape: Qt.PointingHandCursor
                    }
                }
            }

            // Bottom control bar
            RowLayout {
                Layout.fillWidth: true
                height: Theme.px(32)
                spacing: Theme.px(2)

                // Status button
                Rectangle {
                    Layout.preferredWidth: Theme.px(70)
                    Layout.fillHeight: true
                    radius: 4
                    color: root.autopilotActive
                           ? Qt.rgba(Theme.success.r, Theme.success.g, Theme.success.b, 0.8)
                           : Qt.rgba(Theme.warn.r, Theme.warn.g, Theme.warn.b, 0.35)
                    border.color: root.autopilotActive ? Theme.success : Theme.warn
                    border.width: 1

                    Text {
                        anchors.centerIn: parent
                        text: root.status
                        color: root.autopilotActive ? Theme.bg : Theme.warn
                        font.pixelSize: Theme.px(11)
                        font.family: Theme.fontMono
                        font.bold: true
                    }

                    MouseArea {
                        anchors.fill: parent
                        cursorShape: Qt.PointingHandCursor
                        onClicked: root.autopilotActive = !root.autopilotActive
                    }
                }

                // Adjustment buttons
                Repeater {
                    model: ["<<10°", "<1°", "1°>", "10°>>"]

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        radius: 4
                        color: Qt.rgba(Theme.panel.r, Theme.panel.g, Theme.panel.b, 0.65)
                        border.color: Theme.panelEdge

                        Text {
                            anchors.centerIn: parent
                            text: modelData
                            color: Theme.textMuted
                            font.pixelSize: Theme.px(10)
                            font.family: Theme.fontMono
                        }

                        MouseArea {
                            anchors.fill: parent
                            cursorShape: Qt.PointingHandCursor
                        }
                    }
                }

                // Menu button
                Rectangle {
                    Layout.preferredWidth: Theme.px(40)
                    Layout.fillHeight: true
                    radius: 4
                    color: Qt.rgba(Theme.panel.r, Theme.panel.g, Theme.panel.b, 0.65)
                    border.color: Theme.panelEdge

                    Text {
                        anchors.centerIn: parent
                        text: "..."
                        color: Theme.textMuted
                        font.pixelSize: Theme.px(14)
                        font.family: Theme.fontMono
                        font.bold: true
                    }

                    MouseArea {
                        anchors.fill: parent
                        cursorShape: Qt.PointingHandCursor
                    }
                }
            }
        }
    }
}
