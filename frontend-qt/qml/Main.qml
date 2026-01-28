import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQml 2.15
import QtLocation 6.2
import QtPositioning 6.2
import Qt.labs.settings 1.1
import "components"
import "utils/ProfileHandler.js" as ProfileHandler
import "."

ApplicationWindow {
    id: root
    width: 1280
    height: 720
    visible: true
    title: qsTr("AADS Native UI")
    color: "transparent"
    font.family: Theme.fontBody
    font.pixelSize: 12

    Settings {
        id: uiSettings
        property string profilesJson: ""
        property string currentProfile: "default"
        property bool nightMode: false
        property bool showMap: true
        property bool showNavi: true
        property bool showCompass: true
        property bool showWind: true
        property bool showAutopilot: true
        property string mapSource: "local"
        property string localTileUrl: aadsTilesUrl
        property int trackLength: 120
        property string wikiPath: aadsWikiPath
        property bool showSpeed: true
        property bool showDepth: true
        property bool showRpm: true
        property bool showTemp: true
        property bool showFuel: true
        property bool showWater: true
        property bool showBattery: true
        property bool showCurrent: true
        property bool showHistoryGraphs: false
        property string gaugeGridJson: ""
    }

    Binding {
        target: Theme
        property: "nightMode"
        value: uiSettings.nightMode
    }

    Shortcut {
        sequence: "N"
        onActivated: {
            Theme.redMode = !Theme.redMode;
            if (Theme.redMode) {
                uiSettings.nightMode = true;
            }
        }
    }
    property var clientRef: aadsClient

    property string healthStatus: aadsClient.lastHealthStatus
    property bool wsConnected: aadsClient.wsConnected
    property int wsActiveConnections: aadsClient.wsActiveConnections
    property bool signalkConnected: aadsClient.signalkConnected
    property var trackPath: []
    property var naviPreview: []
    property bool showCameraMain: false
    property var gaugeGrid: ({ rows: 3, cols: 3, cells: [] })
    property string currentView: "dashboard"
    property int pollTick: 0

    function serviceStatus(name) {
        var services = aadsClient.healthServices || [];
        for (var i = 0; i < services.length; i++) {
            if ((services[i].name || "").toLowerCase() === name.toLowerCase()) {
                return services[i].status || "unknown";
            }
        }
        return "unknown";
    }

    function serviceOk(name) {
        var status = serviceStatus(name);
        return status === "ok" || status === "ready" || status === "healthy";
    }

    function gaugeEnabled(id) {
        if (id === "speed") return uiSettings.showSpeed;
        if (id === "depth") return uiSettings.showDepth;
        if (id === "rpm") return uiSettings.showRpm;
        if (id === "temp") return uiSettings.showTemp;
        if (id === "fuel") return uiSettings.showFuel;
        if (id === "water") return uiSettings.showWater;
        if (id === "battery") return uiSettings.showBattery;
        if (id === "current") return uiSettings.showCurrent;
        return true;
    }

    function hasNavFix() {
        return aadsClient.navLatitude !== 0 || aadsClient.navLongitude !== 0;
    }

    function navCoordinate() {
        if (hasNavFix()) {
            return QtPositioning.coordinate(aadsClient.navLatitude, aadsClient.navLongitude);
        }
        return QtPositioning.coordinate(78.2232, 15.6267);
    }

    Connections {
        target: aadsClient
        function onNavPositionChanged() {
            if (!hasNavFix()) {
                return;
            }
            var point = QtPositioning.coordinate(aadsClient.navLatitude, aadsClient.navLongitude);
            trackPath.push(point);
            if (trackPath.length > uiSettings.trackLength) {
                trackPath.shift();
            }
        }
        function onWikiPathChanged() {
            aadsClient.loadWiki();
        }
    }

    Connections {
        target: aadsClient
        function onNaviHistoryChanged() {
            updateNaviPreview();
        }
    }

    Connections {
        target: uiSettings
        function onGaugeGridJsonChanged() {
            applyGaugeGrid(false);
        }
    }

    Component.onCompleted: {
        if (!uiSettings.currentProfile || uiSettings.currentProfile === "") {
            uiSettings.currentProfile = "default";
        }
        if (uiSettings.profilesJson && uiSettings.profilesJson !== "") {
            ProfileHandler.applyProfile(uiSettings, aadsClient, uiSettings.currentProfile);
        }
        applyGaugeGrid(true);
        updateNaviPreview();
        aadsClient.loadWiki();
    }





    function defaultGaugeGrid() {
        return {
            rows: 3,
            cols: 2,
            cells: [
                "engine.rpm",
                "engine.rpm",
                "environment.wind.speed",
                "nav.speed_over_ground",
                "environment.wind.angle_apparent",
                "nav.heading"
            ]
        };
    }

    function applyGaugeGrid(persist) {
        var grid = null;
        if (uiSettings.gaugeGridJson && uiSettings.gaugeGridJson !== "") {
            try {
                grid = JSON.parse(uiSettings.gaugeGridJson);
            } catch (e) {
                grid = null;
            }
        }
        if (!grid || !grid.rows || !grid.cols) {
            grid = defaultGaugeGrid();
        }
        grid.rows = Math.max(2, Math.min(4, Number(grid.rows) || 3));
        grid.cols = Math.max(2, Math.min(4, Number(grid.cols) || 3));
        var total = grid.rows * grid.cols;
        if (!grid.cells || !Array.isArray(grid.cells)) {
            grid.cells = [];
        }
        while (grid.cells.length < total) {
            grid.cells.push("");
        }
        if (grid.cells.length > total) {
            grid.cells = grid.cells.slice(0, total);
        }
        gaugeGrid = grid;
        if (persist === undefined || persist) {
            uiSettings.gaugeGridJson = JSON.stringify(grid);
        }
    }

    function setGaugeGridSize(rows, cols) {
        var grid = gaugeGrid;
        grid.rows = rows;
        grid.cols = cols;
        var total = rows * cols;
        while (grid.cells.length < total) {
            grid.cells.push("");
        }
        if (grid.cells.length > total) {
            grid.cells = grid.cells.slice(0, total);
        }
        gaugeGrid = grid;
        uiSettings.gaugeGridJson = JSON.stringify(grid);
    }

    function setGaugeCell(index, key) {
        var grid = gaugeGrid;
        if (index < 0 || index >= grid.cells.length) {
            return;
        }
        grid.cells[index] = key;
        gaugeGrid = grid;
        uiSettings.gaugeGridJson = JSON.stringify(grid);
    }




    function componentForView(view) {
        if (view === "dashboard") return dashboardComponent;
        if (view === "bridge") return bridgeComponent;
        if (view === "navi") return naviComponent;
        if (view === "wiki") return wikiComponent;
        if (view === "settings") return settingsComponent;
        return dashboardComponent;
    }

    function switchView(view) {
        if (!view || view === currentView) {
            return;
        }
        var component = componentForView(view);
        if (!component) {
            return;
        }
        currentView = view;
        viewStack.replace(component);
    }







    function updateNaviPreview() {
        var history = aadsClient.naviHistory || [];
        var start = Math.max(0, history.length - 6);
        var items = [];
        for (var i = start; i < history.length; i++) {
            items.push(history[i]);
        }
        naviPreview = items;
    }

    Rectangle {
        anchors.fill: parent
        color: Theme.bg

        Rectangle {
            anchors.fill: parent
            gradient: Gradient {
                GradientStop { position: 0.0; color: "#050b12" }
                GradientStop { position: 0.55; color: "#0a1520" }
                GradientStop { position: 1.0; color: "#07090d" }
            }
            opacity: 0.95
        }

        Rectangle {
            width: parent.width * 0.65
            height: parent.height * 0.45
            radius: 220
            color: Theme.accent
            opacity: 0.08
            anchors.left: parent.left
            anchors.top: parent.top
            anchors.margins: -120
        }

        Rectangle {
            width: parent.width * 0.55
            height: parent.height * 0.4
            radius: 200
            color: Theme.panelBorder
            opacity: 0.12
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            anchors.margins: -140
        }

        Canvas {
            id: gridOverlay
            anchors.fill: parent
            opacity: 0.08
            onPaint: {
                var ctx = getContext("2d");
                ctx.clearRect(0, 0, width, height);
                ctx.strokeStyle = Qt.rgba(Theme.grid.r, Theme.grid.g, Theme.grid.b, 0.25);
                ctx.lineWidth = 1;
                var step = 60;
                for (var x = 0; x < width; x += step) {
                    ctx.beginPath();
                    ctx.moveTo(x, 0);
                    ctx.lineTo(x, height);
                    ctx.stroke();
                }
                for (var y = 0; y < height; y += step) {
                    ctx.beginPath();
                    ctx.moveTo(0, y);
                    ctx.lineTo(width, y);
                    ctx.stroke();
                }
            }
            onWidthChanged: requestPaint()
            onHeightChanged: requestPaint()
        }

        Rectangle {
            anchors.fill: parent
            color: "transparent"
            border.color: Theme.grid
            border.width: 1
            opacity: 0.35
        }

        Rectangle {
            anchors.fill: parent
            color: "transparent"
            border.color: Theme.grid
            border.width: 1
            opacity: 0.2
            anchors.margins: 26
            radius: Theme.radiusLg + 4
        }

        ColumnLayout {
            anchors.fill: parent
            spacing: 16
            anchors.margins: 20

            TopBar {
                Layout.fillWidth: true
                currentView: root.currentView
                serviceOk: root.serviceOk
                linkOk: aadsClient.wsConnected
                onViewSelected: function(view) { root.switchView(view) }
            }

            RowLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                spacing: 0

                Rectangle {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    radius: Theme.radiusLg + 2
                    color: Qt.rgba(Theme.panel.r, Theme.panel.g, Theme.panel.b, Theme.glassOpacity)
                    border.color: Theme.panelEdge
                    border.width: 1

                    StackView {
                        id: viewStack
                        anchors.fill: parent
                        anchors.margins: 22
                        initialItem: dashboardComponent
                    }
                }
            }
        }
    }

    Timer {
        interval: 1000
        repeat: true
        running: true
        triggeredOnStart: true
        onTriggered: {
            pollTick += 1;
            aadsClient.fetchSignalKNav();
            if (pollTick === 1 || pollTick % 2 === 0) {
                aadsClient.fetchHealth();
                aadsClient.connectWs();
            }
            if (pollTick === 1 || pollTick % 5 === 0) {
                aadsClient.fetchSystemStatus();
                aadsClient.fetchBridgeLatest();
                aadsClient.fetchModuleStatuses();
                aadsClient.fetchNaviHistory(30);
                aadsClient.fetchNavtexSummary();
            }
        }
    }

    Component {
        id: dashboardComponent
        DashboardView {
            uiSettings: uiSettings
            aadsClient: clientRef
            aadsLogoPath: aadsLogoPath
            trackPath: trackPath
            navCoordinate: root.navCoordinate()
            showCameraMain: showCameraMain
            gaugeGrid: gaugeGrid
            naviPreview: naviPreview
            onCameraViewRequested: function(useCamera) { showCameraMain = useCamera }
        }
    }

    Component {
        id: bridgeComponent
        BridgeView {
            aadsClient: clientRef
        }
    }

    Component {
        id: naviComponent
        NaviView {
            aadsClient: clientRef
        }
    }

    Component {
        id: wikiComponent
        WikiView {
            aadsClient: clientRef
        }
    }

    Component {
        id: settingsComponent
        SettingsView {
            aadsClient: clientRef
            uiSettings: uiSettings
            gaugeGrid: gaugeGrid
        }
    }

    Rectangle {
        anchors.fill: parent
        color: "#220000"
        opacity: uiSettings.nightMode ? 0.35 : 0.0
        visible: uiSettings.nightMode
    }
}
