import QtQuick 2.15
pragma Singleton

QtObject {
    property bool nightMode: true
    property bool redMode: false
    // Global UI scale. Set from `Main.qml` based on window size.
    property real uiScale: 1.0

    // Helpers: scale pixels/font sizes consistently.
    function px(v) {
        var s = uiScale;
        if (s === undefined || isNaN(s) || !isFinite(s) || s <= 0) s = 1.0;
        var out = Math.round(v * s);
        // Avoid NaN leaking into width/height/margins.
        if (out === undefined || isNaN(out) || !isFinite(out)) return 0;
        return out;
    }
    function clamp(v, lo, hi) { return Math.max(lo, Math.min(hi, v)); }

    // Font loaders
    // Use resolved URLs so this works both from disk and from the QML module resource prefix.
    property FontLoader fontDisplayLoader: FontLoader { source: Qt.resolvedUrl("fonts/Rajdhani-SemiBold.ttf") }
    property FontLoader fontBodyLoader: FontLoader { source: Qt.resolvedUrl("fonts/SpaceGrotesk.ttf") }
    property FontLoader fontMonoLoader: FontLoader { source: Qt.resolvedUrl("fonts/JetBrainsMono-Regular.ttf") }

    readonly property string fontDisplay: fontDisplayLoader.name !== "" ? fontDisplayLoader.name : "Sans Serif"
    readonly property string fontBody: fontBodyLoader.name !== "" ? fontBodyLoader.name : "Sans Serif"
    readonly property string fontMono: fontMonoLoader.name !== "" ? fontMonoLoader.name : "Monospace"

    // Arctic Blue Theme - Primary Colors (matching logo)
    readonly property color deepBlack: "#03070c"
    readonly property color deepNavy: "#050a12"
    readonly property color slate: "#0b1420"
    readonly property color darkSlate: "#081018"
    readonly property color mist: "#162333"

    // Accent Colors - Arctic/Ice theme
    readonly property color arcticGlow: "#4fe6ff"
    readonly property color arcticCyan: "#00d4ff"
    readonly property color ionBlue: "#2fc0e6"
    readonly property color iceBlue: "#7aeeff"
    readonly property color frostWhite: "#b8f4ff"

    // Secondary accents
    readonly property color ember: "#f3b43e"
    readonly property color gold: "#ffd700"
    readonly property color alertRed: "#ff4d5a"
    readonly property color warningOrange: "#ff8c42"
    readonly property color successGreen: "#4eff91"

    // Text colors
    readonly property color mutedText: "#7d9bb1"
    readonly property color whiteText: "#e7f5ff"
    readonly property color brightText: "#ffffff"

    // Night/Red mode colors
    readonly property color nightBlack: "#040304"
    readonly property color nightRed: "#b40010"
    readonly property color dimRed: "#3b0c10"
    readonly property color bloodRed: "#8b0000"

    // Dynamic theme colors based on mode
    readonly property color bg: redMode ? nightBlack : deepBlack
    readonly property color bgMid: redMode ? Qt.darker(nightBlack, 1.1) : deepNavy
    readonly property color bgLight: redMode ? dimRed : darkSlate

    readonly property color panel: redMode ? Qt.rgba(0.18, 0.02, 0.04, 0.6) : slate
    readonly property color panelSoft: redMode ? Qt.rgba(0.12, 0.02, 0.03, 0.8) : Qt.rgba(0.043, 0.078, 0.125, 0.85)
    readonly property color panelBorder: redMode ? dimRed : ionBlue
    readonly property color panelEdge: redMode ? Qt.rgba(0.23, 0.05, 0.06, 0.6) : Qt.rgba(0.18, 0.75, 0.9, 0.3)

    readonly property color textMain: redMode ? nightRed : whiteText
    readonly property color textMuted: redMode ? dimRed : mutedText
    readonly property color textBright: redMode ? nightRed : brightText

    readonly property color accent: redMode ? nightRed : arcticGlow
    readonly property color accentSoft: redMode ? Qt.rgba(nightRed.r, nightRed.g, nightRed.b, 0.3) : Qt.rgba(arcticGlow.r, arcticGlow.g, arcticGlow.b, 0.3)
    readonly property color accentBright: redMode ? bloodRed : arcticCyan

    readonly property color indicator: redMode ? nightRed : arcticGlow
    readonly property color indicatorGlow: redMode ? Qt.rgba(nightRed.r, nightRed.g, nightRed.b, 0.5) : Qt.rgba(arcticGlow.r, arcticGlow.g, arcticGlow.b, 0.5)

    readonly property color danger: alertRed
    readonly property color warning: warningOrange
    readonly property color success: successGreen

    // Gauge specific colors
    readonly property color gaugeTrack: redMode ? Qt.rgba(0.3, 0.1, 0.1, 0.3) : Qt.rgba(0.3, 0.5, 0.6, 0.2)
    readonly property color gaugeProgress: redMode ? nightRed : arcticGlow
    readonly property color gaugeGlow: redMode ? Qt.rgba(nightRed.r, nightRed.g, nightRed.b, 0.6) : Qt.rgba(arcticGlow.r, arcticGlow.g, arcticGlow.b, 0.6)
    readonly property color gaugeTick: redMode ? dimRed : Qt.rgba(0.5, 0.8, 0.9, 0.4)
    readonly property color gaugeNeedle: redMode ? nightRed : arcticCyan
    readonly property color gaugeCenter: redMode ? bloodRed : iceBlue

    // Map overlay colors
    readonly property color mapOverlay: redMode ? Qt.rgba(0.3, 0, 0, 0.35) : Qt.rgba(0, 0.1, 0.15, 0.2)
    readonly property color mapGrid: redMode ? dimRed : Qt.rgba(arcticGlow.r, arcticGlow.g, arcticGlow.b, 0.15)

    // Border radius
    readonly property int radiusSm: 6
    readonly property int radiusMd: 12
    readonly property int radiusLg: 18
    readonly property int radiusXl: 24

    // Glass effect
    readonly property real glassOpacity: redMode ? 0.0 : 0.88
    readonly property real glassBlur: 20

    // Shadows and glows
    readonly property color shadowColor: Qt.rgba(0, 0, 0, 0.5)
    readonly property color glowColor: redMode ? Qt.rgba(nightRed.r, nightRed.g, nightRed.b, 0.3) : Qt.rgba(arcticGlow.r, arcticGlow.g, arcticGlow.b, 0.3)

    // Animation durations
    readonly property int animFast: 150
    readonly property int animNormal: 300
    readonly property int animSlow: 500

    // Neon glow intensities
    readonly property real neonGlowStrength: 0.8
    readonly property real neonGlowRadius: 15
    readonly property real neonPulseMin: 0.4
    readonly property real neonPulseMax: 1.0

    // 3D/Depth effects
    readonly property color bevelLight: Qt.rgba(1, 1, 1, 0.15)
    readonly property color bevelDark: Qt.rgba(0, 0, 0, 0.4)
    readonly property real depthShadowOffset: 3

    // Glow colors for different states
    readonly property color glowActive: redMode ? Qt.rgba(1, 0.2, 0.2, 0.8) : Qt.rgba(0.3, 0.9, 1, 0.8)
    readonly property color glowHover: redMode ? Qt.rgba(1, 0.3, 0.3, 0.5) : Qt.rgba(0.4, 0.95, 1, 0.5)
    readonly property color glowIdle: redMode ? Qt.rgba(0.6, 0.1, 0.1, 0.3) : Qt.rgba(0.2, 0.7, 0.9, 0.3)

    // Gradient presets for 3D look
    readonly property var panelGradient: [
        Qt.rgba(0.08, 0.12, 0.18, 0.95),
        Qt.rgba(0.04, 0.06, 0.10, 0.98)
    ]

    readonly property var buttonGradient: [
        Qt.rgba(0.15, 0.25, 0.35, 0.9),
        Qt.rgba(0.08, 0.12, 0.18, 0.95)
    ]

    readonly property var gaugeRingGradient: [
        Qt.rgba(arcticGlow.r, arcticGlow.g, arcticGlow.b, 0.9),
        Qt.rgba(ionBlue.r, ionBlue.g, ionBlue.b, 0.4)
    ]

    // Backwards-compatible aliases
    readonly property color text: textMain
    readonly property color muted: textMuted
    readonly property color warn: danger
    readonly property color glow: accent
    readonly property color ice: indicator
    readonly property color grid: mutedText

    // Gradient helpers for gauges
    function gaugeGradient(startColor, endColor) {
        return [
            Qt.rgba(startColor.r, startColor.g, startColor.b, 0.8),
            Qt.rgba(endColor.r, endColor.g, endColor.b, 1.0)
        ];
    }

    // Warning level colors for gauges
    function levelColor(value, min, max, warnLow, warnHigh) {
        var pct = (value - min) / (max - min);
        if (warnLow !== undefined && pct < warnLow) return warning;
        if (warnHigh !== undefined && pct > warnHigh) return danger;
        return accent;
    }
}
