import QtQuick 2.15
import QtQuick.Shapes 1.15
import ".."
import "../utils/SignalLogic.js" as Logic

Item {
    id: root
    property var metaData
    property var value
    property bool showLabel: true
    property bool animated: true
    property real glowIntensity: 0.6

    readonly property double numValue: Number(value) || 0
    readonly property double min: metaData ? metaData.min : 0
    readonly property double max: metaData ? metaData.max : 100
    readonly property string unit: metaData ? metaData.unit : ""
    readonly property string label: metaData ? metaData.label : ""
    readonly property double angleRange: 270
    readonly property double rawProgress: (Math.max(min, Math.min(max, numValue)) - min) / (max - min)
    readonly property double progress: animated ? animatedProgress : rawProgress
    readonly property double endAngle: -135 + (progress * angleRange)

    property double animatedProgress: 0

    Behavior on animatedProgress {
        NumberAnimation {
            duration: Theme.animNormal
            easing.type: Easing.OutCubic
        }
    }

    onRawProgressChanged: {
        if (animated) {
            animatedProgress = rawProgress;
        }
    }

    Component.onCompleted: {
        animatedProgress = rawProgress;
    }

    // Outer glow ring
    Rectangle {
        id: glowRing
        anchors.centerIn: parent
        width: Math.min(parent.width, parent.height) - 8
        height: width
        radius: width / 2
        color: "transparent"
        border.color: Qt.rgba(Theme.accent.r, Theme.accent.g, Theme.accent.b, 0.08 * progress)
        border.width: 12
        opacity: 0.6

        Behavior on border.color {
            ColorAnimation { duration: Theme.animNormal }
        }
    }

    // Background arc (track)
    Shape {
        id: baseArc
        anchors.centerIn: parent
        width: Math.min(parent.width, parent.height) - 24
        height: width
        layer.enabled: true
        layer.samples: 4

        ShapePath {
            strokeColor: Theme.gaugeTrack
            strokeWidth: 8
            fillColor: "transparent"
            capStyle: ShapePath.RoundCap

            PathAngleArc {
                centerX: baseArc.width / 2
                centerY: baseArc.height / 2
                radiusX: (baseArc.width / 2) - 6
                radiusY: (baseArc.height / 2) - 6
                startAngle: -135
                sweepAngle: 270
            }
        }
    }

    // Tick marks
    Canvas {
        id: tickCanvas
        anchors.centerIn: baseArc
        width: baseArc.width
        height: baseArc.height

        onPaint: {
            var ctx = getContext("2d");
            ctx.clearRect(0, 0, width, height);

            var cx = width / 2;
            var cy = height / 2;
            var outerR = (width / 2) - 2;
            var innerRMajor = outerR - 12;
            var innerRMinor = outerR - 8;

            ctx.strokeStyle = Qt.rgba(Theme.gaugeTick.r, Theme.gaugeTick.g, Theme.gaugeTick.b, 0.6);

            for (var i = 0; i <= 10; i++) {
                var angle = (-135 + (i * 27)) * Math.PI / 180;
                var isMajor = (i % 2 === 0);
                var innerR = isMajor ? innerRMajor : innerRMinor;

                ctx.lineWidth = isMajor ? 2 : 1;
                ctx.beginPath();
                ctx.moveTo(cx + Math.cos(angle) * innerR, cy + Math.sin(angle) * innerR);
                ctx.lineTo(cx + Math.cos(angle) * outerR, cy + Math.sin(angle) * outerR);
                ctx.stroke();
            }
        }

        Component.onCompleted: requestPaint()
    }

    // Progress arc with glow
    Shape {
        id: glowArc
        anchors.centerIn: baseArc
        width: baseArc.width
        height: baseArc.height
        layer.enabled: true
        layer.samples: 4
        opacity: glowIntensity * 0.5

        ShapePath {
            strokeColor: Theme.gaugeGlow
            strokeWidth: 14
            fillColor: "transparent"
            capStyle: ShapePath.RoundCap

            PathAngleArc {
                centerX: glowArc.width / 2
                centerY: glowArc.height / 2
                radiusX: (glowArc.width / 2) - 6
                radiusY: (glowArc.height / 2) - 6
                startAngle: -135
                sweepAngle: root.progress * 270
            }
        }
    }

    // Progress arc (main)
    Shape {
        id: progressArc
        anchors.centerIn: baseArc
        width: baseArc.width
        height: baseArc.height
        layer.enabled: true
        layer.samples: 4

        ShapePath {
            strokeColor: Theme.gaugeProgress
            strokeWidth: 8
            fillColor: "transparent"
            capStyle: ShapePath.RoundCap

            PathAngleArc {
                centerX: progressArc.width / 2
                centerY: progressArc.height / 2
                radiusX: (progressArc.width / 2) - 6
                radiusY: (progressArc.height / 2) - 6
                startAngle: -135
                sweepAngle: root.progress * 270
            }
        }
    }

    // Inner decorative ring
    Rectangle {
        width: baseArc.width * 0.72
        height: width
        radius: width / 2
        anchors.centerIn: baseArc
        color: "transparent"
        border.color: Qt.rgba(Theme.accent.r, Theme.accent.g, Theme.accent.b, 0.12)
        border.width: 1
    }

    // Center decorative circle
    Rectangle {
        width: baseArc.width * 0.18
        height: width
        radius: width / 2
        anchors.centerIn: baseArc
        color: Qt.rgba(Theme.panelSoft.r, Theme.panelSoft.g, Theme.panelSoft.b, 0.8)
        border.color: Qt.rgba(Theme.accent.r, Theme.accent.g, Theme.accent.b, 0.3)
        border.width: 1
    }

    // Needle
    Item {
        anchors.centerIn: baseArc
        width: baseArc.width
        height: baseArc.height

        Rectangle {
            id: needle
            width: 3
            height: baseArc.width / 2 - 20
            radius: 1.5
            color: Theme.gaugeNeedle
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.bottom: parent.verticalCenter
            anchors.bottomMargin: -6
            transformOrigin: Item.Bottom

            transform: Rotation {
                origin.x: needle.width / 2
                origin.y: needle.height
                angle: root.endAngle + 90
            }

            // Needle glow
            Rectangle {
                anchors.fill: parent
                anchors.margins: -2
                radius: 3
                color: "transparent"
                border.color: Qt.rgba(Theme.gaugeNeedle.r, Theme.gaugeNeedle.g, Theme.gaugeNeedle.b, 0.4)
                border.width: 2
            }
        }

        // Center cap
        Rectangle {
            width: 12
            height: 12
            radius: 6
            anchors.centerIn: parent
            color: Theme.gaugeCenter

            Rectangle {
                anchors.fill: parent
                anchors.margins: -3
                radius: (width + 6) / 2
                color: "transparent"
                border.color: Qt.rgba(Theme.gaugeCenter.r, Theme.gaugeCenter.g, Theme.gaugeCenter.b, 0.4)
                border.width: 2
            }
        }
    }

    // Value display
    Column {
        anchors.centerIn: parent
        anchors.verticalCenterOffset: baseArc.height * 0.18
        spacing: 2

        Text {
            id: valueText
            text: Logic.formatValue(root.numValue, root.unit)
            color: Theme.textBright
            font.pixelSize: Math.max(16, baseArc.width * 0.2)
            font.bold: true
            font.family: Theme.fontMono
            anchors.horizontalCenter: parent.horizontalCenter

            Behavior on text {
                SequentialAnimation {
                    NumberAnimation { target: valueText; property: "opacity"; to: 0.7; duration: 50 }
                    NumberAnimation { target: valueText; property: "opacity"; to: 1.0; duration: 100 }
                }
            }
        }

        Text {
            text: Logic.displayUnit(root.unit)
            color: Theme.accent
            font.pixelSize: Math.max(10, baseArc.width * 0.1)
            font.family: Theme.fontMono
            font.bold: true
            anchors.horizontalCenter: parent.horizontalCenter
            visible: root.unit !== ""
        }
    }

    // Label at bottom
    Text {
        text: root.label.toUpperCase()
        color: Theme.textMuted
        font.pixelSize: Math.max(9, Math.min(12, baseArc.width * 0.09))
        font.bold: true
        font.letterSpacing: 1
        font.family: Theme.fontBody
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 4
        anchors.horizontalCenter: parent.horizontalCenter
        visible: root.showLabel && root.label !== ""
        elide: Text.ElideRight
        width: parent.width - 8
        horizontalAlignment: Text.AlignHCenter
    }

    // Min/Max labels
    Text {
        text: root.min.toString()
        color: Qt.rgba(Theme.textMuted.r, Theme.textMuted.g, Theme.textMuted.b, 0.6)
        font.pixelSize: 8
        font.family: Theme.fontMono
        anchors.left: parent.left
        anchors.leftMargin: 8
        anchors.bottom: parent.bottom
        anchors.bottomMargin: baseArc.height * 0.25
        visible: root.showLabel
    }

    Text {
        text: root.max.toString()
        color: Qt.rgba(Theme.textMuted.r, Theme.textMuted.g, Theme.textMuted.b, 0.6)
        font.pixelSize: 8
        font.family: Theme.fontMono
        anchors.right: parent.right
        anchors.rightMargin: 8
        anchors.bottom: parent.bottom
        anchors.bottomMargin: baseArc.height * 0.25
        visible: root.showLabel
    }
}
