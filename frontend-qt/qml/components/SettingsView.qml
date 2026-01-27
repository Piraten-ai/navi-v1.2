import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import ".."
import "../utils/ProfileHandler.js" as ProfileHandler
import "../utils/SignalLogic.js" as Logic

Item {
    id: root
    property var uiSettings
    property var aadsClient
    property var gaugeGrid

    property string newProfileName: ""
    property var profileList: ProfileHandler.getProfileNames(uiSettings ? uiSettings.profilesJson : "")
    property var gaugeCatalog: Logic.getCatalog()

    function ensureGrid() {
        if (gaugeGrid && gaugeGrid.rows && gaugeGrid.cols && gaugeGrid.cells) {
            return gaugeGrid;
        }
        return { rows: 3, cols: 3, cells: [] };
    }

    function commitGrid(grid) {
        gaugeGrid = grid;
        if (uiSettings) {
            uiSettings.gaugeGridJson = JSON.stringify(grid);
        }
    }

    function resizeGrid(rows, cols) {
        var grid = ensureGrid();
        grid.rows = rows;
        grid.cols = cols;
        var total = rows * cols;
        if (!grid.cells || !Array.isArray(grid.cells)) {
            grid.cells = [];
        }
        while (grid.cells.length < total) {
            grid.cells.push("");
        }
        if (grid.cells.length > total) {
            grid.cells = grid.cells.slice(0, total);
        }
        commitGrid(grid);
    }

    function setGaugeCell(index, key) {
        var grid = ensureGrid();
        if (index < 0 || index >= grid.cells.length) {
            return;
        }
        grid.cells[index] = key;
        commitGrid(grid);
    }

    Connections {
        target: uiSettings || null
        function onProfilesJsonChanged() {
            root.profileList = ProfileHandler.getProfileNames(uiSettings.profilesJson);
        }
    }

    Component.onCompleted: {
        resizeGrid(ensureGrid().rows, ensureGrid().cols);
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 12

        Label {
            text: qsTr("Settings")
            color: Theme.text
            font.pixelSize: 24
            font.bold: true
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
                clip: true

                ColumnLayout {
                    width: parent.width - 24
                    x: 12
                    y: 12
                    spacing: 20

                    SettingsGroup {
                        title: qsTr("Vessel Profile")

                        RowLayout {
                            spacing: 12
                            Label { text: qsTr("Active"); color: Theme.muted; Layout.preferredWidth: 100 }
                            ComboBox {
                                Layout.fillWidth: true
                                model: root.profileList
                                currentIndex: uiSettings ? root.profileList.indexOf(uiSettings.currentProfile) : 0
                                onActivated: function(index) {
                                    if (!uiSettings) {
                                        return;
                                    }
                                    var name = root.profileList[index];
                                    uiSettings.currentProfile = name;
                                    ProfileHandler.applyProfile(uiSettings, aadsClient, name);
                                }
                            }
                        }

                        RowLayout {
                            spacing: 12
                            Label { text: qsTr("New / Save"); color: Theme.muted; Layout.preferredWidth: 100 }
                            TextField {
                                Layout.fillWidth: true
                                placeholderText: qsTr("e.g. rough-sea")
                                text: root.newProfileName
                                onTextChanged: root.newProfileName = text
                                color: Theme.text
                                background: Rectangle { color: Theme.bg; border.color: Theme.grid; radius: 4 }
                            }
                            Button {
                                text: qsTr("Save Current")
                                onClicked: {
                                    if (!uiSettings) {
                                        return;
                                    }
                                    var name = root.newProfileName.trim();
                                    if (name === "") name = uiSettings.currentProfile;

                                    var json = ProfileHandler.saveCurrentToProfile(uiSettings, name);
                                    uiSettings.profilesJson = json;

                                    root.profileList = ProfileHandler.getProfileNames(json);
                                    uiSettings.currentProfile = name;
                                    root.newProfileName = "";
                                }
                            }
                        }
                    }

                    SettingsGroup {
                        title: qsTr("Connectivity")

                        SettingRow { label: qsTr("API URL"); value: aadsClient.apiUrl; onEdited: function(txt) { aadsClient.apiUrl = txt; } }
                        SettingRow { label: qsTr("WS URL"); value: aadsClient.wsUrl; onEdited: function(txt) { aadsClient.wsUrl = txt; } }
                        SettingRow { label: qsTr("SignalK"); value: aadsClient.signalkUrl; onEdited: function(txt) { aadsClient.signalkUrl = txt; } }

                        Button {
                            text: qsTr("Reconnect WebSocket")
                            Layout.alignment: Qt.AlignRight
                            onClicked: { aadsClient.disconnectWs(); aadsClient.connectWs(); }
                        }
                    }

                    SettingsGroup {
                        title: qsTr("Display & Map")

                        RowLayout {
                            Label { text: qsTr("Night Mode"); color: Theme.muted; Layout.fillWidth: true }
                            Switch {
                                checked: uiSettings ? uiSettings.nightMode : false
                                onToggled: {
                                    if (uiSettings) {
                                        uiSettings.nightMode = checked;
                                    }
                                }
                            }
                        }

                        RowLayout {
                            Label { text: qsTr("Red Night Mode"); color: Theme.muted; Layout.fillWidth: true }
                            Switch {
                                checked: Theme.redMode
                                onToggled: Theme.redMode = checked
                            }
                        }
                        Text {
                            text: qsTr("Preserves night vision (Red filter)")
                            color: Theme.muted
                            font.pixelSize: 10
                            visible: true
                        }

                        SettingRow {
                            label: qsTr("Tile URL")
                            value: uiSettings ? uiSettings.localTileUrl : ""
                            placeholder: qsTr("http://localhost:8080/...")
                            onEdited: uiSettings ? function(txt) { uiSettings.localTileUrl = txt; } : null
                        }

                        RowLayout {
                            Label { text: qsTr("Track Length"); color: Theme.muted; Layout.fillWidth: true }
                            Label { text: uiSettings ? uiSettings.trackLength : 0; color: Theme.text }
                        }
                        Slider {
                            Layout.fillWidth: true
                            from: 50; to: 500
                            value: uiSettings ? uiSettings.trackLength : 0
                            onValueChanged: {
                                if (uiSettings) {
                                    uiSettings.trackLength = value;
                                }
                            }
                        }
                    }

                    SettingsGroup {
                        title: qsTr("Panels")
                        GridLayout {
                            columns: 2
                            rowSpacing: 10
                            columnSpacing: 20

                            SwitchRow { label: qsTr("Show Map"); checked: uiSettings ? uiSettings.showMap : true; onToggled: uiSettings ? function(val) { uiSettings.showMap = val; } : null }
                            SwitchRow { label: qsTr("Show Navi"); checked: uiSettings ? uiSettings.showNavi : true; onToggled: uiSettings ? function(val) { uiSettings.showNavi = val; } : null }
                            SwitchRow { label: qsTr("Show Compass"); checked: uiSettings ? uiSettings.showCompass : true; onToggled: uiSettings ? function(val) { uiSettings.showCompass = val; } : null }
                            SwitchRow { label: qsTr("Show Wind"); checked: uiSettings ? uiSettings.showWind : true; onToggled: uiSettings ? function(val) { uiSettings.showWind = val; } : null }
                            SwitchRow { label: qsTr("Show Autopilot"); checked: uiSettings ? uiSettings.showAutopilot : true; onToggled: uiSettings ? function(val) { uiSettings.showAutopilot = val; } : null }
                        }
                    }

                    SettingsGroup {
                        title: qsTr("Dashboard Widgets")
                        GridLayout {
                            columns: 2
                            rowSpacing: 10
                            columnSpacing: 20

                            SwitchRow { label: qsTr("Speed"); checked: uiSettings ? uiSettings.showSpeed : false; onToggled: uiSettings ? function(val) { uiSettings.showSpeed = val; } : null }
                            SwitchRow { label: qsTr("Depth"); checked: uiSettings ? uiSettings.showDepth : false; onToggled: uiSettings ? function(val) { uiSettings.showDepth = val; } : null }
                            SwitchRow { label: qsTr("RPM"); checked: uiSettings ? uiSettings.showRpm : false; onToggled: uiSettings ? function(val) { uiSettings.showRpm = val; } : null }
                            SwitchRow { label: qsTr("Temp"); checked: uiSettings ? uiSettings.showTemp : false; onToggled: uiSettings ? function(val) { uiSettings.showTemp = val; } : null }
                            SwitchRow { label: qsTr("Fuel"); checked: uiSettings ? uiSettings.showFuel : false; onToggled: uiSettings ? function(val) { uiSettings.showFuel = val; } : null }
                            SwitchRow { label: qsTr("Battery"); checked: uiSettings ? uiSettings.showBattery : false; onToggled: uiSettings ? function(val) { uiSettings.showBattery = val; } : null }
                        }
                    }

                    SettingsGroup {
                        title: qsTr("Gauges")

                        RowLayout {
                            spacing: 12
                            Label { text: qsTr("Grid"); color: Theme.muted; Layout.preferredWidth: 100 }
                            SpinBox {
                                id: rowsSpin
                                from: 2
                                to: 4
                                value: ensureGrid().rows
                                onValueModified: resizeGrid(value, colsSpin.value)
                            }
                            Text { text: "x"; color: Theme.muted }
                            SpinBox {
                                id: colsSpin
                                from: 2
                                to: 4
                                value: ensureGrid().cols
                                onValueModified: resizeGrid(rowsSpin.value, value)
                            }
                        }

                        GridLayout {
                            columns: ensureGrid().cols
                            rowSpacing: 8
                            columnSpacing: 8
                            Layout.fillWidth: true

                            Repeater {
                                model: ensureGrid().rows * ensureGrid().cols
                                delegate: ComboBox {
                                    Layout.fillWidth: true
                                    model: root.gaugeCatalog
                                    textRole: "display"
                                    currentIndex: Logic.gaugeIndexForKey(ensureGrid().cells[index])
                                    onActivated: function(idx) { setGaugeCell(index, root.gaugeCatalog[idx].key); }
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    component SettingsGroup : ColumnLayout {
        property string title: ""
        spacing: 10
        Layout.fillWidth: true

        Label { text: title; font.bold: true; color: Theme.text; font.pixelSize: 16 }
        Rectangle { height: 1; color: Theme.grid; Layout.fillWidth: true }
    }

    component SettingRow : RowLayout {
        id: settingRow
        property string label: ""
        property string value: ""
        property string placeholder: ""
        property var onEdited

        spacing: 12
        Label { text: label; color: Theme.muted; Layout.preferredWidth: 100 }
        TextField {
            Layout.fillWidth: true
            text: value
            placeholderText: placeholder
            color: Theme.text
            background: Rectangle { color: Theme.bg; border.color: Theme.grid; radius: 4 }
            onEditingFinished: {
                if (settingRow.onEdited) {
                    settingRow.onEdited(text);
                }
            }
        }
    }

    component SwitchRow : RowLayout {
        id: switchRow
        property string label: ""
        property bool checked: false
        property var onToggled

        Label { text: label; color: Theme.muted; Layout.fillWidth: true }
        Switch {
            checked: switchRow.checked
            onToggled: {
                if (switchRow.onToggled) {
                    switchRow.onToggled(checked);
                }
            }
        }
    }
}
