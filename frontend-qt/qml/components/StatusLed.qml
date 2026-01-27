import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import ".."

Item {
    id: root
    property bool active: false
    property color colorActive: Theme.accent
    property color colorInactive: Theme.warn
    property string label: ""

    implicitWidth: row.implicitWidth
    implicitHeight: 34

    RowLayout {
        id: row
        spacing: 10

        Rectangle {
            width: 18
            height: 18
            radius: 9
            color: root.active ? root.colorActive : root.colorInactive
            opacity: root.active ? 1.0 : 0.5

            SequentialAnimation on opacity {
                running: root.active
                loops: Animation.Infinite
                NumberAnimation { from: 1.0; to: 0.25; duration: 600 }
                NumberAnimation { from: 0.25; to: 1.0; duration: 600 }
            }
        }

        Label {
            text: root.label
            color: Theme.muted
            font.pixelSize: 11
        }
    }
}
