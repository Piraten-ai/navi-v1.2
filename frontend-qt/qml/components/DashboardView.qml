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
    property var gaugeGrid: ({ rows: 3, cols: 3, cells: [] })
    property var naviPreview
    signal cameraViewRequested(bool useCamera)
    property string cameraName: uiSettings && uiSettings.cameraName ? uiSettings.cameraName : "J1455"
    property bool cameraAvailable: mediaDevices.videoInputs.length > 0
    property real leftColumnRatio: 0.65
    property real rightColumnRatio: 0.35
    property real topRowRatio: 0.2


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
        videoOutput: cameraOutputA
    }

    Component.onCompleted: {
        if (cameraAvailable) {
            mainCamera.start();
        }
    }

    function autopilotStatus() {
        if (aadsClient && aadsClient.autopilotStatus) {
            return String(aadsClient.autopilotStatus).toUpperCase();
        }
        return qsTr("STANDBY");
    }

    RowLayout {
        anchors.fill: parent
        spacing: 12

        ColumnLayout {
            Layout.preferredWidth: root.width * root.leftColumnRatio
            Layout.fillHeight: true
            spacing: 12

            RowLayout {
                Layout.fillWidth: true
                Layout.preferredHeight: root.height * root.topRowRatio
                spacing: 12

                Rectangle {
                    Layout.preferredWidth: root.width * 0.25
                    Layout.fillHeight: true
                    radius: Theme.radiusMd
                    color: Theme.panelSoft
                    border.color: Theme.panelEdge
                    border.width: 1
                    clip: true

                    VideoOutput {
                        id: cameraOutputA
                        anchors.fill: parent
                        fillMode: VideoOutput.PreserveAspectCrop
                        visible: root.cameraAvailable
                    }

                    Text {
                        anchors.centerIn: parent
                        text: qsTr("NO CAMERA")
                        color: Theme.muted
                        font.pixelSize: 11
                        font.bold: true
                        font.family: Theme.fontMono
                        visible: !root.cameraAvailable
                    }

                    Text {
                        anchors.left: parent.left
                        anchors.top: parent.top
                        anchors.margins: 10
                        text: qsTr("kamera feed")
                        color: Theme.muted
                        font.pixelSize: 10
                        font.family: Theme.fontMono
                    }
                }

                Rectangle {
                    Layout.preferredWidth: root.width * 0.35
                    Layout.fillHeight: true
                    radius: Theme.radiusMd
                    color: Theme.panelSoft
                    border.color: Theme.panelEdge
                    border.width: 1

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 14
                        spacing: 8

                        Text {
                            text: qsTr("AUTOPILOT CONTROL")
                            color: Theme.textMuted
                            font.pixelSize: 10
                            font.family: Theme.fontMono
                            font.letterSpacing: 1.4
                        }

                        GridLayout {
                            Layout.fillWidth: true
                            columns: 2
                            rowSpacing: 6
                            columnSpacing: 10

                            Text { text: qsTr("MODE"); color: Theme.muted; font.pixelSize: 9; font.family: Theme.fontMono }
                            Text { text: qsTr("HEADING"); color: Theme.text; font.pixelSize: 11; font.family: Theme.fontBody }

                            Text { text: qsTr("COURSE"); color: Theme.muted; font.pixelSize: 9; font.family: Theme.fontMono }
                            Text { text: aadsClient ? Logic.headingText(aadsClient.navHeading) : qsTr("--"); color: Theme.text; font.pixelSize: 11; font.family: Theme.fontBody }

                            Text { text: qsTr("SPEED"); color: Theme.muted; font.pixelSize: 9; font.family: Theme.fontMono }
                            Text { text: aadsClient ? aadsClient.navSpeed.toFixed(1) + qsTr(" kn") : qsTr("0.0 kn"); color: Theme.text; font.pixelSize: 11; font.family: Theme.fontBody }

                            Text { text: qsTr("STATUS"); color: Theme.muted; font.pixelSize: 9; font.family: Theme.fontMono }
                            Text { text: root.autopilotStatus(); color: Theme.accent; font.pixelSize: 11; font.family: Theme.fontBody }
                        }

                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 8

                            Rectangle {
                                Layout.fillWidth: true
                                height: 28
                                radius: 10
                                color: Qt.rgba(Theme.accent.r, Theme.accent.g, Theme.accent.b, 0.25)
                                border.color: Theme.accent
                                Text { anchors.centerIn: parent; text: qsTr("SET"); color: Theme.textMain; font.pixelSize: 10; font.family: Theme.fontMono }
                            }

                            Rectangle {
                                Layout.fillWidth: true
                                height: 28
                                radius: 10
                                color: Qt.rgba(Theme.danger.r, Theme.danger.g, Theme.danger.b, 0.2)
                                border.color: Theme.danger
                                Text { anchors.centerIn: parent; text: qsTr("DISENGAGE"); color: Theme.danger; font.pixelSize: 10; font.family: Theme.fontMono }
                            }

                            Rectangle {
                                Layout.fillWidth: true
                                height: 28
                                radius: 10
                                color: Qt.rgba(Theme.panelBorder.r, Theme.panelBorder.g, Theme.panelBorder.b, 0.2)
                                border.color: Theme.panelBorder
                                Text { anchors.centerIn: parent; text: qsTr("ADJUST"); color: Theme.textMain; font.pixelSize: 10; font.family: Theme.fontMono }
                            }
                        }
                    }
                }

                Item { Layout.fillWidth: true }
            }

            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                radius: Theme.radiusMd
                color: Theme.panelSoft
                border.color: Theme.panelEdge
                border.width: 1
                clip: true

                MapPanel {
                    anchors.fill: parent
                    aadsClient: aadsClient
                    tileUrl: uiSettings ? uiSettings.localTileUrl : ""
                    navCoordinate: navCoordinate
                    trackPath: trackPath
                    visible: uiSettings ? uiSettings.showMap : true
                }

                Rectangle {
                    anchors.fill: parent
                    visible: uiSettings ? !uiSettings.showMap : false
                    color: Theme.panelSoft
                    border.color: Theme.panelEdge
                    border.width: 1
                    radius: Theme.radiusMd

                    Text {
                        anchors.centerIn: parent
                        text: qsTr("MAP HIDDEN")
                        color: Theme.muted
                        font.pixelSize: 12
                        font.bold: true
                        font.letterSpacing: 2
                        font.family: Theme.fontDisplay
                    }
                }

                Rectangle {
                    anchors.left: parent.left
                    anchors.top: parent.top
                    anchors.margins: 12
                    radius: 10
                    color: Theme.panel
                    border.color: Theme.panelEdge
                    border.width: 1
                    height: 24

                    Text {
                        anchors.centerIn: parent
                        text: qsTr("TRACK ") + (trackPath ? trackPath.length : 0)
                        color: Theme.text
                        font.pixelSize: 9
                        font.bold: true
                        font.family: Theme.fontMono
                        anchors.margins: 8
                    }
                }

                Rectangle {
                    anchors.left: parent.left
                    anchors.top: parent.top
                    anchors.margins: 56
                    width: 110
                    height: 110
                    radius: 12
                    color: Theme.panel
                    border.color: Theme.panelEdge
                    border.width: 1
                    visible: uiSettings ? uiSettings.showCompass : true

                    Canvas {
                        anchors.fill: parent
                        anchors.margins: 14
                        onPaint: {
                            var ctx = getContext("2d");
                            ctx.clearRect(0, 0, width, height);
                            var cx = width / 2;
                            var cy = height / 2;
                            var r = Math.min(width, height) / 2 - 6;
                            ctx.strokeStyle = Theme.accent;
                            ctx.lineWidth = 2;
                            ctx.beginPath();
                            ctx.arc(cx, cy, r, 0, Math.PI * 2);
                            ctx.stroke();
                        }
                    }

                    Text {
                        anchors.centerIn: parent
                        text: aadsClient ? Logic.headingText(aadsClient.navHeading) : qsTr("--")
                        color: Theme.text
                        font.pixelSize: 14
                        font.bold: true
                        font.family: Theme.fontMono
                        horizontalAlignment: Text.AlignHCenter
                    }

                    Text {
                        anchors.horizontalCenter: parent.horizontalCenter
                        anchors.bottom: parent.bottom
                        anchors.bottomMargin: 8
                        text: qsTr("HEADING")
                        color: Theme.muted
                        font.pixelSize: 9
                        font.family: Theme.fontMono
                    }
                }

                Rectangle {
                    anchors.right: parent.right
                    anchors.top: parent.top
                    anchors.margins: 18
                    width: 180
                    height: 84
                    radius: Theme.radiusSm
                    color: Theme.panel
                    border.color: Theme.panelEdge
                    border.width: 1

                    Column {
                        anchors.centerIn: parent
                        spacing: 4
                        Text { text: qsTr("VAKTEN OVERLAY"); color: Theme.muted; font.pixelSize: 9 }
                        Text { text: qsTr("No targets detected"); color: Theme.text; font.pixelSize: 10; font.family: Theme.fontBody }
                    }
                }

                Rectangle {
                    anchors.right: parent.right
                    anchors.top: parent.top
                    anchors.margins: 18
                    y: 96
                    width: 220
                    height: 120
                    radius: Theme.radiusSm
                    color: Theme.panel
                    border.color: Theme.panelEdge
                    border.width: 1

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 10
                        spacing: 4
                        Text { text: qsTr("LOG FEED"); color: Theme.muted; font.pixelSize: 9; font.family: Theme.fontMono }
                        Repeater {
                            model: naviPreview || []
                            delegate: Text {
                                text: modelData ? modelData.message : ""
                                color: Theme.text
                                font.pixelSize: 8
                                font.family: Theme.fontBody
                                elide: Text.ElideRight
                            }
                        }
                    }
                }

                Rectangle {
                    anchors.left: parent.left
                    anchors.bottom: parent.bottom
                    anchors.margins: 12
                    width: 360
                    height: 130
                    radius: Theme.radiusMd
                    color: Theme.panel
                    border.color: Theme.panelEdge
                    border.width: 1
                    visible: uiSettings ? uiSettings.showNavi : true

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 10
                        spacing: 6

                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 8
                            Text { text: qsTr("AMUNDSEN CHAT"); color: Theme.muted; font.pixelSize: 9; font.bold: true; font.family: Theme.fontMono }
                            Rectangle {
                                width: 42
                                height: 14
                                radius: 7
                                color: Theme.indicator
                                Layout.alignment: Qt.AlignVCenter
                                Text {
                                    anchors.centerIn: parent
                                    text: qsTr("ready")
                                    color: Theme.bg
                                    font.pixelSize: 8
                                    font.bold: true
                                    font.family: Theme.fontMono
                                }
                            }
                        }

                        ListView {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            model: naviPreview || []
                            clip: true
                            delegate: Text {
                                text: modelData ? modelData.message : ""
                                color: Theme.text
                                font.pixelSize: 8
                                font.family: Theme.fontBody
                                elide: Text.ElideRight
                            }
                        }

                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 6

                            TextField {
                                id: chatInput
                                Layout.fillWidth: true
                                placeholderText: qsTr("Ask Navi...")
                                color: Theme.text
                                background: Rectangle { color: Theme.panel; border.color: Theme.panelEdge; radius: 6 }
                                onAccepted: sendBtn.clicked()
                            }

                            Button {
                                id: sendBtn
                                text: qsTr("Send")
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
        }

        Rectangle {
            Layout.preferredWidth: root.width * root.rightColumnRatio
            Layout.fillHeight: true
            radius: Theme.radiusMd
            color: Theme.panelSoft
            border.color: Theme.panelEdge
            border.width: 1

            GaugePanel {
                anchors.fill: parent
                anchors.margins: 12
                title: qsTr("TACTICAL GAUGES")
                gaugeGrid: gaugeGrid
                aadsClient: aadsClient
                showHistory: uiSettings ? uiSettings.showHistoryGraphs : false
            }
        }
    }
}
