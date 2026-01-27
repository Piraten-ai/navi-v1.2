import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Item {
    id: root
    property var theme
    property var aadsClient
    property var uiSettings
    property var profileList: []
    property var applyProfile
    property var parseProfiles
    property var captureSettings
    property var saveProfiles
    property var syncProfile
    property var gaugeGrid
    property var gaugeCatalog
    property var gaugeIndexForKey
    property var setGaugeGridSize
    property var setGaugeCell
    property string newProfileName: ""

    ColumnLayout {
        anchors.fill: parent
        spacing: 12

        Label {
            text: "Settings"
            color: theme.text
            font.pixelSize: 24
            font.bold: true
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            radius: theme.radiusMd
            color: theme.panelSoft
            border.color: theme.grid
            border.width: 1

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 16
                spacing: 16

                Rectangle {
                    Layout.fillWidth: true
                    radius: theme.radiusSm
                    color: "transparent"
                    border.color: theme.grid
                    border.width: 1

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 12
                        spacing: 8

                        Label {
                            text: "Vessel Profile"
                            color: theme.text
                            font.pixelSize: 16
                            font.bold: true
                        }

                        RowLayout {
                            spacing: 12
                            Label { text: "Active"; color: theme.muted; font.pixelSize: 14; Layout.preferredWidth: 100 }
                            ComboBox {
                                Layout.fillWidth: true
                                model: profileList
                                currentIndex: profileList.indexOf(uiSettings.currentProfile)
                                onActivated: {
                                    if (currentIndex >= 0 && applyProfile) {
                                        applyProfile(profileList[currentIndex]);
                                    }
                                }
                            }
                        }

                        RowLayout {
                            spacing: 12
                            Label { text: "New"; color: theme.muted; font.pixelSize: 14; Layout.preferredWidth: 100 }
                            TextField {
                                Layout.fillWidth: true
                                text: root.newProfileName
                                placeholderText: "e.g. sailboat-01"
                                onTextChanged: root.newProfileName = text
                            }
                            Button {
                                text: "Add"
                                onClicked: {
                                    var name = root.newProfileName.trim();
                                    if (name.length === 0 || !parseProfiles || !captureSettings || !saveProfiles || !applyProfile) {
                                        return;
                                    }
                                    var obj = parseProfiles();
                                    if (obj.profiles.indexOf(name) === -1) {
                                        obj.profiles.push(name);
                                    }
                                    obj.data[name] = captureSettings();
                                    saveProfiles(obj);
                                    root.newProfileName = "";
                                    applyProfile(name);
                                }
                            }
                        }
                    }
                }

                RowLayout {
                    spacing: 12
                    Label {
                        text: "API URL"
                        color: theme.muted
                        font.pixelSize: 16
                        Layout.preferredWidth: 100
                    }
                    TextField {
                        Layout.fillWidth: true
                        text: aadsClient.apiUrl
                        onEditingFinished: aadsClient.apiUrl = text
                    }
                }

                RowLayout {
                    spacing: 12
                    Label {
                        text: "WS URL"
                        color: theme.muted
                        font.pixelSize: 16
                        Layout.preferredWidth: 100
                    }
                    TextField {
                        Layout.fillWidth: true
                        text: aadsClient.wsUrl
                        onEditingFinished: aadsClient.wsUrl = text
                    }
                }

                RowLayout {
                    spacing: 12
                    Label {
                        text: "SignalK"
                        color: theme.muted
                        font.pixelSize: 16
                        Layout.preferredWidth: 100
                    }
                    TextField {
                        Layout.fillWidth: true
                        text: aadsClient.signalkUrl
                        onEditingFinished: aadsClient.signalkUrl = text
                    }
                }

                RowLayout {
                    spacing: 12
                    Label {
                        text: "Wiki Path"
                        color: theme.muted
                        font.pixelSize: 16
                        Layout.preferredWidth: 100
                    }
                    TextField {
                        Layout.fillWidth: true
                        text: uiSettings.wikiPath
                        onEditingFinished: {
                            uiSettings.wikiPath = text;
                            aadsClient.wikiPath = text;
                            aadsClient.loadWiki();
                            if (syncProfile) {
                                syncProfile();
                            }
                        }
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    radius: theme.radiusSm
                    color: "transparent"
                    border.color: theme.grid
                    border.width: 1

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 12
                        spacing: 8

                        Label {
                            text: "Offline Map (MBTiles)"
                            color: theme.text
                            font.pixelSize: 16
                            font.bold: true
                        }

                        RowLayout {
                            spacing: 12
                            Label { text: "Tile URL"; color: theme.muted; font.pixelSize: 14; Layout.preferredWidth: 120 }
                            TextField {
                                Layout.fillWidth: true
                                text: uiSettings.localTileUrl
                                placeholderText: "http://localhost:8080/styles/raster/"
                                onEditingFinished: {
                                    uiSettings.localTileUrl = text;
                                    if (syncProfile) {
                                        syncProfile();
                                    }
                                }
                            }
                        }

                        RowLayout {
                            spacing: 12
                            Label { text: "Track Length"; color: theme.muted; font.pixelSize: 14; Layout.preferredWidth: 120 }
                            Slider {
                                Layout.fillWidth: true
                                from: 50
                                to: 400
                                value: uiSettings.trackLength
                                onValueChanged: {
                                    uiSettings.trackLength = Math.round(value);
                                    if (syncProfile) {
                                        syncProfile();
                                    }
                                }
                            }
                            Label {
                                text: uiSettings.trackLength.toString()
                                color: theme.text
                                font.pixelSize: 12
                            }
                        }
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    radius: theme.radiusSm
                    color: "transparent"
                    border.color: theme.grid
                    border.width: 1

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 12
                        spacing: 8

                        Label {
                            text: "Display Settings"
                            color: theme.text
                            font.pixelSize: 16
                            font.bold: true
                        }

                        RowLayout {
                            spacing: 12
                            Label { text: "Night Mode"; color: theme.muted; font.pixelSize: 14; Layout.preferredWidth: 120 }
                            Switch { checked: uiSettings.nightMode; onToggled: { uiSettings.nightMode = checked; if (syncProfile) syncProfile(); } }
                        }

                        RowLayout {
                            spacing: 12
                            Label { text: "Show Map"; color: theme.muted; font.pixelSize: 14; Layout.preferredWidth: 120 }
                            Switch { checked: uiSettings.showMap; onToggled: { uiSettings.showMap = checked; if (syncProfile) syncProfile(); } }
                        }

                        RowLayout {
                            spacing: 12
                            Label { text: "Show Navi"; color: theme.muted; font.pixelSize: 14; Layout.preferredWidth: 120 }
                            Switch { checked: uiSettings.showNavi; onToggled: { uiSettings.showNavi = checked; if (syncProfile) syncProfile(); } }
                        }

                        RowLayout {
                            spacing: 12
                            Label { text: "Show Compass"; color: theme.muted; font.pixelSize: 14; Layout.preferredWidth: 120 }
                            Switch { checked: uiSettings.showCompass; onToggled: { uiSettings.showCompass = checked; if (syncProfile) syncProfile(); } }
                        }

                        RowLayout {
                            spacing: 12
                            Label { text: "Show Wind"; color: theme.muted; font.pixelSize: 14; Layout.preferredWidth: 120 }
                            Switch { checked: uiSettings.showWind; onToggled: { uiSettings.showWind = checked; if (syncProfile) syncProfile(); } }
                        }

                        RowLayout {
                            spacing: 12
                            Label { text: "Show Autopilot"; color: theme.muted; font.pixelSize: 14; Layout.preferredWidth: 120 }
                            Switch { checked: uiSettings.showAutopilot; onToggled: { uiSettings.showAutopilot = checked; if (syncProfile) syncProfile(); } }
                        }
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    radius: theme.radiusSm
                    color: "transparent"
                    border.color: theme.grid
                    border.width: 1

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 12
                        spacing: 8

                        Label {
                            text: "Gauge Grid"
                            color: theme.text
                            font.pixelSize: 16
                            font.bold: true
                        }

                        RowLayout {
                            spacing: 12
                            Label { text: "Rows"; color: theme.muted; font.pixelSize: 13; Layout.preferredWidth: 90 }
                            ComboBox {
                                model: [2, 3, 4]
                                currentIndex: model.indexOf(gaugeGrid.rows)
                                onActivated: {
                                    if (setGaugeGridSize) {
                                        setGaugeGridSize(model[currentIndex], gaugeGrid.cols);
                                    }
                                }
                            }
                        }

                        RowLayout {
                            spacing: 12
                            Label { text: "Columns"; color: theme.muted; font.pixelSize: 13; Layout.preferredWidth: 90 }
                            ComboBox {
                                model: [2, 3, 4]
                                currentIndex: model.indexOf(gaugeGrid.cols)
                                onActivated: {
                                    if (setGaugeGridSize) {
                                        setGaugeGridSize(gaugeGrid.rows, model[currentIndex]);
                                    }
                                }
                            }
                        }

                        ScrollView {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 240
                            clip: true

                            ColumnLayout {
                                width: parent.width
                                spacing: 8

                                Repeater {
                                    model: gaugeGrid.cells.length
                                    delegate: RowLayout {
                                        spacing: 10
                                        Label {
                                            text: "Cell " + (index + 1)
                                            color: theme.muted
                                            font.pixelSize: 12
                                            Layout.preferredWidth: 90
                                        }
                                        ComboBox {
                                            Layout.fillWidth: true
                                            model: gaugeCatalog
                                            textRole: "label"
                                            valueRole: "key"
                                            currentIndex: gaugeIndexForKey(gaugeGrid.cells[index])
                                            onActivated: {
                                                if (setGaugeCell) {
                                                    setGaugeCell(index, gaugeCatalog[currentIndex].key);
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }

                Button {
                    text: "Reconnect WebSocket"
                    onClicked: {
                        aadsClient.disconnectWs();
                        aadsClient.connectWs();
                    }
                }
            }
        }
    }
}
