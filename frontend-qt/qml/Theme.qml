import QtQuick 2.15

QtObject {
    property bool nightMode: false

    readonly property color bg: nightMode ? "#120505" : "#07141d"
    readonly property color bgMid: nightMode ? "#1a0707" : "#0b1a25"
    readonly property color bgLight: nightMode ? "#240909" : "#0f2230"
    readonly property color panel: nightMode ? "#1c0a0a" : "#0d1b26"
    readonly property color panelSoft: nightMode ? "#150808" : "#0a1620"
    readonly property color accent: nightMode ? "#ff3b3b" : "#49e2ff"
    readonly property color accentSoft: nightMode ? "#3b0f0f" : "#10343f"
    readonly property color text: nightMode ? "#ffb3b3" : "#e3f7ff"
    readonly property color muted: nightMode ? "#b36060" : "#7fa0b4"
    readonly property color warn: nightMode ? "#ff6b6b" : "#f5b14c"
    readonly property color danger: nightMode ? "#ff3b3b" : "#f07070"
    readonly property color glow: nightMode ? "#ff3b3b" : "#1bd4ff"
    readonly property color ice: nightMode ? "#ff8080" : "#8ad4ff"
    readonly property color grid: nightMode ? "#3a0f0f" : "#143142"
    readonly property color panelEdge: nightMode ? "#5a1a1a" : "#1b3a4a"
    readonly property int radiusLg: 18
    readonly property int radiusMd: 12
    readonly property int radiusSm: 8
}
