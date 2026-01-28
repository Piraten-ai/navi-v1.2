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
    property string mode: "compass" // "compass", "wind_relative", "wind_true"

    readonly property double numValue: Number(value) || 0
    readonly property double heading: Logic.normalizeDegrees(numValue) || 0
    readonly property string label: metaData ? metaData.label : ""
    readonly property string cardinal: Logic.cardinalDirection(heading)

    property double animatedHeading: 0

    Behavior on animatedHeading {
        RotationAnimation {
            duration: Theme.animNormal
            direction: RotationAnimation.Shortest
            easing.type: Easing.OutCubic
        }
    }

    onHeadingChanged: {
        if (animated) {
            animatedHeading = heading;
        }
    }

    Component.onCompleted: {
        animatedHeading = heading;
    }

    // Outer decorative ring
    Rectangle {
        anchors.centerIn: parent
        width: Math.min(parent.width, parent.height) - 8
        height: width
        radius: width / 2
        color: "transparent"
        border.color: Qt.rgba(Theme.accent.r, Theme.accent.g, Theme.accent.b, 0.15)
        border.width: 2
    }

    // Main compass rose
    Item {
        id: compassRose
        anchors.centerIn: parent
        width: Math.min(parent.width, parent.height) - 24
        height: width

        // Compass ring background
        Rectangle {
            anchors.fill: parent
            radius: width / 2
            color: Qt.rgba(Theme.panelSoft.r, Theme.panelSoft.g, Theme.panelSoft.b, 0.6)
            border.color: Theme.panelEdge
            border.width: 1
        }

        // Rotating compass dial
        Item {
            id: dial
            anchors.fill: parent
            rotation: mode === "compass" ? -animatedHeading : 0

            Behavior on rotation {
                RotationAnimation {
                    duration: Theme.animNormal
                    direction: RotationAnimation.Shortest
                    easing.type: Easing.OutCubic
                }
            }

            // Tick marks and cardinal directions
            Canvas {
                anchors.fill: parent

                onPaint: {
                    var ctx = getContext("2d");
                    ctx.clearRect(0, 0, width, height);

                    var cx = width / 2;
                    var cy = height / 2;
                    var outerR = (width / 2) - 4;
                    var innerRMajor = outerR - 16;
                    var innerRMinor = outerR - 10;
                    var textR = outerR - 28;

                    // Draw tick marks
                    for (var i = 0; i < 36; i++) {
                        var angle = (i * 10 - 90) * Math.PI / 180;
                        var isMajor = (i % 9 === 0);
                        var isMinor = (i % 3 === 0);
                        var innerR = isMajor ? innerRMajor : (isMinor ? innerRMinor : outerR - 6);

                        ctx.strokeStyle = isMajor
                            ? Qt.rgba(Theme.accent.r, Theme.accent.g, Theme.accent.b, 0.9)
                            : Qt.rgba(Theme.gaugeTick.r, Theme.gaugeTick.g, Theme.gaugeTick.b, 0.5);
                        ctx.lineWidth = isMajor ? 2 : 1;

                        ctx.beginPath();
                        ctx.moveTo(cx + Math.cos(angle) * innerR, cy + Math.sin(angle) * innerR);
                        ctx.lineTo(cx + Math.cos(angle) * outerR, cy + Math.sin(angle) * outerR);
                        ctx.stroke();
                    }

                    // Draw cardinal directions
                    ctx.font = "bold 12px " + Theme.fontMono;
                    ctx.textAlign = "center";
                    ctx.textBaseline = "middle";

                    var cardinals = [
                        { text: "N", angle: -90, color: Theme.danger },
                        { text: "E", angle: 0, color: Theme.textMain },
                        { text: "S", angle: 90, color: Theme.textMain },
                        { text: "W", angle: 180, color: Theme.textMain }
                    ];

                    for (var j = 0; j < cardinals.length; j++) {
                        var c = cardinals[j];
                        var cardAngle = c.angle * Math.PI / 180;
                        var tx = cx + Math.cos(cardAngle) * textR;
                        var ty = cy + Math.sin(cardAngle) * textR;

                        ctx.fillStyle = c.color;
                        ctx.fillText(c.text, tx, ty);
                    }
                }

                Component.onCompleted: requestPaint()
            }
        }

        // Wind direction pointer (for wind modes)
        Item {
            anchors.fill: parent
            visible: mode !== "compass"
            rotation: animatedHeading

            // Arrow pointer
            Canvas {
                anchors.fill: parent

                onPaint: {
                    var ctx = getContext("2d");
                    ctx.clearRect(0, 0, width, height);

                    var cx = width / 2;
                    var cy = height / 2;
                    var r = (width / 2) - 20;

                    // Draw arrow
                    ctx.save();
                    ctx.translate(cx, cy);

                    // Arrow body
                    ctx.fillStyle = Theme.accent;
                    ctx.beginPath();
                    ctx.moveTo(0, -r + 10);
                    ctx.lineTo(8, -r + 30);
                    ctx.lineTo(3, -r + 30);
                    ctx.lineTo(3, r - 30);
                    ctx.lineTo(-3, r - 30);
                    ctx.lineTo(-3, -r + 30);
                    ctx.lineTo(-8, -r + 30);
                    ctx.closePath();
                    ctx.fill();

                    // Glow effect
                    ctx.strokeStyle = Qt.rgba(Theme.accent.r, Theme.accent.g, Theme.accent.b, 0.4);
                    ctx.lineWidth = 4;
                    ctx.stroke();

                    ctx.restore();
                }

                Component.onCompleted: requestPaint()
                onVisibleChanged: if (visible) requestPaint()
            }
        }

        // Compass needle (for compass mode)
        Item {
            anchors.fill: parent
            visible: mode === "compass"

            // North pointer (red)
            Rectangle {
                width: 4
                height: compassRose.height / 2 - 24
                radius: 2
                color: Theme.danger
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.bottom: parent.verticalCenter
                anchors.bottomMargin: 4

                Rectangle {
                    anchors.fill: parent
                    anchors.margins: -2
                    radius: 4
                    color: "transparent"
                    border.color: Qt.rgba(Theme.danger.r, Theme.danger.g, Theme.danger.b, 0.4)
                    border.width: 2
                }
            }

            // South pointer (white)
            Rectangle {
                width: 4
                height: compassRose.height / 2 - 24
                radius: 2
                color: Theme.textMain
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.top: parent.verticalCenter
                anchors.topMargin: 4
                opacity: 0.6
            }
        }

        // Center hub
        Rectangle {
            width: 20
            height: 20
            radius: 10
            anchors.centerIn: parent
            color: Theme.gaugeCenter

            Rectangle {
                anchors.fill: parent
                anchors.margins: -4
                radius: (width + 8) / 2
                color: "transparent"
                border.color: Qt.rgba(Theme.gaugeCenter.r, Theme.gaugeCenter.g, Theme.gaugeCenter.b, 0.4)
                border.width: 2
            }
        }
    }

    // Heading indicator triangle (top)
    Canvas {
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: compassRose.top
        anchors.topMargin: -2
        width: 16
        height: 12

        onPaint: {
            var ctx = getContext("2d");
            ctx.clearRect(0, 0, width, height);

            ctx.fillStyle = Theme.accent;
            ctx.beginPath();
            ctx.moveTo(width / 2, height);
            ctx.lineTo(0, 0);
            ctx.lineTo(width, 0);
            ctx.closePath();
            ctx.fill();
        }

        Component.onCompleted: requestPaint()
    }

    // Value display
    Column {
        anchors.centerIn: parent
        anchors.verticalCenterOffset: compassRose.height * 0.22
        spacing: 0

        Text {
            text: Math.round(heading) + "\u00B0"
            color: Theme.textBright
            font.pixelSize: Math.max(14, compassRose.width * 0.16)
            font.bold: true
            font.family: Theme.fontMono
            anchors.horizontalCenter: parent.horizontalCenter
        }

        Text {
            text: cardinal
            color: Theme.accent
            font.pixelSize: Math.max(10, compassRose.width * 0.1)
            font.bold: true
            font.family: Theme.fontMono
            anchors.horizontalCenter: parent.horizontalCenter
        }
    }

    // Label at bottom
    Text {
        text: root.label.toUpperCase()
        color: Theme.textMuted
        font.pixelSize: Math.max(9, Math.min(12, compassRose.width * 0.09))
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
}
