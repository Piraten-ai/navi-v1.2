.pragma library

var defaults = {
    nightMode: false,
    showMap: true,
    showNavi: true,
    showCompass: true,
    showWind: true,
    showAutopilot: true,
    mapSource: "local",
    localTileUrl: "",
    trackLength: 120,
    wikiPath: "",
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

function parseStore(json) {
    try {
        var obj = JSON.parse(json);
        if (obj && obj.profiles && obj.data) return obj;
    } catch (e) {}
    return { profiles: ["default"], data: { "default": {} } };
}

function getProfileNames(json) {
    var store = parseStore(json);
    return store.profiles || ["default"];
}

function saveCurrentToProfile(uiSettings, profileName) {
    if (!uiSettings) {
        return JSON.stringify(parseStore("{}"));
    }
    var store = parseStore(uiSettings.profilesJson);

    var data = {};
    for (var key in defaults) {
        if (uiSettings.hasOwnProperty(key)) {
            data[key] = uiSettings[key];
        }
    }

    store.data[profileName] = data;

    if (store.profiles.indexOf(profileName) === -1) {
        store.profiles.push(profileName);
    }

    return JSON.stringify(store);
}

function applyProfile(uiSettings, client, profileName) {
    if (!uiSettings) {
        return;
    }
    var store = parseStore(uiSettings.profilesJson);
    var data = store.data[profileName] || {};

    for (var key in defaults) {
        var val = data.hasOwnProperty(key) ? data[key] : defaults[key];
        if (key === "localTileUrl" && (!val || val === "")) {
            val = uiSettings.localTileUrl;
        }
        if (uiSettings.hasOwnProperty(key)) {
            uiSettings[key] = val;
        }
    }

    if (client) {
        if (uiSettings.wikiPath) client.wikiPath = uiSettings.wikiPath;
        if (client.loadWiki) client.loadWiki();
    }
}

function deleteProfile(json, profileName) {
    if (profileName === "default") return json;
    var store = parseStore(json);

    var idx = store.profiles.indexOf(profileName);
    if (idx !== -1) {
        store.profiles.splice(idx, 1);
        delete store.data[profileName];
    }
    return JSON.stringify(store);
}
