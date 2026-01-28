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

    // Organize catalog by category
    property var gaugeCategories: {
        var cats = {};
        for (var i = 0; i < gaugeCatalog.length; i++) {
            var item = gaugeCatalog[i];
            var cat = item.category || "Other";
            if (!cats[cat]) cats[cat] = [];
            cats[cat].push(item);
        }
        return cats;
    }

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
        spacing: 16

        // Header
        RowLayout {
            Layout.fillWidth: true
            spacing: 12

            Text {
                text: qsTr("SETTINGS")
                color: Theme.accent
                font.pixelSize: 22
                font.bold: true
                font.family: Theme.fontDisplay
                font.letterSpacing: 3
            }

            Item { Layout.fillWidth: true }

            Rectangle {
                width: profileBadge.width + 20
                height: 28
                radius: 14
                color: Qt.rgba(Theme.accent.r, Theme.accent.g, Theme.accent.b, 0.15)
                border.color: Theme.accent
                border.width: 1

                Text {
                    id: profileBadge
                    anchors.centerIn: parent
                    text: uiSettings ? uiSettings.currentProfile.toUpperCase() : "DEFAULT"
                    color: Theme.accent
                    font.pixelSize: 10
                    font.bold: true
                    font.family: Theme.fontMono
                }
            }
        }

        // Main content area
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            radius: Theme.radiusMd
            color: Theme.panelSoft
            border.color: Theme.panelEdge
            border.width: 1

            ScrollView {
                anchors.fill: parent
                anchors.margins: 16
                clip: true
                ScrollBar.vertical.policy: ScrollBar.AsNeeded

                ColumnLayout {
                    width: parent.width - 32
                    spacing: 24

                    // Vessel Profile Section
                    SettingsSection {
                        title: qsTr("Vessel Profile")
                        icon: "\u2693" // Anchor

                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 12

                            Text {
                                text: qsTr("Active Profile")
                                color: Theme.muted
                                font.pixelSize: 11
                                font.family: Theme.fontBody
                                Layout.preferredWidth: 120
                            }

                            ComboBox {
                                Layout.fillWidth: true
                                model: root.profileList
                                currentIndex: uiSettings ? root.profileList.indexOf(uiSettings.currentProfile) : 0
                                font.family: Theme.fontBody
                                font.pixelSize: 11

                                background: Rectangle {
                                    radius: 6
                                    color: Theme.bgLight
                                    border.color: Theme.panelEdge
                                }

                                contentItem: Text {
                                    text: parent.displayText
                                    color: Theme.text
                                    font: parent.font
                                    verticalAlignment: Text.AlignVCenter
                                    leftPadding: 10
                                }

                                onActivated: function(index) {
                                    if (!uiSettings) return;
                                    var name = root.profileList[index];
                                    uiSettings.currentProfile = name;
                                    ProfileHandler.applyProfile(uiSettings, aadsClient, name);
                                }
                            }
                        }

                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 12

                            Text {
                                text: qsTr("Create / Save")
                                color: Theme.muted
                                font.pixelSize: 11
                                font.family: Theme.fontBody
                                Layout.preferredWidth: 120
                            }

                            TextField {
                                Layout.fillWidth: true
                                placeholderText: qsTr("e.g. night-watch, rough-sea")
                                placeholderTextColor: Theme.muted
                                text: root.newProfileName
                                onTextChanged: root.newProfileName = text
                                color: Theme.text
                                font.family: Theme.fontBody
                                font.pixelSize: 11
                                background: Rectangle {
                                    radius: 6
                                    color: Theme.bgLight
                                    border.color: Theme.panelEdge
                                }
                            }

                            Button {
                                text: qsTr("Save")
                                font.family: Theme.fontMono
                                font.pixelSize: 10
                                font.bold: true

                                background: Rectangle {
                                    radius: 6
                                    color: Qt.rgba(Theme.accent.r, Theme.accent.g, Theme.accent.b, 0.2)
                                    border.color: Theme.accent
                                }

                                contentItem: Text {
                                    text: parent.text
                                    color: Theme.accent
                                    font: parent.font
                                    horizontalAlignment: Text.AlignHCenter
                                    verticalAlignment: Text.AlignVCenter
                                }

                                onClicked: {
                                    if (!uiSettings) return;
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

                    // Gauge Grid Section
                    SettingsSection {
                        title: qsTr("Gauge Grid Configuration")
                        icon: "\u25A6" // Grid icon

                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 20

                            Text {
                                text: qsTr("Grid Size")
                                color: Theme.muted
                                font.pixelSize: 11
                                font.family: Theme.fontBody
                            }

                            RowLayout {
                                spacing: 8

                                Repeater {
                                    model: [
                                        { rows: 2, cols: 2, label: "2x2" },
                                        { rows: 2, cols: 3, label: "2x3" },
                                        { rows: 3, cols: 3, label: "3x3" },
                                        { rows: 3, cols: 4, label: "3x4" },
                                        { rows: 4, cols: 4, label: "4x4" }
                                    ]

                                    delegate: Rectangle {
                                        width: 50
                                        height: 32
                                        radius: 6
                                        color: (ensureGrid().rows === modelData.rows && ensureGrid().cols === modelData.cols)
                                               ? Theme.accent
                                               : Qt.rgba(Theme.bgLight.r, Theme.bgLight.g, Theme.bgLight.b, 0.8)
                                        border.color: Theme.panelEdge
                                        border.width: 1

                                        Text {
                                            anchors.centerIn: parent
                                            text: modelData.label
                                            color: (ensureGrid().rows === modelData.rows && ensureGrid().cols === modelData.cols)
                                                   ? Theme.bg
                                                   : Theme.text
                                            font.pixelSize: 11
                                            font.bold: true
                                            font.family: Theme.fontMono
                                        }

                                        MouseArea {
                                            anchors.fill: parent
                                            cursorShape: Qt.PointingHandCursor
                                            onClicked: resizeGrid(modelData.rows, modelData.cols)
                                        }
                                    }
                                }
                            }

                            Item { Layout.fillWidth: true }
                        }

                        // Gauge grid editor
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.preferredHeight: Math.max(200, ensureGrid().rows * 60 + 20)
                            radius: Theme.radiusSm
                            color: Qt.rgba(Theme.bg.r, Theme.bg.g, Theme.bg.b, 0.5)
                            border.color: Theme.panelEdge

                            GridLayout {
                                anchors.fill: parent
                                anchors.margins: 10
                                columns: ensureGrid().cols
                                rowSpacing: 8
                                columnSpacing: 8

                                Repeater {
                                    model: ensureGrid().rows * ensureGrid().cols

                                    delegate: Rectangle {
                                        Layout.fillWidth: true
                                        Layout.fillHeight: true
                                        Layout.minimumHeight: 44
                                        radius: 6
                                        color: Qt.rgba(Theme.panelSoft.r, Theme.panelSoft.g, Theme.panelSoft.b, 0.6)
                                        border.color: Theme.panelEdge

                                        ColumnLayout {
                                            anchors.fill: parent
                                            anchors.margins: 4
                                            spacing: 2

                                            Text {
                                                Layout.fillWidth: true
                                                text: (index + 1).toString()
                                                color: Theme.muted
                                                font.pixelSize: 8
                                                font.family: Theme.fontMono
                                                horizontalAlignment: Text.AlignRight
                                            }

                                            ComboBox {
                                                Layout.fillWidth: true
                                                Layout.fillHeight: true
                                                model: root.gaugeCatalog
                                                textRole: "label"
                                                currentIndex: Logic.gaugeIndexForKey(ensureGrid().cells[index])
                                                font.family: Theme.fontBody
                                                font.pixelSize: 9

                                                background: Rectangle {
                                                    radius: 4
                                                    color: Theme.bgLight
                                                    border.color: Theme.panelEdge
                                                }

                                                contentItem: Text {
                                                    text: parent.displayText
                                                    color: Theme.text
                                                    font: parent.font
                                                    verticalAlignment: Text.AlignVCenter
                                                    leftPadding: 6
                                                    elide: Text.ElideRight
                                                }

                                                onActivated: function(idx) {
                                                    setGaugeCell(index, root.gaugeCatalog[idx].key);
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }

                    // Display Settings Section
                    SettingsSection {
                        title: qsTr("Display & Appearance")
                        icon: "\u263C" // Sun

                        GridLayout {
                            Layout.fillWidth: true
                            columns: 2
                            rowSpacing: 12
                            columnSpacing: 20

                            SwitchRow {
                                label: qsTr("Night Mode")
                                checked: uiSettings ? uiSettings.nightMode : false
                                onToggled: function(val) { if (uiSettings) uiSettings.nightMode = val; }
                            }

                            SwitchRow {
                                label: qsTr("Red Night Mode")
                                description: qsTr("Preserves night vision")
                                checked: Theme.redMode
                                onToggled: function(val) { Theme.redMode = val; }
                            }

                            SwitchRow {
                                label: qsTr("Show History Graphs")
                                checked: uiSettings ? uiSettings.showHistoryGraphs : false
                                onToggled: function(val) { if (uiSettings) uiSettings.showHistoryGraphs = val; }
                            }
                        }
                    }

                    // Panel Visibility Section
                    SettingsSection {
                        title: qsTr("Panel Visibility")
                        icon: "\u25A3" // Panels

                        GridLayout {
                            Layout.fillWidth: true
                            columns: 2
                            rowSpacing: 12
                            columnSpacing: 20

                            SwitchRow {
                                label: qsTr("Show Map")
                                checked: uiSettings ? uiSettings.showMap : true
                                onToggled: function(val) { if (uiSettings) uiSettings.showMap = val; }
                            }

                            SwitchRow {
                                label: qsTr("Show Navi Chat")
                                checked: uiSettings ? uiSettings.showNavi : true
                                onToggled: function(val) { if (uiSettings) uiSettings.showNavi = val; }
                            }

                            SwitchRow {
                                label: qsTr("Show Compass")
                                checked: uiSettings ? uiSettings.showCompass : true
                                onToggled: function(val) { if (uiSettings) uiSettings.showCompass = val; }
                            }

                            SwitchRow {
                                label: qsTr("Show Autopilot")
                                checked: uiSettings ? uiSettings.showAutopilot : true
                                onToggled: function(val) { if (uiSettings) uiSettings.showAutopilot = val; }
                            }

                            SwitchRow {
                                label: qsTr("Show Wind Panel")
                                checked: uiSettings ? uiSettings.showWind : true
                                onToggled: function(val) { if (uiSettings) uiSettings.showWind = val; }
                            }
                        }
                    }

                    // Connectivity Section
                    SettingsSection {
                        title: qsTr("Connectivity")
                        icon: "\u21C4" // Arrows

                        GridLayout {
                            Layout.fillWidth: true
                            columns: 2
                            rowSpacing: 12
                            columnSpacing: 12

                            Text {
                                text: qsTr("API URL")
                                color: Theme.muted
                                font.pixelSize: 11
                                font.family: Theme.fontBody
                            }

                            TextField {
                                Layout.fillWidth: true
                                text: aadsClient ? aadsClient.apiUrl : ""
                                color: Theme.text
                                font.family: Theme.fontMono
                                font.pixelSize: 10
                                background: Rectangle {
                                    radius: 6
                                    color: Theme.bgLight
                                    border.color: Theme.panelEdge
                                }
                                onEditingFinished: if (aadsClient) aadsClient.apiUrl = text
                            }

                            Text {
                                text: qsTr("WebSocket URL")
                                color: Theme.muted
                                font.pixelSize: 11
                                font.family: Theme.fontBody
                            }

                            TextField {
                                Layout.fillWidth: true
                                text: aadsClient ? aadsClient.wsUrl : ""
                                color: Theme.text
                                font.family: Theme.fontMono
                                font.pixelSize: 10
                                background: Rectangle {
                                    radius: 6
                                    color: Theme.bgLight
                                    border.color: Theme.panelEdge
                                }
                                onEditingFinished: if (aadsClient) aadsClient.wsUrl = text
                            }

                            Text {
                                text: qsTr("SignalK URL")
                                color: Theme.muted
                                font.pixelSize: 11
                                font.family: Theme.fontBody
                            }

                            TextField {
                                Layout.fillWidth: true
                                text: aadsClient ? aadsClient.signalkUrl : ""
                                color: Theme.text
                                font.family: Theme.fontMono
                                font.pixelSize: 10
                                background: Rectangle {
                                    radius: 6
                                    color: Theme.bgLight
                                    border.color: Theme.panelEdge
                                }
                                onEditingFinished: if (aadsClient) aadsClient.signalkUrl = text
                            }

                            Text {
                                text: qsTr("Tile Server URL")
                                color: Theme.muted
                                font.pixelSize: 11
                                font.family: Theme.fontBody
                            }

                            TextField {
                                Layout.fillWidth: true
                                text: uiSettings ? uiSettings.localTileUrl : ""
                                placeholderText: "http://localhost:8080/..."
                                placeholderTextColor: Theme.muted
                                color: Theme.text
                                font.family: Theme.fontMono
                                font.pixelSize: 10
                                background: Rectangle {
                                    radius: 6
                                    color: Theme.bgLight
                                    border.color: Theme.panelEdge
                                }
                                onEditingFinished: if (uiSettings) uiSettings.localTileUrl = text
                            }
                        }

                        RowLayout {
                            Layout.fillWidth: true
                            Layout.topMargin: 8
                            spacing: 12

                            Item { Layout.fillWidth: true }

                            Button {
                                text: qsTr("Reconnect WebSocket")
                                font.family: Theme.fontMono
                                font.pixelSize: 10

                                background: Rectangle {
                                    radius: 6
                                    color: Qt.rgba(Theme.accent.r, Theme.accent.g, Theme.accent.b, 0.15)
                                    border.color: Theme.accent
                                }

                                contentItem: Text {
                                    text: parent.text
                                    color: Theme.accent
                                    font: parent.font
                                    horizontalAlignment: Text.AlignHCenter
                                    verticalAlignment: Text.AlignVCenter
                                }

                                onClicked: {
                                    if (aadsClient) {
                                        aadsClient.disconnectWs();
                                        aadsClient.connectWs();
                                    }
                                }
                            }
                        }
                    }

                    // Track Settings Section
                    SettingsSection {
                        title: qsTr("Track & Navigation")
                        icon: "\u2192" // Arrow

                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 12

                            Text {
                                text: qsTr("Track Length")
                                color: Theme.muted
                                font.pixelSize: 11
                                font.family: Theme.fontBody
                            }

                            Slider {
                                Layout.fillWidth: true
                                from: 50
                                to: 500
                                stepSize: 10
                                value: uiSettings ? uiSettings.trackLength : 120

                                background: Rectangle {
                                    x: parent.leftPadding
                                    y: parent.topPadding + parent.availableHeight / 2 - height / 2
                                    implicitWidth: 200
                                    implicitHeight: 4
                                    width: parent.availableWidth
                                    height: implicitHeight
                                    radius: 2
                                    color: Theme.bgLight

                                    Rectangle {
                                        width: parent.parent.visualPosition * parent.width
                                        height: parent.height
                                        color: Theme.accent
                                        radius: 2
                                    }
                                }

                                handle: Rectangle {
                                    x: parent.leftPadding + parent.visualPosition * (parent.availableWidth - width)
                                    y: parent.topPadding + parent.availableHeight / 2 - height / 2
                                    implicitWidth: 16
                                    implicitHeight: 16
                                    radius: 8
                                    color: Theme.accent
                                    border.color: Theme.accentBright
                                }

                                onValueChanged: {
                                    if (uiSettings) uiSettings.trackLength = value;
                                }
                            }

                            Text {
                                text: (uiSettings ? uiSettings.trackLength : 120) + " pts"
                                color: Theme.text
                                font.pixelSize: 11
                                font.family: Theme.fontMono
                                Layout.preferredWidth: 60
                            }
                        }
                    }

                    // Spacer at bottom
                    Item { Layout.preferredHeight: 20 }
                }
            }
        }
    }

    // Settings Section Component
    component SettingsSection: ColumnLayout {
        property string title: ""
        property string icon: ""

        Layout.fillWidth: true
        spacing: 12

        RowLayout {
            Layout.fillWidth: true
            spacing: 10

            Text {
                text: icon
                color: Theme.accent
                font.pixelSize: 16
                visible: icon !== ""
            }

            Text {
                text: title
                font.bold: true
                color: Theme.text
                font.pixelSize: 14
                font.family: Theme.fontDisplay
                font.letterSpacing: 1
            }

            Rectangle {
                Layout.fillWidth: true
                height: 1
                color: Qt.rgba(Theme.panelEdge.r, Theme.panelEdge.g, Theme.panelEdge.b, 0.5)
            }
        }
    }

    // Switch Row Component
    component SwitchRow: RowLayout {
        property string label: ""
        property string description: ""
        property bool checked: false
        property var onToggled

        Layout.fillWidth: true
        spacing: 8

        ColumnLayout {
            Layout.fillWidth: true
            spacing: 2

            Text {
                text: label
                color: Theme.text
                font.pixelSize: 11
                font.family: Theme.fontBody
            }

            Text {
                text: description
                color: Theme.muted
                font.pixelSize: 9
                font.family: Theme.fontBody
                visible: description !== ""
            }
        }

        Switch {
            checked: parent.checked

            indicator: Rectangle {
                implicitWidth: 40
                implicitHeight: 20
                x: parent.leftPadding
                y: parent.height / 2 - height / 2
                radius: 10
                color: parent.checked ? Theme.accent : Theme.bgLight
                border.color: parent.checked ? Theme.accentBright : Theme.panelEdge

                Rectangle {
                    x: parent.parent.checked ? parent.width - width - 2 : 2
                    y: 2
                    width: 16
                    height: 16
                    radius: 8
                    color: Theme.text

                    Behavior on x {
                        NumberAnimation { duration: 150 }
                    }
                }
            }

            onToggled: {
                if (parent.onToggled) {
                    parent.onToggled(checked);
                }
            }
        }
    }
}
