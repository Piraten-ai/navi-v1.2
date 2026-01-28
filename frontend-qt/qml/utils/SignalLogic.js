.pragma library

function formatValue(val, unit) {
    if (val === undefined || val === null || val === "--") return "--";
    var num = Number(val);
    if (isNaN(num)) return val;
    var decimals = (unit === "rpm" || unit === "deg" || unit === "pct" || unit === "hPa") ? 0 : 1;
    return num.toFixed(decimals);
}

function normalizeDegrees(val) {
    var num = Number(val);
    if (isNaN(num)) return null;
    var deg = num % 360;
    return (deg < 0) ? deg + 360 : deg;
}

function cardinalDirection(deg) {
    var dirs = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"];
    var idx = Math.round(deg / 45) % 8;
    return dirs[idx];
}

function headingText(val) {
    var deg = normalizeDegrees(val);
    if (deg === null) return "--";
    return Math.round(deg) + " deg " + cardinalDirection(deg);
}

function gaugeText(val, unit) {
    if (unit === "") return (val === undefined || val === null || val === "") ? "--" : val;
    return formatValue(val, unit) + " " + displayUnit(unit);
}

function displayUnit(unit) {
    if (unit === "pct") return "%";
    if (unit === "deg") return "\u00B0";
    if (unit === "C") return "\u00B0C";
    return unit;
}

function isDirectionKey(key) {
    return key === "nav.heading" ||
           key === "nav.course_over_ground" ||
           key === "environment.wind.angle_apparent" ||
           key === "environment.wind.angle_true";
}

