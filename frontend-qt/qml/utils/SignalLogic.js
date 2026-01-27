.pragma library

function formatValue(val, unit) {
    if (val === undefined || val === null) return "--";
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
    if (unit === "deg") return "deg";
    if (unit === "C") return "C";
    return unit;
}

function isDirectionKey(key) {
    return key === "nav.heading" ||
           key === "nav.course_over_ground" ||
           key === "environment.wind.angle_apparent" ||
           key === "environment.wind.angle_true";
}

var gaugeCatalog = [
    { key: "", category: qsTr("Valg"), label: qsTr("(tom)"), display: qsTr("Valg / (tom)"), unit: "", min: 0, max: 1 },

    { key: "engine.rpm", category: qsTr("Motor"), label: qsTr("RPM"), display: qsTr("Motor / RPM"), unit: "rpm", min: 0, max: 4000 },
    { key: "engine.temperature", category: qsTr("Motor"), label: qsTr("Motortemp"), display: qsTr("Motor / Motortemp"), unit: "C", min: 0, max: 120 },
    { key: "engine.oil_pressure", category: qsTr("Motor"), label: qsTr("Oljetrykk"), display: qsTr("Motor / Oljetrykk"), unit: "bar", min: 0, max: 10 },
    { key: "engine.alternator_voltage", category: qsTr("Motor"), label: qsTr("Ladespenning"), display: qsTr("Motor / Ladespenning"), unit: "V", min: 0, max: 16 },

    { key: "battery.house.voltage", category: qsTr("Batteri"), label: qsTr("Batterispenning"), display: qsTr("Batteri / Batterispenning"), unit: "V", min: 0, max: 16 },
    { key: "battery.charge_current", category: qsTr("Batteri"), label: qsTr("Ladestrøm"), display: qsTr("Batteri / Ladestrøm"), unit: "A", min: -50, max: 200 },

    { key: "tanks.fuel.level", category: qsTr("Tanker"), label: qsTr("Dieselnivå (%)"), display: qsTr("Tanker / Dieselnivå (%)"), unit: "pct", min: 0, max: 100 },
    { key: "tanks.fuel.volume", category: qsTr("Tanker"), label: qsTr("Dieselnivå (L)"), display: qsTr("Tanker / Dieselnivå (L)"), unit: "L", min: 0, max: 1000 },
    { key: "tanks.freshwater.level", category: qsTr("Tanker"), label: qsTr("Ferskvann (%)"), display: qsTr("Tanker / Ferskvann (%)"), unit: "pct", min: 0, max: 100 },
    { key: "tanks.freshwater.volume", category: qsTr("Tanker"), label: qsTr("Ferskvann (L)"), display: qsTr("Tanker / Ferskvann (L)"), unit: "L", min: 0, max: 1000 },
    { key: "tanks.blackwater.level", category: qsTr("Tanker"), label: qsTr("Septik (%)"), display: qsTr("Tanker / Septik (%)"), unit: "pct", min: 0, max: 100 },
    { key: "tanks.blackwater.volume", category: qsTr("Tanker"), label: qsTr("Septik (L)"), display: qsTr("Tanker / Septik (L)"), unit: "L", min: 0, max: 1000 },

    { key: "nav.depth", category: qsTr("Navigasjon"), label: qsTr("Dybde"), display: qsTr("Navigasjon / Dybde"), unit: "m", min: 0, max: 200 },
    { key: "nav.speed_through_water", category: qsTr("Navigasjon"), label: qsTr("Fart gjennom vann"), display: qsTr("Navigasjon / Fart gjennom vann"), unit: "kn", min: 0, max: 30 },
    { key: "nav.speed_over_ground", category: qsTr("Navigasjon"), label: qsTr("Fart over grunn"), display: qsTr("Navigasjon / Fart over grunn"), unit: "kn", min: 0, max: 30 },
    { key: "nav.course_over_ground", category: qsTr("Navigasjon"), label: qsTr("Kurs over grunn"), display: qsTr("Navigasjon / Kurs over grunn"), unit: "deg", min: 0, max: 360 },

    { key: "environment.wind.speed", category: qsTr("Vind"), label: qsTr("Vindhastighet"), display: qsTr("Vind / Vindhastighet"), unit: "kn", min: 0, max: 60 },
    { key: "environment.wind.angle_apparent", category: qsTr("Vind"), label: qsTr("Vindretning (relativ)"), display: qsTr("Vind / Vindretning (relativ)"), unit: "deg", min: 0, max: 360 },
    { key: "environment.wind.angle_true", category: qsTr("Vind"), label: qsTr("Vindretning (ekte)"), display: qsTr("Vind / Vindretning (ekte)"), unit: "deg", min: 0, max: 360 },

    { key: "nav.heading", category: qsTr("Retning"), label: qsTr("Kompasskurs"), display: qsTr("Retning / Kompasskurs"), unit: "deg", min: 0, max: 360 },
    { key: "navigation.attitude.roll", category: qsTr("Retning"), label: qsTr("Krengning / tilt"), display: qsTr("Retning / Krengning / tilt"), unit: "deg", min: -45, max: 45 },
    { key: "autopilot.rudder_angle", category: qsTr("Retning"), label: qsTr("Rorvinkel"), display: qsTr("Retning / Rorvinkel"), unit: "deg", min: -45, max: 45 },

    { key: "environment.air.temperature", category: qsTr("Miljø"), label: qsTr("Lufttemperatur"), display: qsTr("Miljø / Lufttemperatur"), unit: "C", min: -20, max: 40 },
    { key: "environment.air.humidity", category: qsTr("Miljø"), label: qsTr("Luftfuktighet"), display: qsTr("Miljø / Luftfuktighet"), unit: "pct", min: 0, max: 100 },
    { key: "environment.air.pressure", category: qsTr("Miljø"), label: qsTr("Barometer"), display: qsTr("Miljø / Barometer"), unit: "hPa", min: 900, max: 1100 }
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
        "nav.depth": function() { return client.navDepth !== 0 ? client.navDepth : bv(key, "--"); },
        "nav.speed_over_ground": function() { return bv(key, client.navSpeed); },
        "nav.heading": function() { return client.navHeading !== 0 ? client.navHeading : bv(key, "--"); },
        "environment.wind.speed": function() { return bv(key, client.navWind); },
        "environment.wind.angle_true": function() { return bv(key, bv("wind_dir_true", "--")); },
        "environment.wind.angle_apparent": function() { return bv(key, bv("wind_dir", "--")); },
        "nav.speed_through_water": function() { return bv(key, client.navSpeed); },
        "nav.course_over_ground": function() { return bv(key, "--"); },
        "environment.air.temperature": function() { return bv(key, bv("sense_temp_c", "--")); },
        "environment.air.humidity": function() { return bv(key, bv("sense_humidity_pct", "--")); },
        "environment.air.pressure": function() { return bv(key, bv("sense_pressure_hpa", "--")); },
        "navigation.attitude.roll": function() { return bv(key, bv("sense_roll_deg", "--")); },
        "engine.rpm": function() { return bv(key, bv("rpm", "--")); },
        "engine.temperature": function() { return bv(key, bv("temp_c", "--")); },
        "battery.house.voltage": function() { return bv(key, bv("battery_voltage", "--")); },
        "battery.charge_current": function() { return bv(key, bv("current_a", "--")); },
        "tanks.fuel.level": function() { return bv(key, bv("fuel_pct", "--")); },
        "tanks.fuel.volume": function() { return bv(key, bv("fuel_liters", "--")); },
        "tanks.freshwater.level": function() { return bv(key, bv("water_pct", "--")); },
        "tanks.freshwater.volume": function() { return bv(key, bv("water_liters", "--")); },
        "tanks.blackwater.level": function() { return bv(key, bv("blackwater_pct", "--")); },
        "tanks.blackwater.volume": function() { return bv(key, bv("blackwater_liters", "--")); },
        "autopilot.rudder_angle": function() { return bv(key, bv("rudder_deg", "--")); }
    };

    if (map[key]) return map[key]();
    return bv(key, "--");
}
