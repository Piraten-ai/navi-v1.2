import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import ".."

Item {
    id: root
    property string label: ""
    property string unit: ""
    property real value: 0
    property real min: 0
    property real max: 100
    property bool isValid: true
    property string displayText: ""
    property string unitText: unit

    readonly property real clampedValue: Math.max(min, Math.min(max, value))

    Rectangle {
        id: gaugeCircle
        anchors.centerIn: parent
        width: Math.max(110, Math.min(parent.width, parent.height) - 36)
        height: width
        radius: width / 2
        color: "transparent"
        border.color: Theme.ice
        border.width: 2

        Rectangle {
            width: 3
            height: Math.max(36, gaugeCircle.width * 0.35)
            radius: 2
            color: Theme.accent
            anchors.centerIn: parent
            visible: root.isValid && root.max > root.min
            transform: Rotation {
                origin.x: 1.5
                origin.y: Math.max(30, gaugeCircle.width * 0.3)
                angle: root.max > root.min
                       ? -135 + (root.clampedValue - root.min) / (root.max - root.min) * 270
                       : -135
            }
        }

        ColumnLayout {
            anchors.centerIn: parent
            spacing: 2
            Label {
                text: root.displayText !== ""
                      ? root.displayText
                      : (root.isValid ? Number(root.value).toFixed(1) : "--")
                font.bold: true
                font.pixelSize: 18
                color: Theme.text
                horizontalAlignment: Text.AlignHCenter
            }
            Label {
                text: root.unitText
                font.pixelSize: 10
                color: Theme.muted
                horizontalAlignment: Text.AlignHCenter
            }
        }
    }

    Label {
        text: root.label
        anchors.top: gaugeCircle.top
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.topMargin: -16
        color: Theme.muted
        font.pixelSize: 12
    }
}
