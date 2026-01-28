import QtQuick 2.15
import ".."

Item {
    id: root
    property string label: "DATA"
    property string unit: ""
    property var value: 0
    property real min: 0
    property real max: 100
    property int historySize: 60
    property var history: []

    function toNumber(val) {
        var num = Number(val);
        return isNaN(num) ? null : num;
    }

    onValueChanged: {
        var num = toNumber(value);
        if (num === null) return;
        history.push(num);
        if (history.length > historySize) history.shift();
        canvas.requestPaint();
    }

    Rectangle {
        anchors.fill: parent
        color: Qt.rgba(Theme.panel.r, Theme.panel.g, Theme.panel.b, 0.4)
        border.color: Theme.panelEdge
        border.width: 1
        radius: Theme.radiusSm

        // Gradient background
        Rectangle {
            anchors.fill: parent
            radius: parent.radius
            gradient: Gradient {
                GradientStop { position: 0.0; color: Qt.rgba(Theme.accent.r, Theme.accent.g, Theme.accent.b, 0.05) }
                GradientStop { position: 1.0; color: "transparent" }
            }
        }
    }

    // Grid lines
    Canvas {
        id: gridCanvas
        anchors.fill: parent
        anchors.margins: 4

        onPaint: {
            var ctx = getContext("2d");
            ctx.clearRect(0, 0, width, height);

            ctx.strokeStyle = Qt.rgba(Theme.gaugeTick.r, Theme.gaugeTick.g, Theme.gaugeTick.b, 0.2);
            ctx.lineWidth = 1;

            // Horizontal grid lines
            for (var i = 1; i < 4; i++) {
                var y = (height / 4) * i;
                ctx.beginPath();
                ctx.moveTo(0, y);
                ctx.lineTo(width, y);
                ctx.stroke();
            }

            // Vertical grid lines
            for (var j = 1; j < 6; j++) {
                var x = (width / 6) * j;
                ctx.beginPath();
                ctx.moveTo(x, 0);
                ctx.lineTo(x, height);
                ctx.stroke();
            }
        }

        Component.onCompleted: requestPaint()
    }

    Canvas {
        id: canvas
        anchors.fill: parent
        anchors.margins: 4

        onPaint: {
            var ctx = getContext("2d");
            ctx.clearRect(0, 0, width, height);

            if (root.history.length < 2) return;

            var stepX = width / (root.historySize - 1);
            var range = root.max - root.min;
            if (range <= 0) range = 1;

            // Draw gradient fill
            ctx.beginPath();
            for (var i = 0; i < root.history.length; i++) {
                var val = root.history[i];
                var clamped = Math.max(root.min, Math.min(root.max, val));
                var norm = 1.0 - ((clamped - root.min) / range);
                var x = i * stepX;
                var y = norm * height;

                if (i === 0) ctx.moveTo(x, y);
                else ctx.lineTo(x, y);
            }

            // Complete the fill area
            ctx.lineTo((root.history.length - 1) * stepX, height);
            ctx.lineTo(0, height);
            ctx.closePath();

            // Gradient fill
            var gradient = ctx.createLinearGradient(0, 0, 0, height);
            gradient.addColorStop(0, Qt.rgba(Theme.accent.r, Theme.accent.g, Theme.accent.b, 0.3));
            gradient.addColorStop(1, Qt.rgba(Theme.accent.r, Theme.accent.g, Theme.accent.b, 0.02));
            ctx.fillStyle = gradient;
            ctx.fill();

            // Draw line
            ctx.lineWidth = 2;
            ctx.strokeStyle = Theme.accent;
            ctx.lineCap = "round";
            ctx.lineJoin = "round";
            ctx.beginPath();

            for (var j = 0; j < root.history.length; j++) {
                var val2 = root.history[j];
                var clamped2 = Math.max(root.min, Math.min(root.max, val2));
                var norm2 = 1.0 - ((clamped2 - root.min) / range);
                var x2 = j * stepX;
                var y2 = norm2 * height;

                if (j === 0) ctx.moveTo(x2, y2);
                else ctx.lineTo(x2, y2);
            }
            ctx.stroke();

            // Draw glow line
            ctx.lineWidth = 4;
            ctx.strokeStyle = Qt.rgba(Theme.accent.r, Theme.accent.g, Theme.accent.b, 0.3);
            ctx.beginPath();

            for (var k = 0; k < root.history.length; k++) {
                var val3 = root.history[k];
                var clamped3 = Math.max(root.min, Math.min(root.max, val3));
                var norm3 = 1.0 - ((clamped3 - root.min) / range);
                var x3 = k * stepX;
                var y3 = norm3 * height;

                if (k === 0) ctx.moveTo(x3, y3);
                else ctx.lineTo(x3, y3);
            }
            ctx.stroke();

            // Draw current value dot
            if (root.history.length > 0) {
                var lastVal = root.history[root.history.length - 1];
                var lastClamped = Math.max(root.min, Math.min(root.max, lastVal));
                var lastNorm = 1.0 - ((lastClamped - root.min) / range);
                var lastX = (root.history.length - 1) * stepX;
                var lastY = lastNorm * height;

                // Glow
                ctx.fillStyle = Qt.rgba(Theme.accent.r, Theme.accent.g, Theme.accent.b, 0.4);
                ctx.beginPath();
                ctx.arc(lastX, lastY, 6, 0, Math.PI * 2);
                ctx.fill();

                // Dot
                ctx.fillStyle = Theme.accent;
                ctx.beginPath();
                ctx.arc(lastX, lastY, 3, 0, Math.PI * 2);
                ctx.fill();
            }
        }
    }

    // Label and value overlay
    Column {
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.margins: 8
        spacing: 2

        Text {
            text: root.label
            color: Theme.textMuted
            font.pixelSize: 9
            font.bold: true
            font.family: Theme.fontMono
            font.letterSpacing: 1
        }

        Row {
            spacing: 4

            Text {
                text: toNumber(root.value) === null ? "--" : toNumber(root.value).toFixed(1)
                color: Theme.textBright
                font.pixelSize: 16
                font.bold: true
                font.family: Theme.fontMono
            }

            Text {
                text: root.unit
                color: Theme.accent
                font.pixelSize: 10
                font.family: Theme.fontMono
                anchors.baseline: parent.children[0].baseline
            }
        }
    }

    // Min/Max labels
    Text {
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.margins: 6
        text: root.max.toString()
        color: Qt.rgba(Theme.textMuted.r, Theme.textMuted.g, Theme.textMuted.b, 0.6)
        font.pixelSize: 8
        font.family: Theme.fontMono
    }

    Text {
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.margins: 6
        text: root.min.toString()
        color: Qt.rgba(Theme.textMuted.r, Theme.textMuted.g, Theme.textMuted.b, 0.6)
        font.pixelSize: 8
        font.family: Theme.fontMono
    }
}