// Complete gauge catalog with all sailboat instruments
var gaugeCatalog = [
    // Empty selection
    { key: "", category: qsTr("Valg"), label: qsTr("(tom)"), display: qsTr("Valg / (tom)"), unit: "", min: 0, max: 1 },

    // Motor / Engine
    { key: "engine.rpm", category: qsTr("Motor"), label: qsTr("RPM"), display: qsTr("Motor / RPM"), unit: "rpm", min: 0, max: 4000 },
    { key: "engine.temperature", category: qsTr("Motor"), label: qsTr("Motortemp"), display: qsTr("Motor / Motortemp"), unit: "C", min: 0, max: 120 },
    { key: "engine.oil_pressure", category: qsTr("Motor"), label: qsTr("Oljetrykk"), display: qsTr("Motor / Oljetrykk"), unit: "bar", min: 0, max: 10 },
    { key: "engine.alternator_voltage", category: qsTr("Motor"), label: qsTr("Ladespenning"), display: qsTr("Motor / Ladespenning"), unit: "V", min: 0, max: 16 },
    { key: "engine.hours", category: qsTr("Motor"), label: qsTr("Driftstimer"), display: qsTr("Motor / Driftstimer"), unit: "h", min: 0, max: 10000 },
    { key: "engine.coolant_temp", category: qsTr("Motor"), label: qsTr("Kj\u00F8lev\u00E6sketemp"), display: qsTr("Motor / Kj\u00F8lev\u00E6sketemp"), unit: "C", min: 0, max: 120 },

    // Battery / Batteri
    { key: "battery.house.voltage", category: qsTr("Batteri"), label: qsTr("Forbruksbatteri"), display: qsTr("Batteri / Forbruksbatteri"), unit: "V", min: 0, max: 16 },
    { key: "battery.start.voltage", category: qsTr("Batteri"), label: qsTr("Startbatteri"), display: qsTr("Batteri / Startbatteri"), unit: "V", min: 0, max: 16 },
    { key: "battery.charge_current", category: qsTr("Batteri"), label: qsTr("Ladestr\u00F8m"), display: qsTr("Batteri / Ladestr\u00F8m"), unit: "A", min: -50, max: 200 },
    { key: "battery.discharge_current", category: qsTr("Batteri"), label: qsTr("Forbruksstr\u00F8m"), display: qsTr("Batteri / Forbruksstr\u00F8m"), unit: "A", min: 0, max: 100 },
    { key: "battery.state_of_charge", category: qsTr("Batteri"), label: qsTr("Batteriniv\u00E5"), display: qsTr("Batteri / Batteriniv\u00E5"), unit: "pct", min: 0, max: 100 },
    { key: "battery.time_remaining", category: qsTr("Batteri"), label: qsTr("Tid igjen"), display: qsTr("Batteri / Tid igjen"), unit: "h", min: 0, max: 48 },

    // Tanks / Tanker
    { key: "tanks.fuel.level", category: qsTr("Tanker"), label: qsTr("Dieselniv\u00E5 (%)"), display: qsTr("Tanker / Dieselniv\u00E5 (%)"), unit: "pct", min: 0, max: 100 },
    { key: "tanks.fuel.volume", category: qsTr("Tanker"), label: qsTr("Dieselniv\u00E5 (L)"), display: qsTr("Tanker / Dieselniv\u00E5 (L)"), unit: "L", min: 0, max: 1000 },
    { key: "tanks.freshwater.level", category: qsTr("Tanker"), label: qsTr("Ferskvann (%)"), display: qsTr("Tanker / Ferskvann (%)"), unit: "pct", min: 0, max: 100 },
    { key: "tanks.freshwater.volume", category: qsTr("Tanker"), label: qsTr("Ferskvann (L)"), display: qsTr("Tanker / Ferskvann (L)"), unit: "L", min: 0, max: 1000 },
    { key: "tanks.blackwater.level", category: qsTr("Tanker"), label: qsTr("Septik (%)"), display: qsTr("Tanker / Septik (%)"), unit: "pct", min: 0, max: 100 },
    { key: "tanks.blackwater.volume", category: qsTr("Tanker"), label: qsTr("Septik (L)"), display: qsTr("Tanker / Septik (L)"), unit: "L", min: 0, max: 1000 },
    { key: "tanks.greywater.level", category: qsTr("Tanker"), label: qsTr("Gr\u00E5vann (%)"), display: qsTr("Tanker / Gr\u00E5vann (%)"), unit: "pct", min: 0, max: 100 },

    // Navigation / Navigasjon
    { key: "nav.depth", category: qsTr("Navigasjon"), label: qsTr("Dybde"), display: qsTr("Navigasjon / Dybde"), unit: "m", min: 0, max: 200 },
    { key: "nav.speed_through_water", category: qsTr("Navigasjon"), label: qsTr("Fart gjennom vann"), display: qsTr("Navigasjon / Fart gjennom vann"), unit: "kn", min: 0, max: 30 },
    { key: "nav.speed_over_ground", category: qsTr("Navigasjon"), label: qsTr("Fart over grunn"), display: qsTr("Navigasjon / Fart over grunn"), unit: "kn", min: 0, max: 30 },
    { key: "nav.course_over_ground", category: qsTr("Navigasjon"), label: qsTr("Kurs over grunn"), display: qsTr("Navigasjon / Kurs over grunn"), unit: "deg", min: 0, max: 360 },
    { key: "nav.water_temperature", category: qsTr("Navigasjon"), label: qsTr("Vanntemperatur"), display: qsTr("Navigasjon / Vanntemperatur"), unit: "C", min: -5, max: 35 },

    // Wind / Vind
    { key: "environment.wind.speed", category: qsTr("Vind"), label: qsTr("Vindhastighet"), display: qsTr("Vind / Vindhastighet"), unit: "kn", min: 0, max: 60 },
    { key: "environment.wind.angle_apparent", category: qsTr("Vind"), label: qsTr("Vindretning (relativ)"), display: qsTr("Vind / Vindretning (relativ)"), unit: "deg", min: 0, max: 360 },
    { key: "environment.wind.angle_true", category: qsTr("Vind"), label: qsTr("Vindretning (ekte)"), display: qsTr("Vind / Vindretning (ekte)"), unit: "deg", min: 0, max: 360 },
    { key: "environment.wind.speed_true", category: qsTr("Vind"), label: qsTr("Vindhastighet (ekte)"), display: qsTr("Vind / Vindhastighet (ekte)"), unit: "kn", min: 0, max: 60 },

    // Direction / Retning
    { key: "nav.heading", category: qsTr("Retning"), label: qsTr("Kompasskurs"), display: qsTr("Retning / Kompasskurs"), unit: "deg", min: 0, max: 360 },
    { key: "navigation.attitude.roll", category: qsTr("Retning"), label: qsTr("Krengning"), display: qsTr("Retning / Krengning"), unit: "deg", min: -45, max: 45 },
    { key: "navigation.attitude.pitch", category: qsTr("Retning"), label: qsTr("Trim"), display: qsTr("Retning / Trim"), unit: "deg", min: -30, max: 30 },
    { key: "autopilot.rudder_angle", category: qsTr("Retning"), label: qsTr("Rorvinkel"), display: qsTr("Retning / Rorvinkel"), unit: "deg", min: -45, max: 45 },

    // Environment / Milj\u00F8
    { key: "environment.air.temperature", category: qsTr("Milj\u00F8"), label: qsTr("Lufttemperatur"), display: qsTr("Milj\u00F8 / Lufttemperatur"), unit: "C", min: -20, max: 40 },
    { key: "environment.air.humidity", category: qsTr("Milj\u00F8"), label: qsTr("Luftfuktighet"), display: qsTr("Milj\u00F8 / Luftfuktighet"), unit: "pct", min: 0, max: 100 },
    { key: "environment.air.pressure", category: qsTr("Milj\u00F8"), label: qsTr("Barometer"), display: qsTr("Milj\u00F8 / Barometer"), unit: "hPa", min: 900, max: 1100 },
    { key: "environment.water.temperature", category: qsTr("Milj\u00F8"), label: qsTr("Vanntemperatur"), display: qsTr("Milj\u00F8 / Vanntemperatur"), unit: "C", min: -5, max: 35 }
];

