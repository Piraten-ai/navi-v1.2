.pragma library

function addProfile(list, name) {
    if (list.indexOf(name) === -1) {
        list.push(name);
    }
    return list;
}

function ensureDefaults(data, profileName, defaultSettings) {
    if (!data[profileName]) {
        data[profileName] = defaultSettings;
    }
    return data;
}
