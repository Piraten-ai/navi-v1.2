import QtQuick 2.15
pragma Singleton

QtObject {
    property bool nightMode: true
    property bool redMode: false

    property FontLoader fontDisplayLoader: FontLoader { source: "qrc:/AadsUi/qml/fonts/Rajdhani-SemiBold.ttf" }
    property FontLoader fontBodyLoader: FontLoader { source: "qrc:/AadsUi/qml/fonts/SpaceGrotesk.ttf" }
    property FontLoader fontMonoLoader: FontLoader { source: "qrc:/AadsUi/qml/fonts/JetBrainsMono-Regular.ttf" }

    readonly property string fontDisplay: fontDisplayLoader.name !== "" ? fontDisplayLoader.name : "Sans Serif"
    readonly property string fontBody: fontBodyLoader.name !== "" ? fontBodyLoader.name : "Sans Serif"
    readonly property string fontMono: fontMonoLoader.name !== "" ? fontMonoLoader.name : "Monospace"

    readonly property color deepBlack: "#03070c"
    readonly property color slate: "#0b1420"
    readonly property color mist: "#162333"
    readonly property color arcticGlow: "#4fe6ff"
    readonly property color ionBlue: "#2fc0e6"
    readonly property color ember: "#f3b43e"
    readonly property color alertRed: "#ff4d5a"
    readonly property color mutedText: "#7d9bb1"
    readonly property color whiteText: "#e7f5ff"

    readonly property color nightBlack: "#040304"
    readonly property color nightRed: "#b40010"
    readonly property color dimRed: "#3b0c10"

    readonly property color bg: redMode ? nightBlack : deepBlack
    readonly property color panel: redMode ? Qt.rgba(0.18, 0.02, 0.04, 0.6) : slate
    readonly property color panelBorder: redMode ? dimRed : ionBlue

    readonly property color textMain: redMode ? nightRed : whiteText
    readonly property color textMuted: redMode ? dimRed : mutedText

    readonly property color accent: redMode ? nightRed : arcticGlow
    readonly property color indicator: redMode ? nightRed : arcticGlow
    readonly property color danger: alertRed

    readonly property int radiusSm: 6
    readonly property int radiusMd: 12
    readonly property int radiusLg: 18
    readonly property real glassOpacity: redMode ? 0.0 : 0.88

    // Backwards-compatible aliases for existing QML usage
    readonly property color bgMid: bg
    readonly property color bgLight: bg
    readonly property color panelSoft: panel
    readonly property color accentSoft: accent
    readonly property color text: textMain
    readonly property color muted: textMuted
    readonly property color warn: danger
    readonly property color glow: accent
    readonly property color ice: indicator
    readonly property color grid: mutedText
    readonly property color panelEdge: panelBorder
}