function getGaugeMeta(key) {
    for (var i = 0; i < gaugeCatalog.length; i++) {
        if (gaugeCatalog[i].key === key) return gaugeCatalog[i];
    }
    return gaugeCatalog[0];
}

function getCatalog() {
    return gaugeCatalog;
}

function gaugeIndexForKey(key) {
    for (var i = 0; i < gaugeCatalog.length; i++) {
        if (gaugeCatalog[i].key === key) {
            return i;
        }
    }
    return 0;
}

function resolve(key, client, bridgeSignals) {
    if (!key) return "--";

    function bv(k, fallback) {
        if (!bridgeSignals) return fallback;
        for (var i = 0; i < bridgeSignals.length; i++) {
            if (bridgeSignals[i].name === k) return bridgeSignals[i].value;
        }
        return fallback;
    }

    var map = {
        // Navigation
        "nav.depth": function() { return client && client.navDepth !== 0 ? client.navDepth : bv(key, "--"); },
        "nav.speed_over_ground": function() { return bv(key, client ? client.navSpeed : "--"); },
        "nav.speed_through_water": function() { return bv(key, client ? client.navSpeed : "--"); },
        "nav.heading": function() { return client && client.navHeading !== 0 ? client.navHeading : bv(key, "--"); },
        "nav.course_over_ground": function() { return bv(key, client ? client.navHeading : "--"); },
        "nav.water_temperature": function() { return bv(key, bv("water_temp_c", "--")); },

        // Wind
        "environment.wind.speed": function() { return bv(key, client ? client.navWind : "--"); },
        "environment.wind.speed_true": function() { return bv(key, bv("wind_speed_true", "--")); },
        "environment.wind.angle_true": function() { return bv(key, bv("wind_dir_true", "--")); },
        "environment.wind.angle_apparent": function() { return bv(key, bv("wind_dir", "--")); },

        // Environment
        "environment.air.temperature": function() { return bv(key, bv("sense_temp_c", "--")); },
        "environment.air.humidity": function() { return bv(key, bv("sense_humidity_pct", "--")); },
        "environment.air.pressure": function() { return bv(key, bv("sense_pressure_hpa", "--")); },
        "environment.water.temperature": function() { return bv(key, bv("water_temp_c", "--")); },

        // Attitude
        "navigation.attitude.roll": function() { return bv(key, bv("sense_roll_deg", "--")); },
        "navigation.attitude.pitch": function() { return bv(key, bv("sense_pitch_deg", "--")); },

        // Engine
        "engine.rpm": function() { return bv(key, bv("rpm", "--")); },
        "engine.temperature": function() { return bv(key, bv("temp_c", "--")); },
        "engine.oil_pressure": function() { return bv(key, bv("oil_pressure_bar", "--")); },
        "engine.alternator_voltage": function() { return bv(key, bv("alternator_v", "--")); },
        "engine.hours": function() { return bv(key, bv("engine_hours", "--")); },
        "engine.coolant_temp": function() { return bv(key, bv("coolant_temp_c", "--")); },

        // Battery
        "battery.house.voltage": function() { return bv(key, bv("battery_voltage", "--")); },
        "battery.start.voltage": function() { return bv(key, bv("start_battery_v", "--")); },
        "battery.charge_current": function() { return bv(key, bv("current_a", "--")); },
        "battery.discharge_current": function() { return bv(key, bv("discharge_a", "--")); },
        "battery.state_of_charge": function() { return bv(key, bv("battery_soc_pct", "--")); },
        "battery.time_remaining": function() { return bv(key, bv("battery_time_h", "--")); },

        // Tanks
        "tanks.fuel.level": function() { return bv(key, bv("fuel_pct", "--")); },
        "tanks.fuel.volume": function() { return bv(key, bv("fuel_liters", "--")); },
        "tanks.freshwater.level": function() { return bv(key, bv("water_pct", "--")); },
        "tanks.freshwater.volume": function() { return bv(key, bv("water_liters", "--")); },
        "tanks.blackwater.level": function() { return bv(key, bv("blackwater_pct", "--")); },
        "tanks.blackwater.volume": function() { return bv(key, bv("blackwater_liters", "--")); },
        "tanks.greywater.level": function() { return bv(key, bv("greywater_pct", "--")); },

        // Autopilot
        "autopilot.rudder_angle": function() { return bv(key, bv("rudder_deg", "--")); }
    };

    if (map[key]) return map[key]();
    return bv(key, "--");
}
