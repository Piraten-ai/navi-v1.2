import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Item {
    id: root
    property var theme
    property var uiSettings
    property var aadsClient
    property string aadsLogoPath: ""
    property var trackPath
    property var navCoordinate
    property bool showCameraMain: false
    property var gaugeGrid
    property var gaugeCatalog
    property var gaugeMeta
    property var resolveSignal
    property var isDirectionKey
    property var headingText
    property var normalizeDegrees
    property var gaugeText
    property var naviPreview
    signal cameraViewRequested(bool useCamera)

    ColumnLayout {
        anchors.fill: parent
        spacing: 12

        Item {
            Layout.fillWidth: true
            Layout.fillHeight: true

            RowLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                spacing: 0

                MapPanel {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    theme: theme
                    localTileUrl: uiSettings.localTileUrl
                    navCoordinate: navCoordinate
                    trackPath: trackPath
                    signalkStatus: aadsClient.signalkStatus
                    nmeaStatus: aadsClient.nmeaStatus
                    aadsLogoPath: aadsLogoPath
                    showCameraMain: root.showCameraMain
                    showCompass: uiSettings.showCompass
                    headingText: headingText
                    normalizeDegrees: normalizeDegrees
                    navHeading: aadsClient.navHeading
                    naviStatus: aadsClient.naviStatus
                    naviPreview: naviPreview
                    sendNaviMessage: aadsClient.sendNaviMessage
                    onCameraViewRequested: root.cameraViewRequested(useCamera)
                }

                GaugePanel {
                    Layout.preferredWidth: Math.max(320, parent.width * 0.32)
                    Layout.fillHeight: true
                    theme: theme
                    gaugeGrid: gaugeGrid
                    gaugeCatalog: gaugeCatalog
                    gaugeMeta: gaugeMeta
                    resolveSignal: resolveSignal
                    isDirectionKey: isDirectionKey
                    headingText: headingText
                    gaugeText: gaugeText
                    navtexWarningCount: aadsClient.navtexWarningCount
                    navtexSummary: aadsClient.navtexSummary
                }
            }
        }
    }
}
