import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Item {
    id: root
    property var theme
    property var aadsClient

    ColumnLayout {
        anchors.fill: parent
        spacing: 12

        RowLayout {
            Layout.fillWidth: true
            spacing: 12
            Label {
                text: "Offline Wiki"
                color: theme.text
                font.pixelSize: 24
                font.bold: true
            }
            Item { Layout.fillWidth: true }
            Button {
                text: "Reload"
                onClicked: aadsClient.loadWiki()
            }
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            radius: theme.radiusMd
            color: theme.panelSoft
            border.color: theme.grid
            border.width: 1

            ScrollView {
                anchors.fill: parent
                anchors.margins: 12
                clip: true
                Text {
                    width: parent.width
                    text: aadsClient.wikiContent
                    color: theme.text
                    wrapMode: Text.Wrap
                    textFormat: Text.MarkdownText
                }
            }
        }
    }
}
