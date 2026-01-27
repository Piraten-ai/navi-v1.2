import QtQuick 2.15
import QtQuick.Shapes 1.15
import ".."
import "../utils/SignalLogic.js" as Logic

Item {
    id: root
    property var metaData
    property var value

    readonly property double numValue: Number(value) || 0
    readonly property double min: metaData ? metaData.min : 0
    readonly property double max: metaData ? metaData.max : 100
    readonly property double angleRange: 270
    readonly property double progress: (Math.max(min, Math.min(max, numValue)) - min) / (max - min)
    readonly property double endAngle: -135 + (progress * angleRange)

    Shape {
        id: baseArc
        anchors.centerIn: parent
        width: Math.min(parent.width, parent.height) - 20
        height: width
        layer.enabled: true

        ShapePath {
            strokeColor: Qt.rgba(Theme.mutedText.r, Theme.mutedText.g, Theme.mutedText.b, 0.2)
            strokeWidth: 6
            fillColor: "transparent"
            capStyle: ShapePath.FlatCap
            PathAngleArc {
                centerX: width / 2; centerY: height / 2
                radiusX: (width / 2) - 4; radiusY: (height / 2) - 4
                startAngle: -135
                sweepAngle: 270
            }
        }
    }

    Shape {
        id: progressArc
        anchors.centerIn: baseArc
        width: baseArc.width
        height: baseArc.height
        layer.enabled: true

        ShapePath {
            strokeColor: Theme.indicator
            strokeWidth: 6
            fillColor: "transparent"
            capStyle: ShapePath.FlatCap
            PathAngleArc {
                centerX: width / 2; centerY: height / 2
                radiusX: (width / 2) - 4; radiusY: (height / 2) - 4
                startAngle: -135
                sweepAngle: root.progress * 270
            }
        }
    }

    Column {
        anchors.centerIn: parent
        spacing: 4

        Text {
            text: Logic.gaugeText(root.value, "")
            color: Theme.textMain
            font.pixelSize: parent.width * 0.22
            font.bold: true
            font.family: Theme.fontMono
            anchors.horizontalCenter: parent.horizontalCenter
        }

        Text {
            text: metaData ? Logic.displayUnit(metaData.unit) : ""
            color: Theme.accent
            font.pixelSize: parent.width * 0.1
            font.family: Theme.fontMono
            anchors.horizontalCenter: parent.horizontalCenter
        }
    }

    Rectangle {
        width: baseArc.width * 0.82
        height: width
        radius: width / 2
        anchors.centerIn: baseArc
        color: "transparent"
        border.color: Qt.rgba(Theme.accent.r, Theme.accent.g, Theme.accent.b, 0.15)
        border.width: 1
    }

    Rectangle {
        width: 2
        height: baseArc.width / 2 - 16
        radius: 1
        color: Theme.accent
        anchors.centerIn: baseArc
        transform: Rotation {
            origin.x: 1
            origin.y: height - 2
            angle: root.endAngle
        }
    }

    Text {
        text: metaData ? metaData.label.toUpperCase() : ""
        color: Theme.textMuted
        font.pixelSize: 12
        font.bold: true
        font.family: Theme.fontBody
        anchors.bottom: parent.bottom
        anchors.horizontalCenter: parent.horizontalCenter
    }
}
