import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import ".."

RowLayout {
    property string label: ""
    property bool active: false
    property color activeColor: Theme.accent
    property color inactiveColor: Theme.warn
    property string fontFamily: Theme.fontMono

    spacing: 10

    Rectangle {
        width: 18; height: 18; radius: 9
        color: active ? activeColor : inactiveColor
        opacity: active ? 1.0 : 0.5

        SequentialAnimation on opacity {
            running: active
            loops: Animation.Infinite
            NumberAnimation { from: 1.0; to: 0.25; duration: 600 }
            NumberAnimation { from: 0.25; to: 1.0; duration: 600 }
        }
    }
    Label {
        text: label
        color: Theme.muted
        font.pixelSize: 11
        font.family: fontFamily
    }
}
