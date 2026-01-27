import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtLocation 6.2
import QtPositioning 6.2
import Qt.labs.settings 1.1
import "components"

ApplicationWindow {
    id: root
    width: 1280
    height: 720
    visible: true
    title: "AADS Native UI"
    color: "transparent"

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
        property string gaugeGridJson: ""
    }

    Theme { id: theme; nightMode: uiSettings.nightMode }
    property var themeRef: theme
    property var clientRef: aadsClient

    property string healthStatus: aadsClient.lastHealthStatus
    property bool wsConnected: aadsClient.wsConnected
    property int wsActiveConnections: aadsClient.wsActiveConnections
    property bool signalkConnected: aadsClient.signalkConnected
    property var trackPath: []
    property var naviPreview: []
    property var profileList: []
    property bool applyingProfile: false
    property string newProfileName: ""
    property bool showCameraMain: false
    property var gaugeGrid: ({ rows: 3, cols: 3, cells: [] })
    property var gaugeCatalog: [
        { key: "", label: "(tom)", unit: "", min: 0, max: 1 },
        { key: "engine.rpm", label: "RPM", unit: "rpm", min: 0, max: 4000 },
        { key: "engine.temperature", label: "Motortemperatur", unit: "°C", min: 0, max: 120 },
        { key: "engine.oil_pressure", label: "Oljetrykk", unit: "bar", min: 0, max: 10 },
        { key: "engine.alternator_voltage", label: "Ladespenning", unit: "V", min: 0, max: 16 },
        { key: "battery.start.voltage", label: "Batterispenning (start)", unit: "V", min: 0, max: 16 },
        { key: "battery.house.voltage", label: "Batterispenning (forbruk)", unit: "V", min: 0, max: 16 },
        { key: "battery.charge_current", label: "Ladestrøm", unit: "A", min: -50, max: 200 },
        { key: "tanks.fuel.level", label: "Dieselnivå", unit: "%", min: 0, max: 100 },
        { key: "tanks.freshwater.level", label: "Ferskvannsnivå", unit: "%", min: 0, max: 100 },
        { key: "tanks.blackwater.level", label: "Septiknivå", unit: "%", min: 0, max: 100 },
        { key: "tanks.greywater.level", label: "Gråvannsnivå", unit: "%", min: 0, max: 100 },
        { key: "nav.depth", label: "Dybde", unit: "m", min: 0, max: 200 },
        { key: "nav.speed_through_water", label: "Fart gjennom vann", unit: "kn", min: 0, max: 30 },
        { key: "nav.speed_over_ground", label: "Fart over grunn", unit: "kn", min: 0, max: 30 },
        { key: "nav.course_over_ground", label: "Kurs over grunn", unit: "°", min: 0, max: 360 },
        { key: "environment.water.temperature", label: "Vanntemperatur", unit: "°C", min: -5, max: 30 },
        { key: "environment.air.temperature", label: "Lufttemperatur", unit: "°C", min: -30, max: 40 },
        { key: "environment.air.humidity", label: "Luftfuktighet", unit: "%", min: 0, max: 100 },
        { key: "environment.air.pressure", label: "Barometer", unit: "hPa", min: 900, max: 1100 },
        { key: "environment.wind.speed", label: "Vindhastighet", unit: "kn", min: 0, max: 60 },
        { key: "environment.wind.angle_apparent", label: "Vindretning (relativ)", unit: "°", min: 0, max: 360 },
        { key: "environment.wind.angle_true", label: "Vindretning (ekte)", unit: "°", min: 0, max: 360 },
        { key: "nav.heading", label: "Kompasskurs", unit: "°", min: 0, max: 360 },
        { key: "navigation.attitude.roll", label: "Krengning", unit: "°", min: -45, max: 45 },
        { key: "steering.rudder_angle", label: "Rorvinkel", unit: "°", min: -45, max: 45 }
    ]

    function bridgeValue(key, fallback) {
        for (var i = 0; i < aadsClient.bridgeSignals.length; i++) {
            if (aadsClient.bridgeSignals[i].name === key) {
                return aadsClient.bridgeSignals[i].value;
            }
        }
        return fallback;
    }

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
            if (navMap) {
                navMap.center = point;
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

    Component.onCompleted: {
        var obj = parseProfiles();
        if (obj.profiles.indexOf("default") === -1) {
            obj.profiles.push("default");
        }
        if (!obj.data["default"]) {
            obj.data["default"] = captureSettings();
        }
        if (obj.profiles.indexOf("solo-arctic") === -1) {
            obj.profiles.push("solo-arctic");
        }
        if (!obj.data["solo-arctic"]) {
            obj.data["solo-arctic"] = {
                nightMode: false,
                showMap: true,
                showNavi: true,
                showCompass: true,
                showWind: true,
                showAutopilot: true,
                mapSource: "local",
                localTileUrl: uiSettings.localTileUrl,
                trackLength: 180,
                wikiPath: uiSettings.wikiPath,
                showSpeed: true,
                showDepth: true,
                showRpm: true,
                showTemp: true,
                showFuel: true,
                showWater: true,
                showBattery: true,
                showCurrent: true,
                gaugeGridJson: ""
            };
        }
        saveProfiles(obj);
        if (!uiSettings.currentProfile || uiSettings.currentProfile === "") {
            uiSettings.currentProfile = "default";
        }
        applyProfile(uiSettings.currentProfile);
        applyGaugeGrid();
        updateNaviPreview();
        aadsClient.loadWiki();
    }
    function formatValue(val, unit) {
        if (val === undefined || val === null) {
            return "--";
        }
        var num = Number(val);
        if (isNaN(num)) {
            return val;
        }
        var decimals = 1;
        if (unit === "rpm" || unit === "°") {
            decimals = 0;
        }
        return num.toFixed(decimals);
    }

    function gaugeText(val, unit) {
        if (unit === "") {
            return val === undefined || val === null || val === "" ? "--" : val;
        }
        return formatValue(val, unit) + " " + unit;
    }

    function normalizeDegrees(val) {
        var num = Number(val);
        if (isNaN(num)) {
            return null;
        }
        var deg = num % 360;
        if (deg < 0) {
            deg += 360;
        }
        return deg;
    }

    function cardinalDirection(deg) {
        var dirs = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"];
        var idx = Math.round(deg / 45) % 8;
        return dirs[idx];
    }

    function headingText(val) {
        var deg = normalizeDegrees(val);
        if (deg === null) {
            return "--";
        }
        return Math.round(deg) + "° " + cardinalDirection(deg);
    }

    function defaultGaugeGrid() {
        return {
            rows: 3,
            cols: 3,
            cells: [
                "engine.rpm",
                "engine.temperature",
                "battery.house.voltage",
                "tanks.fuel.level",
                "nav.depth",
                "nav.speed_over_ground",
                "nav.heading",
                "environment.wind.speed",
                "environment.wind.angle_true"
            ]
        };
    }

    function applyGaugeGrid() {
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
        uiSettings.gaugeGridJson = JSON.stringify(grid);
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
        syncProfile();
    }

    function setGaugeCell(index, key) {
        var grid = gaugeGrid;
        if (index < 0 || index >= grid.cells.length) {
            return;
        }
        grid.cells[index] = key;
        gaugeGrid = grid;
        uiSettings.gaugeGridJson = JSON.stringify(grid);
        syncProfile();
    }

    function gaugeIndexForKey(key) {
        for (var i = 0; i < gaugeCatalog.length; i++) {
            if (gaugeCatalog[i].key === key) {
                return i;
            }
        }
        return 0;
    }

    function gaugeMeta(key) {
        for (var i = 0; i < gaugeCatalog.length; i++) {
            if (gaugeCatalog[i].key === key) {
                return gaugeCatalog[i];
            }
        }
        return gaugeCatalog[0];
    }

    function resolveSignal(key) {
        if (!key || key === "") {
            return "--";
        }
        if (key === "nav.depth") return aadsClient.navDepth !== 0 ? aadsClient.navDepth : bridgeValue(key, "--");
        if (key === "nav.speed_through_water") return bridgeValue(key, aadsClient.navSpeed);
        if (key === "nav.speed_over_ground") return bridgeValue(key, aadsClient.navSpeed);
        if (key === "nav.course_over_ground") return bridgeValue(key, "--");
        if (key === "nav.heading") return aadsClient.navHeading !== 0 ? aadsClient.navHeading : bridgeValue(key, "--");
        if (key === "environment.wind.speed") return bridgeValue(key, aadsClient.navWind);
        if (key === "environment.wind.angle_apparent") return bridgeValue(key, bridgeValue("wind_dir", "--"));
        if (key === "environment.wind.angle_true") return bridgeValue(key, bridgeValue("wind_dir_true", "--"));
        if (key === "environment.air.temperature") return bridgeValue(key, bridgeValue("sense_temp_c", "--"));
        if (key === "environment.air.humidity") return bridgeValue(key, bridgeValue("sense_humidity_pct", "--"));
        if (key === "environment.air.pressure") return bridgeValue(key, bridgeValue("sense_pressure_hpa", "--"));
        if (key === "navigation.attitude.roll") return bridgeValue(key, bridgeValue("sense_roll_deg", "--"));
        if (key === "engine.rpm") return bridgeValue(key, bridgeValue("rpm", "--"));
        if (key === "engine.temperature") return bridgeValue(key, bridgeValue("temp_c", "--"));
        if (key === "engine.oil_pressure") return bridgeValue(key, "--");
        if (key === "engine.alternator_voltage") return bridgeValue(key, "--");
        if (key === "battery.start.voltage") return bridgeValue(key, "--");
        if (key === "battery.house.voltage") return bridgeValue(key, bridgeValue("battery_voltage", "--"));
        if (key === "battery.charge_current") return bridgeValue(key, bridgeValue("current_a", "--"));
        if (key === "tanks.fuel.level") return bridgeValue(key, bridgeValue("fuel_pct", "--"));
        if (key === "tanks.freshwater.level") return bridgeValue(key, "--");
        if (key === "tanks.blackwater.level") return bridgeValue(key, "--");
        if (key === "tanks.greywater.level") return bridgeValue(key, "--");
        if (key === "environment.water.temperature") return bridgeValue(key, "--");
        if (key === "steering.rudder_angle") return bridgeValue(key, "--");
        return bridgeValue(key, "--");
    }

    function isDirectionKey(key) {
        return key === "nav.heading" ||
               key === "nav.course_over_ground" ||
               key === "environment.wind.angle_apparent" ||
               key === "environment.wind.angle_true";
    }

    function parseProfiles() {
        if (!uiSettings.profilesJson || uiSettings.profilesJson === "") {
            return { profiles: ["default"], data: {} };
        }
        try {
            var parsed = JSON.parse(uiSettings.profilesJson);
            if (!parsed.profiles || !parsed.data) {
                return { profiles: ["default"], data: {} };
            }
            return parsed;

        } catch (e) {
            return { profiles: ["default"], data: {} };
        }
    }

    function saveProfiles(obj) {
        uiSettings.profilesJson = JSON.stringify(obj);
        profileList = obj.profiles;
    }

    function captureSettings() {
        return {
            nightMode: uiSettings.nightMode,
            showMap: uiSettings.showMap,
            showNavi: uiSettings.showNavi,
            showCompass: uiSettings.showCompass,
            showWind: uiSettings.showWind,
            showAutopilot: uiSettings.showAutopilot,
            mapSource: uiSettings.mapSource,
            localTileUrl: uiSettings.localTileUrl,
            trackLength: uiSettings.trackLength,
            wikiPath: uiSettings.wikiPath,
            showSpeed: uiSettings.showSpeed,
            showDepth: uiSettings.showDepth,
            showRpm: uiSettings.showRpm,
            showTemp: uiSettings.showTemp,
            showFuel: uiSettings.showFuel,
            showWater: uiSettings.showWater,
            showBattery: uiSettings.showBattery,
            showCurrent: uiSettings.showCurrent,
            gaugeGridJson: uiSettings.gaugeGridJson
        };
    }

    function applyProfile(name) {
        var obj = parseProfiles();
        var data = obj.data[name];
        if (!data) {
            data = captureSettings();
            obj.data[name] = data;
            if (obj.profiles.indexOf(name) === -1) {
                obj.profiles.push(name);
            }
            saveProfiles(obj);
        }
        applyingProfile = true;
        uiSettings.currentProfile = name;
        uiSettings.nightMode = data.nightMode;
        uiSettings.showMap = data.showMap;
        uiSettings.showNavi = data.showNavi;
        uiSettings.showCompass = data.showCompass;
        uiSettings.showWind = data.showWind;
        uiSettings.showAutopilot = data.showAutopilot;
        uiSettings.mapSource = "local";
        uiSettings.localTileUrl = data.localTileUrl || uiSettings.localTileUrl;
        uiSettings.trackLength = data.trackLength || 120;
        uiSettings.wikiPath = data.wikiPath || uiSettings.wikiPath;
        aadsClient.wikiPath = uiSettings.wikiPath;
        aadsClient.loadWiki();
        uiSettings.showSpeed = data.showSpeed;
        uiSettings.showDepth = data.showDepth;
        uiSettings.showRpm = data.showRpm;
        uiSettings.showTemp = data.showTemp;
        uiSettings.showFuel = data.showFuel;
        uiSettings.showWater = data.showWater;
        uiSettings.showBattery = data.showBattery;
        uiSettings.showCurrent = data.showCurrent;
        uiSettings.gaugeGridJson = data.gaugeGridJson || uiSettings.gaugeGridJson;
        applyingProfile = false;
        syncProfile();
        applyGaugeGrid();
    }

    function syncProfile() {
        if (applyingProfile) {
            return;
        }
        var obj = parseProfiles();
        var name = uiSettings.currentProfile || "default";
        if (obj.profiles.indexOf(name) === -1) {
            obj.profiles.push(name);
        }
        obj.data[name] = captureSettings();
        saveProfiles(obj);
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
        gradient: Gradient {
            GradientStop { position: 0.0; color: theme.bg }
            GradientStop { position: 0.5; color: theme.bgMid }
            GradientStop { position: 1.0; color: theme.bgLight }
        }

        Rectangle {
            anchors.fill: parent
            color: "transparent"
            border.color: theme.grid
            border.width: 1
            opacity: 0.5
        }

        Rectangle {
            anchors.fill: parent
            color: "transparent"
            border.color: theme.grid
            border.width: 1
            opacity: 0.25
            anchors.margins: 24
            radius: theme.radiusLg
        }

        ColumnLayout {
            anchors.fill: parent
            spacing: 14
            anchors.margins: 18

            TopBar {
                Layout.fillWidth: true
                theme: themeRef
                currentView: viewStack.currentView
                serviceOk: root.serviceOk
                onViewSelected: function(view) { viewStack.currentView = view }
            }

            RowLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                spacing: 0

                Rectangle {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    radius: theme.radiusLg
                    color: theme.panel
                    border.color: theme.panelEdge
                    border.width: 1

                    StackLayout {
                        id: viewStack
                        anchors.fill: parent
                        anchors.margins: 22
                        property string currentView: "dashboard"

                        onCurrentViewChanged: {
                            if (currentView === "dashboard") currentIndex = 0;
                            else if (currentView === "bridge") currentIndex = 1;
                            else if (currentView === "navi") currentIndex = 2;
                            else if (currentView === "wiki") currentIndex = 3;
                            else if (currentView === "settings") currentIndex = 4;
                        }

                        DashboardView {
                            id: dashboardView
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            theme: themeRef
                            uiSettings: uiSettings
                            aadsClient: clientRef
                            aadsLogoPath: aadsLogoPath
                            trackPath: trackPath
                            navCoordinate: root.navCoordinate()
                            showCameraMain: showCameraMain
                            gaugeGrid: gaugeGrid
                            gaugeCatalog: gaugeCatalog
                            gaugeMeta: gaugeMeta
                            resolveSignal: root.resolveSignal
                            isDirectionKey: root.isDirectionKey
                            headingText: root.headingText
                            normalizeDegrees: root.normalizeDegrees
                            gaugeText: root.gaugeText
                            naviPreview: naviPreview
                            onCameraViewRequested: function(useCamera) { showCameraMain = useCamera }
                        }
                        BridgeView {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            theme: themeRef
                            aadsClient: clientRef
                        }

                        NaviView {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            theme: themeRef
                            aadsClient: clientRef
                        }

                        WikiView {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            theme: themeRef
                            aadsClient: clientRef
                        }

                        SettingsView {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            theme: themeRef
                            aadsClient: clientRef
                            uiSettings: uiSettings
                            profileList: profileList
                            applyProfile: root.applyProfile
                            parseProfiles: root.parseProfiles
                            captureSettings: root.captureSettings
                            saveProfiles: root.saveProfiles
                            syncProfile: root.syncProfile
                            gaugeGrid: gaugeGrid
                            gaugeCatalog: gaugeCatalog
                            gaugeIndexForKey: root.gaugeIndexForKey
                            setGaugeGridSize: root.setGaugeGridSize
                            setGaugeCell: root.setGaugeCell
                        }
                    }
                }
            }
        }
    }

    Timer {
        interval: 2000
        repeat: true
        running: true
        triggeredOnStart: true
        onTriggered: {
            aadsClient.fetchHealth();
            aadsClient.connectWs();
        }
    }

    Timer {
        interval: 5000
        repeat: true
        running: true
        triggeredOnStart: true
        onTriggered: {
            aadsClient.fetchSystemStatus();
            aadsClient.fetchBridgeLatest();
            aadsClient.fetchModuleStatuses();
            aadsClient.fetchNaviHistory(30);
            aadsClient.fetchNavtexSummary();
        }
    }

    Timer {
        interval: 1000
        repeat: true
        running: true
        triggeredOnStart: true
        onTriggered: {
            aadsClient.fetchSignalKNav();
        }
    }

    Rectangle {
        anchors.fill: parent
        color: "#220000"
        opacity: uiSettings.nightMode ? 0.35 : 0.0
        visible: uiSettings.nightMode
    }
}
