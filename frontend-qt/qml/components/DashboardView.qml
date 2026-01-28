import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtMultimedia 6.2
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

    property string cameraName: uiSettings && uiSettings.cameraName ? uiSettings.cameraName : "J1455"
    property bool cameraAvailable: mediaDevices.videoInputs.length > 0

    function findCameraDevice() {
        var inputs = mediaDevices.videoInputs;
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
            if (root.cameraAvailable) {
                mainCamera.start();
            }
        }
    }

    Camera {
        id: mainCamera
        cameraDevice: root.findCameraDevice()
        onCameraDeviceChanged: {
            if (root.cameraAvailable) {
                start();
            }
        }
    }

    CaptureSession {
        id: cameraSession
        camera: mainCamera
        videoOutput: cameraOutput
    }

    Component.onCompleted: {
        if (cameraAvailable) {
            mainCamera.start();
        }
    }

    // Parse grid properties
    readonly property int gridRows: (gaugeGrid && gaugeGrid.rows) ? gaugeGrid.rows : 3
    readonly property int gridCols: (gaugeGrid && gaugeGrid.cols) ? gaugeGrid.cols : 2
    readonly property var gridCells: (gaugeGrid && gaugeGrid.cells && gaugeGrid.cells.length > 0)
                                     ? gaugeGrid.cells
                                     : defaultCells()

    function defaultCells() {
        return [
            "engine.rpm", "engine.rpm",
            "environment.wind.speed", "nav.speed_over_ground",
            "environment.wind.speed", "nav.heading"
        ];
    }

    RowLayout {
        anchors.fill: parent
        spacing: 12

        // ========== LEFT COLUMN - Map and overlays ==========
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.preferredWidth: parent.width * 0.65
            radius: Theme.radiusMd
            color: "transparent"

            // Main map
            MapPanel {
                id: mainMap
                anchors.fill: parent
                aadsClient: root.aadsClient
                tileUrl: uiSettings ? uiSettings.localTileUrl : ""
                navCoordinate: root.navCoordinate
                trackPath: root.trackPath
            }

            // ===== TOP LEFT: Compass =====
            Rectangle {
                id: compassOverlay
                anchors.left: parent.left
                anchors.top: parent.top
                anchors.margins: 12
                width: 120
                height: 120
                radius: 60
                color: Qt.rgba(Theme.panel.r, Theme.panel.g, Theme.panel.b, 0.85)
                border.color: Theme.panelEdge
                border.width: 1

                CompassGauge {
                    anchors.fill: parent
                    anchors.margins: 8
                    metaData: Logic.getGaugeMeta("nav.heading")
                    value: aadsClient ? aadsClient.navHeading : 0
                    showLabel: false
                    mode: "compass"
                }
            }

            // ===== TOP CENTER: Camera feed =====
            Rectangle {
                id: cameraOverlay
                anchors.left: compassOverlay.right
                anchors.top: parent.top
                anchors.margins: 12
                anchors.leftMargin: 12
                width: 220
                height: 140
                radius: Theme.radiusMd
                color: Qt.rgba(Theme.panel.r, Theme.panel.g, Theme.panel.b, 0.9)
                border.color: Theme.panelEdge
                border.width: 1
                clip: true

                VideoOutput {
                    id: cameraOutput
                    anchors.fill: parent
                    fillMode: VideoOutput.PreserveAspectCrop
                    visible: cameraAvailable
                }

                // No camera placeholder
                Column {
                    anchors.centerIn: parent
                    spacing: 6
                    visible: !cameraAvailable

                    Text {
                        text: qsTr("NO CAMERA")
                        color: Theme.muted
                        font.pixelSize: 12
                        font.family: Theme.fontDisplay
                        font.bold: true
                        anchors.horizontalCenter: parent.horizontalCenter
                    }

                    Text {
                        text: qsTr("Connect camera feed")
                        color: Qt.rgba(Theme.muted.r, Theme.muted.g, Theme.muted.b, 0.6)
                        font.pixelSize: 9
                        font.family: Theme.fontBody
                        anchors.horizontalCenter: parent.horizontalCenter
                    }
                }
            }

            // ===== TOP RIGHT: Autopilot Control =====
            Rectangle {
                id: autopilotOverlay
                anchors.left: cameraOverlay.right
                anchors.top: parent.top
                anchors.margins: 12
                anchors.leftMargin: 12
                width: 260
                height: 160
                radius: Theme.radiusMd
                color: Qt.rgba(Theme.panel.r, Theme.panel.g, Theme.panel.b, 0.92)
                border.color: Theme.panelEdge
                border.width: 1

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 12
                    spacing: 8

                    Text {
                        text: qsTr("AUTOPILOT CONTROL")
                        color: Theme.textMain
                        font.pixelSize: 12
                        font.family: Theme.fontDisplay
                        font.bold: true
                        font.letterSpacing: 1
                    }

                    // Mode and Course row
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 12

                        Column {
                            spacing: 2
                            Text { text: qsTr("MODE:"); color: Theme.muted; font.pixelSize: 9; font.family: Theme.fontMono }
                            Rectangle {
                                width: 70; height: 24; radius: 4
                                color: Qt.rgba(Theme.bg.r, Theme.bg.g, Theme.bg.b, 0.6)
                                border.color: Theme.panelEdge
                                Text {
                                    anchors.centerIn: parent
                                    text: qsTr("HEADING")
                                    color: Theme.textMain
                                    font.pixelSize: 10
                                    font.family: Theme.fontMono
                                    font.bold: true
                                }
                            }
                        }

                        Column {
                            spacing: 2
                            Text { text: qsTr("COURSE:"); color: Theme.muted; font.pixelSize: 9; font.family: Theme.fontMono }
                            Rectangle {
                                width: 60; height: 24; radius: 4
                                color: Qt.rgba(Theme.bg.r, Theme.bg.g, Theme.bg.b, 0.6)
                                border.color: Theme.panelEdge
                                Text {
                                    anchors.centerIn: parent
                                    text: aadsClient ? Math.round(aadsClient.navHeading) + "°" : "---°"
                                    color: Theme.textMain
                                    font.pixelSize: 10
                                    font.family: Theme.fontMono
                                    font.bold: true
                                }
                            }
                        }
                    }

                    // Speed and Status row
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 12

                        Column {
                            spacing: 2
                            Text { text: qsTr("SPEED:"); color: Theme.muted; font.pixelSize: 9; font.family: Theme.fontMono }
                            Rectangle {
                                width: 70; height: 24; radius: 4
                                color: Qt.rgba(Theme.bg.r, Theme.bg.g, Theme.bg.b, 0.6)
                                border.color: Theme.panelEdge
                                Text {
                                    anchors.centerIn: parent
                                    text: aadsClient ? aadsClient.navSpeed.toFixed(1) + " KN" : "0.0 KN"
                                    color: Theme.textMain
                                    font.pixelSize: 10
                                    font.family: Theme.fontMono
                                    font.bold: true
                                }
                            }
                        }

                        Column {
                            spacing: 2
                            Text { text: qsTr("STATUS:"); color: Theme.muted; font.pixelSize: 9; font.family: Theme.fontMono }
                            Rectangle {
                                width: 80; height: 24; radius: 4
                                color: Qt.rgba(Theme.success.r, Theme.success.g, Theme.success.b, 0.2)
                                border.color: Theme.success
                                Text {
                                    anchors.centerIn: parent
                                    text: aadsClient && aadsClient.autopilotStatus ? aadsClient.autopilotStatus.toUpperCase() : qsTr("STANDBY")
                                    color: Theme.success
                                    font.pixelSize: 10
                                    font.family: Theme.fontMono
                                    font.bold: true
                                }
                            }
                        }
                    }

                    // Buttons row
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 8

                        Rectangle {
                            Layout.fillWidth: true
                            height: 28
                            radius: 6
                            color: Qt.rgba(Theme.accent.r, Theme.accent.g, Theme.accent.b, 0.2)
                            border.color: Theme.accent
                            Text { anchors.centerIn: parent; text: qsTr("SET"); color: Theme.accent; font.pixelSize: 10; font.family: Theme.fontMono; font.bold: true }
                            MouseArea { anchors.fill: parent; cursorShape: Qt.PointingHandCursor }
                        }

                        Rectangle {
                            Layout.fillWidth: true
                            height: 28
                            radius: 6
                            color: Qt.rgba(Theme.danger.r, Theme.danger.g, Theme.danger.b, 0.2)
                            border.color: Theme.danger
                            Text { anchors.centerIn: parent; text: qsTr("DISENGAGE"); color: Theme.danger; font.pixelSize: 10; font.family: Theme.fontMono; font.bold: true }
                            MouseArea { anchors.fill: parent; cursorShape: Qt.PointingHandCursor }
                        }

                        Rectangle {
                            Layout.fillWidth: true
                            height: 28
                            radius: 6
                            color: Qt.rgba(Theme.panelEdge.r, Theme.panelEdge.g, Theme.panelEdge.b, 0.3)
                            border.color: Theme.panelEdge
                            Text { anchors.centerIn: parent; text: qsTr("ADJUST"); color: Theme.textMain; font.pixelSize: 10; font.family: Theme.fontMono; font.bold: true }
                            MouseArea { anchors.fill: parent; cursorShape: Qt.PointingHandCursor }
                        }
                    }
                }
            }

            // ===== TOP FAR RIGHT: Log Feed =====
            Rectangle {
                id: logFeedOverlay
                anchors.right: parent.right
                anchors.top: parent.top
                anchors.margins: 12
                width: 180
                height: 160
                radius: Theme.radiusMd
                color: Qt.rgba(Theme.panel.r, Theme.panel.g, Theme.panel.b, 0.92)
                border.color: Theme.panelEdge
                border.width: 1

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 10
                    spacing: 6

                    RowLayout {
                        Layout.fillWidth: true
                        Text {
                            text: qsTr("LOG FEED")
                            color: Theme.muted
                            font.pixelSize: 9
                            font.family: Theme.fontMono
                            font.bold: true
                            font.letterSpacing: 1
                        }
                        Item { Layout.fillWidth: true }
                        Rectangle {
                            width: 8; height: 8; radius: 4
                            color: Theme.success
                            SequentialAnimation on opacity {
                                running: true; loops: Animation.Infinite
                                NumberAnimation { from: 1.0; to: 0.4; duration: 1000 }
                                NumberAnimation { from: 0.4; to: 1.0; duration: 1000 }
                            }
                        }
                    }

                    ListView {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        model: naviPreview || []
                        clip: true
                        spacing: 3

                        delegate: Text {
                            width: ListView.view.width
                            text: modelData ? modelData.message : ""
                            color: Theme.textMain
                            font.pixelSize: 8
                            font.family: Theme.fontMono
                            elide: Text.ElideRight
                        }
                    }
                }
            }

            // ===== Track counter =====
            Rectangle {
                anchors.right: logFeedOverlay.left
                anchors.top: parent.top
                anchors.margins: 12
                anchors.rightMargin: 8
                width: trackLabel.width + 16
                height: 22
                radius: 11
                color: Qt.rgba(Theme.panel.r, Theme.panel.g, Theme.panel.b, 0.85)
                border.color: Theme.panelEdge

                Text {
                    id: trackLabel
                    anchors.centerIn: parent
                    text: qsTr("TRACK ") + (trackPath ? trackPath.length : 0)
                    color: Theme.textMain
                    font.pixelSize: 9
                    font.family: Theme.fontMono
                    font.bold: true
                }
            }

            // ===== BOTTOM LEFT: Navi Chat =====
            Rectangle {
                id: naviChatOverlay
                anchors.left: parent.left
                anchors.bottom: parent.bottom
                anchors.margins: 12
                width: 380
                height: 150
                radius: Theme.radiusMd
                color: Qt.rgba(Theme.panel.r, Theme.panel.g, Theme.panel.b, 0.92)
                border.color: Theme.panelEdge
                border.width: 1

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 10
                    spacing: 6

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 8

                        Text {
                            text: qsTr("AMUNDSEN CHAT")
                            color: Theme.textMain
                            font.pixelSize: 10
                            font.family: Theme.fontDisplay
                            font.bold: true
                            font.letterSpacing: 1
                        }

                        Rectangle {
                            width: 42; height: 16; radius: 8
                            color: Theme.success
                            Text {
                                anchors.centerIn: parent
                                text: qsTr("ready")
                                color: Theme.bg
                                font.pixelSize: 8
                                font.family: Theme.fontMono
                                font.bold: true
                            }
                        }

                        Item { Layout.fillWidth: true }
                    }

                    ListView {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        model: naviPreview || []
                        clip: true
                        spacing: 3

                        delegate: RowLayout {
                            width: ListView.view.width
                            spacing: 6

                            Text {
                                text: modelData && modelData.role === "user" ? qsTr("User") : qsTr("Navi")
                                color: modelData && modelData.role === "user" ? Theme.warning : Theme.accent
                                font.pixelSize: 8
                                font.family: Theme.fontMono
                                font.bold: true
                            }

                            Text {
                                Layout.fillWidth: true
                                text: modelData ? modelData.message : ""
                                color: Theme.textMain
                                font.pixelSize: 9
                                font.family: Theme.fontBody
                                elide: Text.ElideRight
                            }
                        }
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 8

                        TextField {
                            id: chatInput
                            Layout.fillWidth: true
                            placeholderText: qsTr("Ask Navi...")
                            placeholderTextColor: Theme.muted
                            color: Theme.textMain
                            font.pixelSize: 10
                            font.family: Theme.fontBody
                            background: Rectangle {
                                color: Qt.rgba(Theme.bg.r, Theme.bg.g, Theme.bg.b, 0.6)
                                border.color: Theme.panelEdge
                                radius: 6
                            }
                            onAccepted: sendBtn.clicked()
                        }

                        Button {
                            id: sendBtn
                            text: qsTr("Send")
                            font.pixelSize: 10
                            font.family: Theme.fontMono
                            font.bold: true

                            background: Rectangle {
                                radius: 6
                                color: Qt.rgba(Theme.accent.r, Theme.accent.g, Theme.accent.b, 0.3)
                                border.color: Theme.accent
                            }

                            contentItem: Text {
                                text: sendBtn.text
                                color: Theme.accent
                                font: sendBtn.font
                                horizontalAlignment: Text.AlignHCenter
                                verticalAlignment: Text.AlignVCenter
                            }

                            onClicked: {
                                if (chatInput.text === "") return;
                                if (aadsClient) aadsClient.sendNaviMessage(chatInput.text);
                                chatInput.text = "";
                            }
                        }
                    }
                }
            }
        }

        // ========== RIGHT COLUMN - Status and Gauges ==========
        ColumnLayout {
            Layout.preferredWidth: parent.width * 0.32
            Layout.fillHeight: true
            spacing: 12

            // ===== SYSTEM STATUS =====
            Rectangle {
                Layout.fillWidth: true
                height: 50
                radius: Theme.radiusMd
                color: Qt.rgba(Theme.panel.r, Theme.panel.g, Theme.panel.b, 0.7)
                border.color: Theme.panelEdge
                border.width: 1

                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 12
                    spacing: 16

                    Text {
                        text: qsTr("SYSTEM STATUS")
                        color: Theme.muted
                        font.pixelSize: 9
                        font.family: Theme.fontMono
                        font.bold: true
                        font.letterSpacing: 1
                    }

                    Row {
                        spacing: 12

                        Row {
                            spacing: 6
                            Rectangle { width: 10; height: 10; radius: 5; color: Theme.success }
                            Text { text: qsTr("ARDUINO"); color: Theme.textMain; font.pixelSize: 9; font.family: Theme.fontMono }
                        }

                        Row {
                            spacing: 6
                            Rectangle { width: 10; height: 10; radius: 5; color: Theme.warning }
                            Text { text: qsTr("JETSON"); color: Theme.textMain; font.pixelSize: 9; font.family: Theme.fontMono }
                        }
                    }

                    Item { Layout.fillWidth: true }
                }
            }

            // ===== NAVIGATION & CONTROLS header =====
            Rectangle {
                Layout.fillWidth: true
                height: 36
                radius: Theme.radiusMd
                color: Qt.rgba(Theme.panel.r, Theme.panel.g, Theme.panel.b, 0.5)
                border.color: Theme.panelEdge
                border.width: 1

                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 10
                    spacing: 8

                    Text {
                        text: qsTr("NAVIGATION & CONTROLS")
                        color: Theme.accent
                        font.pixelSize: 10
                        font.family: Theme.fontDisplay
                        font.bold: true
                        font.letterSpacing: 1
                    }

                    Item { Layout.fillWidth: true }

                    Rectangle {
                        width: 10; height: 10; radius: 5
                        color: aadsClient && aadsClient.wsConnected ? Theme.success : Theme.danger
                    }
                }
            }

            // ===== Progress bar (placeholder) =====
            Rectangle {
                Layout.fillWidth: true
                height: 8
                radius: 4
                color: Qt.rgba(Theme.bg.r, Theme.bg.g, Theme.bg.b, 0.5)

                Rectangle {
                    width: parent.width * 0.7
                    height: parent.height
                    radius: parent.radius
                    color: Theme.accent
                }
            }

            // ===== GAUGE GRID =====
            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                radius: Theme.radiusMd
                color: Qt.rgba(Theme.panel.r, Theme.panel.g, Theme.panel.b, 0.4)
                border.color: Theme.panelEdge
                border.width: 1

                GridLayout {
                    anchors.fill: parent
                    anchors.margins: 12
                    columns: root.gridCols
                    rowSpacing: 10
                    columnSpacing: 10

                    Repeater {
                        model: root.gridCells

                        delegate: Rectangle {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            color: "transparent"
                            radius: Theme.radiusSm

                            // Section label above each row
                            Text {
                                anchors.top: parent.top
                                anchors.left: parent.left
                                anchors.margins: 4
                                text: {
                                    var meta = Logic.getGaugeMeta(modelData || "");
                                    return meta.label || "";
                                }
                                color: Theme.muted
                                font.pixelSize: 8
                                font.family: Theme.fontMono
                                font.bold: true
                                visible: index % root.gridCols === 0
                            }

                            Loader {
                                anchors.fill: parent
                                anchors.margins: 4

                                sourceComponent: {
                                    var key = modelData || "";
                                    if (Logic.isDirectionKey(key)) {
                                        return compassGaugeComponent;
                                    }
                                    return circularGaugeComponent;
                                }

                                property string gaugeKey: modelData || ""
                            }

                            Component {
                                id: circularGaugeComponent

                                CircularGauge {
                                    metaData: Logic.getGaugeMeta(gaugeKey)
                                    value: Logic.resolve(gaugeKey, root.aadsClient, root.aadsClient ? root.aadsClient.bridgeSignals : null)
                                }
                            }

                            Component {
                                id: compassGaugeComponent

                                CompassGauge {
                                    metaData: Logic.getGaugeMeta(gaugeKey)
                                    value: Logic.resolve(gaugeKey, root.aadsClient, root.aadsClient ? root.aadsClient.bridgeSignals : null)
                                    mode: {
                                        if (gaugeKey === "nav.heading" || gaugeKey === "nav.course_over_ground") {
                                            return "compass";
                                        }
                                        if (gaugeKey.indexOf("wind") !== -1) {
                                            return gaugeKey.indexOf("true") !== -1 ? "wind_true" : "wind_relative";
                                        }
                                        return "compass";
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
