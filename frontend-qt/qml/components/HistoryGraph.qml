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
        color: Qt.rgba(Theme.panel.r, Theme.panel.g, Theme.panel.b, 0.3)
        border.color: Theme.panelBorder
        border.width: 1
        radius: Theme.radiusSm
    }

    Canvas {
        id: canvas
        anchors.fill: parent
        anchors.margins: 4

        onPaint: {
            var ctx = getContext("2d");
            ctx.clearRect(0, 0, width, height);

            if (root.history.length < 2) return;

            ctx.lineWidth = 2;
            ctx.strokeStyle = Theme.accent;
            ctx.beginPath();

            var stepX = width / (root.historySize - 1);
            var range = root.max - root.min;

            for (var i = 0; i < root.history.length; i++) {
                var val = root.history[i];
                var clamped = Math.max(root.min, Math.min(root.max, val));
                var norm = 1.0 - ((clamped - root.min) / range);

                var x = i * stepX;
                var y = norm * height;

                if (i === 0) ctx.moveTo(x, y);
                else ctx.lineTo(x, y);
            }
            ctx.stroke();

            ctx.lineTo(width, height);
            ctx.lineTo(0, height);
            ctx.closePath();
            ctx.fillStyle = Qt.rgba(Theme.accent.r, Theme.accent.g, Theme.accent.b, 0.1);
            ctx.fill();
        }
    }

    Column {
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.margins: 8

        Text {
            text: root.label
            color: Theme.textMuted
            font.pixelSize: 10
            font.bold: true
            font.family: Theme.fontMono
        }
        Row {
            spacing: 4
            Text {
                text: toNumber(root.value) === null ? "--" : toNumber(root.value).toFixed(1)
                color: Theme.textMain
                font.pixelSize: 14
                font.bold: true
                font.family: Theme.fontMono
            }
            Text {
                text: root.unit
                color: Theme.accent
                font.pixelSize: 10
                anchors.baseline: parent.baseline
                font.family: Theme.fontMono
            }
        }
    }
}
