import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import ".."

Rectangle {
    id: root
    property var serviceOk: function(name) { return false; }
    property string currentView: "dashboard"
    property bool linkOk: false
    signal viewSelected(string view)

    height: Theme.px(64)
    radius: Theme.radiusLg + 2
    gradient: Gradient {
        GradientStop { position: 0.0; color: Qt.rgba(Theme.panel.r, Theme.panel.g, Theme.panel.b, 0.95) }
        GradientStop { position: 1.0; color: Qt.rgba(Theme.bg.r, Theme.bg.g, Theme.bg.b, 0.95) }
    }
    border.color: Theme.panelEdge
    border.width: 1

    RowLayout {
        anchors.fill: parent
        anchors.margins: Theme.px(16)
        spacing: Theme.px(14)

        Text {
            text: qsTr("AADS")
            color: Theme.accent
            font.pixelSize: Theme.px(16)
            font.family: Theme.fontDisplay
            font.bold: true
            Layout.alignment: Qt.AlignVCenter
        }

        RowLayout {
            spacing: Theme.px(12)
            Layout.alignment: Qt.AlignVCenter

            StatusLed {
                label: qsTr("ARDUINO")
                active: serviceOk("arduino")
                activeColor: Theme.accent
                inactiveColor: Theme.warn
                fontFamily: Theme.fontMono
            }
            StatusLed {
                label: qsTr("JETSON")
                active: serviceOk("jetson")
                activeColor: Theme.accent
                inactiveColor: Theme.warn
                fontFamily: Theme.fontMono
            }
        }

        // Spacer so the nav pill stays visually centered.
        Item { Layout.fillWidth: true }

        Rectangle {
            Layout.preferredHeight: Theme.px(34)
            Layout.fillWidth: true
            Layout.maximumWidth: Theme.px(560)
            radius: Theme.px(18)
            color: Qt.rgba(Theme.panel.r, Theme.panel.g, Theme.panel.b, 0.7)
            border.color: Theme.panelEdge
            border.width: 1

            RowLayout {
                anchors.fill: parent
                anchors.margins: Theme.px(4)
                spacing: Theme.px(6)

                Repeater {
                    model: [
                        { label: qsTr("Sailing"), view: "dashboard" },
                        { label: qsTr("Bridge"), view: "bridge" },
                        { label: qsTr("Navi"), view: "navi" },
                        { label: qsTr("Wiki"), view: "wiki" },
                        { label: qsTr("Settings"), view: "settings" }
                    ]
                    delegate: Button {
                        height: Theme.px(26)
                        Layout.fillWidth: true
                        padding: Theme.px(6)
                        text: modelData.label
                        font.pixelSize: Theme.px(10)
                        font.family: Theme.fontBody

                        background: Rectangle {
                            radius: Theme.px(12)
                            color: root.currentView === modelData.view ? Theme.accent : "transparent"
                            border.color: root.currentView === modelData.view ? Theme.accent : "transparent"
                            border.width: 1
                        }
                        contentItem: Text {
                            text: parent.text
                            color: root.currentView === modelData.view ? Theme.bg : Theme.textMain
                            font.pixelSize: Theme.px(10)
                            font.bold: true
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }
                        onClicked: root.viewSelected(modelData.view)
                    }
                }
            }
        }

        Item { Layout.fillWidth: true }

        Rectangle {
            width: Theme.px(92)
            height: Theme.px(24)
            radius: Theme.px(12)
            color: linkOk ? Theme.success : Theme.warn
            border.color: Theme.panelEdge
            border.width: 1

            Text {
                anchors.centerIn: parent
                text: linkOk ? qsTr("LINK OK") : qsTr("LINK LOST")
                color: Theme.bg
                font.pixelSize: Theme.px(9)
                font.bold: true
                font.family: Theme.fontMono
            }
        }
    }
}
