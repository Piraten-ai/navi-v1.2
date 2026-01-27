import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: root
    property var theme
    property var serviceOk: function(name) { return false; }
    property string currentView: "dashboard"
    signal viewSelected(string view)

    height: 56
    radius: theme.radiusLg
    color: theme.panel
    border.color: theme.panelEdge
    border.width: 1

    RowLayout {
        anchors.fill: parent
        anchors.margins: 18
        spacing: 16

        Item { Layout.fillWidth: true }
        Item { Layout.fillWidth: true }

        RowLayout {
            spacing: 10
            Rectangle {
                width: 18
                height: 18
                radius: 9
                color: serviceOk("arduino") ? theme.accent : theme.warn
                opacity: serviceOk("arduino") ? 1.0 : 0.5
                SequentialAnimation on opacity {
                    running: serviceOk("arduino")
                    loops: Animation.Infinite
                    NumberAnimation { from: 1.0; to: 0.25; duration: 600 }
                    NumberAnimation { from: 0.25; to: 1.0; duration: 600 }
                }
            }
            Label { text: "ARDUINO"; color: theme.muted; font.pixelSize: 11 }

            Rectangle {
                width: 18
                height: 18
                radius: 9
                color: serviceOk("jetson") ? theme.accent : theme.warn
                opacity: serviceOk("jetson") ? 1.0 : 0.5
                SequentialAnimation on opacity {
                    running: serviceOk("jetson")
                    loops: Animation.Infinite
                    NumberAnimation { from: 1.0; to: 0.25; duration: 600 }
                    NumberAnimation { from: 0.25; to: 1.0; duration: 600 }
                }
            }
            Label { text: "JETSON"; color: theme.muted; font.pixelSize: 11 }
        }

        RowLayout {
            spacing: 8
            Repeater {
                model: [
                    { label: "Sailing", view: "dashboard" },
                    { label: "Bridge", view: "bridge" },
                    { label: "Navi", view: "navi" },
                    { label: "Wiki", view: "wiki" },
                    { label: "Settings", view: "settings" }
                ]
                delegate: Button {
                    height: 34
                    padding: 12
                    text: modelData.label
                    font.pixelSize: 12
                    background: Rectangle {
                        radius: 10
                        color: root.currentView === modelData.view ? theme.accent : theme.panel
                        border.color: root.currentView === modelData.view ? theme.ice : theme.grid
                        border.width: 1
                    }
                    contentItem: Text {
                        text: parent.text
                        color: root.currentView === modelData.view ? theme.bg : theme.text
                        font.pixelSize: 12
                        font.bold: true
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                    onClicked: root.viewSelected(modelData.view)
                }
            }
        }
    }
}
