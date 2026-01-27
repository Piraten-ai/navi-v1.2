.pragma library

var gaugeCatalog = [
    { key: "", label: "(tom)", unit: "", min: 0, max: 1 },
    { key: "engine.rpm", label: "RPM", unit: "rpm", min: 0, max: 4000 },
    { key: "engine.temperature", label: "Motortemperatur", unit: "°C", min: 0, max: 120 },
    { key: "engine.oil_pressure", label: "Oljetrykk", unit: "bar", min: 0, max: 10 },
    { key: "engine.alternator_voltage", label: "Ladespenning", unit: "V", min: 0, max: 16 },
    { key: "battery.start.voltage", label: "Batterispenning (start)", unit: "V", min: 0, max: 16 },
    { key: "battery.house.voltage", label: "Batterispenning (forbruk)", unit: "V", min: 0, max: 16 },
    { key: "battery.charge_current", label: "LadestrÃ¸m", unit: "A", min: -50, max: 200 },
    { key: "tanks.fuel.level", label: "DieselnivÃ¥", unit: "%", min: 0, max: 100 },
    { key: "tanks.freshwater.level", label: "FerskvannsnivÃ¥", unit: "%", min: 0, max: 100 },
    { key: "tanks.blackwater.level", label: "SeptiknivÃ¥", unit: "%", min: 0, max: 100 },
    { key: "tanks.greywater.level", label: "GrÃ¥vannsnivÃ¥", unit: "%", min: 0, max: 100 },
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
];

function bridgeValue(client, key, fallback) {
    var signals = client && client.bridgeSignals ? client.bridgeSignals : [];
    for (var i = 0; i < signals.length; i++) {
        if (signals[i].name === key) {
            return signals[i].value;
        }
    }
    return fallback;
}

var signalResolvers = {
    "nav.depth": function(client) {
        return client.navDepth !== 0 ? client.navDepth : bridgeValue(client, "nav.depth", "--");
    },
    "nav.speed_through_water": function(client) {
        return bridgeValue(client, "nav.speed_through_water", client.navSpeed);
    },
    "nav.speed_over_ground": function(client) {
        return bridgeValue(client, "nav.speed_over_ground", client.navSpeed);
    },
    "nav.course_over_ground": function(client) {
        return bridgeValue(client, "nav.course_over_ground", "--");
    },
    "nav.heading": function(client) {
        return client.navHeading !== 0 ? client.navHeading : bridgeValue(client, "nav.heading", "--");
    },
    "environment.wind.speed": function(client) {
        return bridgeValue(client, "environment.wind.speed", client.navWind);
    },
    "environment.wind.angle_apparent": function(client) {
        return bridgeValue(client, "environment.wind.angle_apparent", bridgeValue(client, "wind_dir", "--"));
    },
    "environment.wind.angle_true": function(client) {
        return bridgeValue(client, "environment.wind.angle_true", bridgeValue(client, "wind_dir_true", "--"));
    },
    "environment.air.temperature": function(client) {
        return bridgeValue(client, "environment.air.temperature", bridgeValue(client, "sense_temp_c", "--"));
    },
    "environment.air.humidity": function(client) {
        return bridgeValue(client, "environment.air.humidity", bridgeValue(client, "sense_humidity_pct", "--"));
    },
    "environment.air.pressure": function(client) {
        return bridgeValue(client, "environment.air.pressure", bridgeValue(client, "sense_pressure_hpa", "--"));
    },
    "navigation.attitude.roll": function(client) {
        return bridgeValue(client, "navigation.attitude.roll", bridgeValue(client, "sense_roll_deg", "--"));
    },
    "engine.rpm": function(client) {
        return bridgeValue(client, "engine.rpm", bridgeValue(client, "rpm", "--"));
    },
    "engine.temperature": function(client) {
        return bridgeValue(client, "engine.temperature", bridgeValue(client, "temp_c", "--"));
    },
    "engine.oil_pressure": function(client) {
        return bridgeValue(client, "engine.oil_pressure", "--");
    },
    "engine.alternator_voltage": function(client) {
        return bridgeValue(client, "engine.alternator_voltage", "--");
    },
    "battery.start.voltage": function(client) {
        return bridgeValue(client, "battery.start.voltage", "--");
    },
    "battery.house.voltage": function(client) {
        return bridgeValue(client, "battery.house.voltage", bridgeValue(client, "battery_voltage", "--"));
    },
    "battery.charge_current": function(client) {
        return bridgeValue(client, "battery.charge_current", bridgeValue(client, "current_a", "--"));
    },
    "tanks.fuel.level": function(client) {
        return bridgeValue(client, "tanks.fuel.level", bridgeValue(client, "fuel_pct", "--"));
    },
    "tanks.freshwater.level": function(client) {
        return bridgeValue(client, "tanks.freshwater.level", "--");
    },
    "tanks.blackwater.level": function(client) {
        return bridgeValue(client, "tanks.blackwater.level", "--");
    },
    "tanks.greywater.level": function(client) {
        return bridgeValue(client, "tanks.greywater.level", "--");
    },
    "environment.water.temperature": function(client) {
        return bridgeValue(client, "environment.water.temperature", "--");
    },
    "steering.rudder_angle": function(client) {
        return bridgeValue(client, "steering.rudder_angle", "--");
    }
};

function resolveSignal(key, client) {
    if (!key || key === "") {
        return "--";
    }
    var resolver = signalResolvers[key];
    if (resolver) {
        return resolver(client);
    }
    return bridgeValue(client, key, "--");
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
