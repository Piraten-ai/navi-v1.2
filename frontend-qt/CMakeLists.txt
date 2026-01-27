cmake_minimum_required(VERSION 3.16)

project(aads_frontend_qt LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(Qt6 REQUIRED COMPONENTS Quick QuickControls2 Network WebSockets Location Positioning Multimedia)

qt_standard_project_setup()

qt_policy(SET QTP0001 NEW)
qt_policy(SET QTP0004 NEW)

qt_add_executable(aads_ui
    src/main.cpp
    src/aads_client.cpp
    src/aads_client.h
)

qt_add_qml_module(aads_ui
    URI AadsUi
    VERSION 1.0
    QML_FILES
        qml/Main.qml
        qml/Theme.qml
        qml/components/TopBar.qml
        qml/components/DashboardView.qml
        qml/components/GaugePanel.qml
        qml/components/MapPanel.qml
        qml/components/StatusLed.qml
        qml/components/CircularGauge.qml
        qml/components/HistoryGraph.qml
        qml/components/BridgeView.qml
        qml/components/NaviView.qml
        qml/components/WikiView.qml
        qml/components/SettingsView.qml
        qml/utils/SignalLogic.js
        qml/utils/ProfileHandler.js
        qml/utils/ProfileUtils.js
    RESOURCES
        qml/qmldir
        qml/fonts/SpaceGrotesk.ttf
        qml/fonts/Rajdhani-SemiBold.ttf
        qml/fonts/JetBrainsMono-Regular.ttf
)

target_link_libraries(aads_ui
    PRIVATE Qt6::Quick Qt6::QuickControls2 Qt6::Network Qt6::WebSockets Qt6::Location Qt6::Positioning Qt6::Multimedia
)
