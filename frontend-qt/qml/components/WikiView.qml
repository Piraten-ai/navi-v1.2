import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import ".."

Item {
    id: root
    property var aadsClient

    ColumnLayout {
        anchors.fill: parent
        spacing: 12

        RowLayout {
            Layout.fillWidth: true
            spacing: 12
            Label {
                text: qsTr("Offline Wiki")
                color: Theme.text
                font.pixelSize: 24
                font.bold: true
                font.family: Theme.fontDisplay
            }
            Item { Layout.fillWidth: true }
            Button {
                text: qsTr("Reload")
                onClicked: aadsClient.loadWiki()
            }
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            radius: Theme.radiusMd
            color: Theme.panelSoft
            border.color: Theme.grid
            border.width: 1

            ScrollView {
                anchors.fill: parent
                anchors.margins: 12
                clip: true
                Text {
                    width: parent.width
                    text: aadsClient.wikiContent
                    color: Theme.text
                    wrapMode: Text.Wrap
                    textFormat: Text.MarkdownText
                    font.family: Theme.fontBody
                }
            }
        }
    }
}
