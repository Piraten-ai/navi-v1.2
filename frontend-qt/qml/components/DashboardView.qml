import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtMultimedia 6.2
import QtQuick.Shapes 1.15
import "../utils/SignalLogic.js" as Logic
import ".."

Item {
    id: root
    property var uiSettings
    property var aadsClient
    property string aadsLogoPath: ""
    property var trackPath
    property var navCoordinate
    property bool showCameraMain: false
    property var gaugeGrid: ({ rows: 3, cols: 2, cells: [] })
    property var naviPreview
    signal cameraViewRequested(bool useCamera)

    property string cameraName: uiSettings && uiSettings.cameraName ? uiSettings.cameraName : ""
    property bool cameraAvailable: mediaDevices.videoInputs.length > 0

    // Get values from backend
    property real heading: aadsClient ? aadsClient.navHeading : 0
    property real windAngle: 45
    property real windSpeed: 0.7
    property real boatSpeed: aadsClient ? aadsClient.navSpeed : 0

    readonly property bool showWindAutopilotGauge: uiSettings
                                                 ? (uiSettings.showAutopilot || uiSettings.showWind)
                                                 : true

    function findCameraDevice() {
        var inputs = mediaDevices.videoInputs;
        if (!cameraName || cameraName === "") {
            return inputs.length ? inputs[0] : null;
        }
        for (var i = 0; i < inputs.length; i++) {
            var desc = inputs[i].description || "";
            if (desc.indexOf(cameraName) !== -1) {
                return inputs[i];
            }
        }
        return inputs.length ? inputs[0] : null;
    }

    MediaDevices {
        id: mediaDevices
        onVideoInputsChanged: {
            mainCamera.cameraDevice = root.findCameraDevice();
            if (root.cameraAvailable) mainCamera.start();
        }
    }

    Camera {
        id: mainCamera
        cameraDevice: root.findCameraDevice()
        onCameraDeviceChanged: { if (root.cameraAvailable) start(); }
    }

    CaptureSession {
        id: cameraSession
        camera: mainCamera
        videoOutput: cameraOutput
    }

    Component.onCompleted: {
        if (cameraAvailable) mainCamera.start();
    }

    // Grid properties
    readonly property int gridRows: (gaugeGrid && gaugeGrid.rows) ? gaugeGrid.rows : 3
    readonly property int gridCols: (gaugeGrid && gaugeGrid.cols) ? gaugeGrid.cols : 2
    readonly property var gridCells: (gaugeGrid && gaugeGrid.cells && gaugeGrid.cells.length > 0)
                                     ? gaugeGrid.cells
                                     : ["engine.rpm", "battery.house.voltage", "tanks.fuel.level", "nav.speed_over_ground", "nav.depth", "engine.temperature"]

    // Responsive sizing based on window size + Theme.uiScale
    function clamp(v, lo, hi) { return Math.max(lo, Math.min(hi, v)); }
    readonly property int px8: Theme.px(8)
    readonly property int px6: Theme.px(6)
    readonly property int topRowH: clamp(Math.round(height * 0.28), Theme.px(160), Theme.px(260))
    readonly property int cameraW: clamp(Math.round(width * 0.22), Theme.px(240), Theme.px(360))
    readonly property int logoSize: clamp(Math.round(topRowH * 0.9), Theme.px(140), Theme.px(210))
    readonly property int gaugePanelW: clamp(Math.round(width * 0.20), Theme.px(220), Theme.px(340))
    readonly property int naviW: clamp(Math.round(width * 0.26), Theme.px(220), Theme.px(340))
    readonly property int naviH: clamp(Math.round(height * 0.18), Theme.px(90), Theme.px(150))

    ColumnLayout {
        anchors.fill: parent
        spacing: Theme.px(8)

        // ========== TOP ROW - Camera, Autopilot, Logo ==========
        RowLayout {
            Layout.fillWidth: true
            Layout.preferredHeight: topRowH
            // Hard clamp so this row can't "eat" the whole dashboard.
            Layout.minimumHeight: topRowH
            Layout.maximumHeight: topRowH
            Layout.fillHeight: false
            spacing: Theme.px(8)

            // Camera feed
            Rectangle {
                Layout.preferredWidth: root.showCameraMain ? cameraW : 0
                Layout.minimumWidth: 0
                Layout.maximumWidth: root.showCameraMain ? cameraW : 0
                Layout.fillHeight: true
                visible: root.showCameraMain
                radius: Theme.radiusMd
                color: Qt.rgba(0.02, 0.04, 0.06, 0.95)
                border.color: Theme.panelEdge
                border.width: 1
                clip: true

                VideoOutput {
                    id: cameraOutput
                    anchors.fill: parent
                    anchors.margins: 2
                    fillMode: VideoOutput.PreserveAspectCrop
                    visible: cameraAvailable
                }

                // No camera placeholder
                Column {
                    anchors.centerIn: parent
                    spacing: Theme.px(8)
                    visible: !cameraAvailable

                    Image {
                        anchors.horizontalCenter: parent.horizontalCenter
                        width: Theme.px(60)
                        height: Theme.px(60)
                        source: aadsLogoPath ? "file:///" + aadsLogoPath : ""
                        fillMode: Image.PreserveAspectFit
                        opacity: 0.5
                        visible: aadsLogoPath !== ""
                    }

                    Text {
                        anchors.horizontalCenter: parent.horizontalCenter
                        text: "CAMERA OFFLINE"
                        color: Theme.muted
                        font.pixelSize: Theme.px(11)
                        font.family: Theme.fontMono
                    }
                }

                // Label
                Rectangle {
                    anchors.top: parent.top
                    anchors.left: parent.left
                    anchors.margins: Theme.px(6)
                    height: Theme.px(18)
                    width: camLabel.width + Theme.px(12)
                    radius: height / 2
                    color: Qt.rgba(0, 0, 0, 0.7)
                    border.color: cameraAvailable ? Theme.success : Theme.warning

                    Text {
                        id: camLabel
                        anchors.centerIn: parent
                        text: cameraAvailable ? "LIVE" : "OFF"
                        color: cameraAvailable ? Theme.success : Theme.warning
                        font.pixelSize: Theme.px(8)
                        font.family: Theme.fontMono
                        font.bold: true
                    }
                }
            }

            // Wind/Autopilot Garmin-style gauge
            WindAutopilotGauge {
                Layout.fillWidth: true
                Layout.fillHeight: true
                visible: root.showWindAutopilotGauge
                heading: root.heading
                windAngle: root.windAngle
                windSpeed: root.windSpeed
                boatSpeed: root.boatSpeed
                mode: "Wind Hold"
                status: aadsClient && aadsClient.autopilotStatus ? aadsClient.autopilotStatus : "Standby"
                autopilotActive: aadsClient && aadsClient.autopilotStatus === "active"
            }

            // Logo/Compass - smaller, fixed size
            Rectangle {
                Layout.preferredWidth: logoSize
                Layout.preferredHeight: logoSize
                Layout.alignment: Qt.AlignVCenter
                radius: width / 2
                color: Qt.rgba(0.02, 0.04, 0.06, 0.9)
                border.color: Theme.panelEdge
                border.width: 2

                // Glow ring
                Rectangle {
                    anchors.fill: parent
                    anchors.margins: -3
                    radius: width / 2
                    color: "transparent"
                    border.color: Theme.glowActive
                    border.width: 2
                    opacity: 0.4
                }

                // Tick marks
                Repeater {
                    model: 12
                    Rectangle {
                        property real angle: index * 30
                        property bool isCardinal: index % 3 === 0
                        x: parent.width / 2 + Math.sin(angle * Math.PI / 180) * (parent.width / 2 - 15) - width / 2
                        y: parent.height / 2 - Math.cos(angle * Math.PI / 180) * (parent.height / 2 - 15) - height / 2
                        width: isCardinal ? 2 : 1
                        height: Theme.px(isCardinal ? 10 : 5)
                        color: isCardinal ? Theme.accent : Theme.muted
                        rotation: angle
                        transformOrigin: Item.Center
                    }
                }

                // N/S/E/W labels
                Repeater {
                    model: [{ l: "N", a: 0 }, { l: "E", a: 90 }, { l: "S", a: 180 }, { l: "W", a: 270 }]
                    Text {
                        property real rad: modelData.a * Math.PI / 180
                        x: parent.width / 2 + Math.sin(rad) * (parent.width / 2 - 28) - width / 2
                        y: parent.height / 2 - Math.cos(rad) * (parent.height / 2 - 28) - height / 2
                        text: modelData.l
                        color: modelData.l === "N" ? Theme.danger : Theme.textMain
                        font.pixelSize: Theme.px(12)
                        font.family: Theme.fontMono
                        font.bold: true
                    }
                }

                // Rotating logo
                Item {
                    anchors.centerIn: parent
                    width: parent.width * 0.5
                    height: width
                    rotation: -root.heading
                    Behavior on rotation { NumberAnimation { duration: 400 } }

                    Image {
                        anchors.fill: parent
                        source: aadsLogoPath ? "file:///" + aadsLogoPath : ""
                        fillMode: Image.PreserveAspectFit
                        visible: aadsLogoPath !== ""
                        opacity: 0.85
                    }

                    // Fallback arrow
                    Shape {
                        anchors.fill: parent
                        visible: aadsLogoPath === ""
                        ShapePath {
                            fillColor: Theme.danger
                            strokeColor: "transparent"
                            startX: parent.width / 2; startY: 5
                            PathLine { x: parent.width / 2 + 8; y: parent.height / 2 }
                            PathLine { x: parent.width / 2 - 8; y: parent.height / 2 }
                            PathLine { x: parent.width / 2; y: 5 }
                        }
                        ShapePath {
                            fillColor: "#ffffff"
                            strokeColor: "transparent"
                            startX: parent.width / 2; startY: parent.height - 5
                            PathLine { x: parent.width / 2 + 8; y: parent.height / 2 }
                            PathLine { x: parent.width / 2 - 8; y: parent.height / 2 }
                            PathLine { x: parent.width / 2; y: parent.height - 5 }
                        }
                    }
                }

                // Heading display
                Rectangle {
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.top: parent.top
                    anchors.topMargin: -Theme.px(8)
                    width: Theme.px(44)
                    height: Theme.px(20)
                    radius: 4
                    color: Qt.rgba(0, 0, 0, 0.9)
                    border.color: Theme.accent

                    Text {
                        anchors.centerIn: parent
                        text: Math.round(root.heading) + "°"
                        color: Theme.accent
                        font.pixelSize: Theme.px(11)
                        font.family: Theme.fontMono
                        font.bold: true
                    }
                }

                // Fixed marker
                Rectangle {
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.top: parent.top
                    anchors.topMargin: Theme.px(10)
                    width: Math.max(1, Theme.px(3))
                    height: Theme.px(15)
                    color: Theme.accent
                }
            }
        }

        // ========== MAIN AREA - Map and Gauges ==========
        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            // Prevent the main area from collapsing into a tiny "cluster".
            Layout.minimumHeight: Theme.px(260)
            spacing: Theme.px(8)

            // Map panel
            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                radius: Theme.radiusMd
                color: "transparent"
                border.color: Theme.panelEdge
                border.width: 1
                clip: true

                MapPanel {
                    anchors.fill: parent
                    anchors.margins: 2
                    aadsClient: root.aadsClient
                    tileUrl: uiSettings ? uiSettings.localTileUrl : ""
                    navCoordinate: root.navCoordinate
                    trackPath: root.trackPath
                }

                // Track counter
                Rectangle {
                    anchors.left: parent.left
                    anchors.top: parent.top
                    anchors.margins: Theme.px(10)
                    width: trackRow.width + Theme.px(12)
                    height: Theme.px(22)
                    radius: 11
                    color: Qt.rgba(0, 0, 0, 0.75)
                    border.color: Theme.accent

                    Row {
                        id: trackRow
                        anchors.centerIn: parent
                        spacing: Theme.px(5)
                        Rectangle { width: Theme.px(6); height: Theme.px(6); radius: Theme.px(3); color: Theme.success; anchors.verticalCenter: parent.verticalCenter }
                        Text { text: "TRACK " + (trackPath ? trackPath.length : 0); color: Theme.textMain; font.pixelSize: Theme.px(9); font.family: Theme.fontMono }
                    }
                }

                // SOG/HDG overlay
                Rectangle {
                    anchors.right: parent.right
                    anchors.top: parent.top
                    anchors.margins: Theme.px(10)
                    width: Theme.px(110)
                    height: Theme.px(54)
                    radius: 6
                    color: Qt.rgba(0, 0, 0, 0.8)
                    border.color: Theme.panelEdge

                    Column {
                        anchors.centerIn: parent
                        spacing: Theme.px(2)
                        Row {
                            spacing: Theme.px(6)
                            Text { text: "SOG"; color: Theme.muted; font.pixelSize: Theme.px(8); font.family: Theme.fontMono; width: Theme.px(25) }
                            Text { text: root.boatSpeed.toFixed(1) + " kn"; color: Theme.accent; font.pixelSize: Theme.px(12); font.family: Theme.fontMono; font.bold: true }
                        }
                        Row {
                            spacing: Theme.px(6)
                            Text { text: "HDG"; color: Theme.muted; font.pixelSize: Theme.px(8); font.family: Theme.fontMono; width: Theme.px(25) }
                            Text { text: Math.round(root.heading) + "°"; color: Theme.textMain; font.pixelSize: Theme.px(12); font.family: Theme.fontMono; font.bold: true }
                        }
                    }
                }

                // Navi chat
                Rectangle {
                    anchors.left: parent.left
                    anchors.bottom: parent.bottom
                    anchors.margins: Theme.px(10)
                    width: naviW
                    height: naviH
                    radius: Theme.radiusSm
                    color: Qt.rgba(0, 0, 0, 0.85)
                    border.color: Theme.panelEdge
                    visible: uiSettings ? uiSettings.showNavi : true

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: Theme.px(8)
                        spacing: Theme.px(4)

                        Row {
                            spacing: Theme.px(6)
                            Text { text: "NAVI"; color: Theme.accent; font.pixelSize: Theme.px(10); font.family: Theme.fontDisplay; font.bold: true }
                            Rectangle {
                                width: Theme.px(40); height: Theme.px(14); radius: Theme.px(7)
                                color: Qt.rgba(Theme.success.r, Theme.success.g, Theme.success.b, 0.3)
                                border.color: Theme.success
                                Text { anchors.centerIn: parent; text: "online"; color: Theme.success; font.pixelSize: Theme.px(7); font.family: Theme.fontMono }
                            }
                        }

                        ListView {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            model: naviPreview || []
                            clip: true
                            spacing: Math.max(1, Theme.px(1))
                            delegate: Text {
                                width: ListView.view.width
                                text: (modelData && modelData.role === "user" ? "> " : "") + (modelData ? modelData.message : "")
                                color: modelData && modelData.role === "user" ? Theme.warning : Theme.textMain
                                font.pixelSize: Theme.px(8)
                                font.family: Theme.fontMono
                                elide: Text.ElideRight
                            }
                        }

                        TextField {
                            Layout.fillWidth: true
                            Layout.preferredHeight: Theme.px(24)
                            placeholderText: "Ask Navi..."
                            placeholderTextColor: Theme.muted
                            color: Theme.textMain
                            font.pixelSize: Theme.px(9)
                            font.family: Theme.fontBody
                            background: Rectangle { color: Qt.rgba(0.1, 0.15, 0.2, 0.8); border.color: Theme.panelEdge; radius: 4 }
                            onAccepted: { if (text !== "" && aadsClient) { aadsClient.sendNaviMessage(text); text = ""; } }
                        }
                    }
                }
            }

            // Gauge panel
            Rectangle {
                Layout.preferredWidth: gaugePanelW
                Layout.fillHeight: true
                radius: Theme.radiusMd
                color: Qt.rgba(0.03, 0.05, 0.08, 0.9)
                border.color: Theme.panelEdge
                border.width: 1

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: Theme.px(8)
                    spacing: Theme.px(6)

                    Row {
                        spacing: Theme.px(6)
                        Text { text: "INSTRUMENTS"; color: Theme.accent; font.pixelSize: Theme.px(10); font.family: Theme.fontDisplay; font.bold: true }
                        Item { width: 1; height: 1 }
                        Text { text: root.gridRows + "x" + root.gridCols; color: Theme.muted; font.pixelSize: Theme.px(8); font.family: Theme.fontMono }
                    }

                    GridLayout {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        columns: root.gridCols
                        rowSpacing: Theme.px(4)
                        columnSpacing: Theme.px(4)

                        Repeater {
                            model: root.gridCells

                            delegate: Rectangle {
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                radius: 6
                                color: Qt.rgba(0.05, 0.08, 0.12, 0.8)
                                border.color: Qt.rgba(Theme.accent.r, Theme.accent.g, Theme.accent.b, 0.2)

                                Loader {
                                    anchors.fill: parent
                                    anchors.margins: Theme.px(3)
                                    sourceComponent: Logic.isDirectionKey(modelData || "") ? compassComp : circularComp
                                    property string gaugeKey: modelData || ""
                                }

                                Component {
                                    id: circularComp
                                    CircularGauge {
                                        metaData: Logic.getGaugeMeta(gaugeKey)
                                        value: Logic.resolve(gaugeKey, root.aadsClient, root.aadsClient ? root.aadsClient.bridgeSignals : null)
                                    }
                                }

                                Component {
                                    id: compassComp
                                    CompassGauge {
                                        metaData: Logic.getGaugeMeta(gaugeKey)
                                        value: Logic.resolve(gaugeKey, root.aadsClient, root.aadsClient ? root.aadsClient.bridgeSignals : null)
                                        mode: gaugeKey.indexOf("wind") !== -1 ? "wind_relative" : "compass"
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
