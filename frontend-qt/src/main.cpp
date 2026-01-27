#include <QGuiApplication>
#include <QQmlApplicationEngine>
#include <QQmlContext>
#include <QProcessEnvironment>
#include <QtQuickControls2/QQuickStyle>
#include <QDir>
#include <QDateTime>
#include <QFile>
#include <QTextStream>

#include "aads_client.h"

static QString envOrDefault(const QProcessEnvironment &env, const QString &key, const QString &fallback) {
    if (env.contains(key)) {
        QString value = env.value(key).trimmed();
        if (!value.isEmpty()) {
            return value;
        }
    }
    return fallback;
}

static QFile g_logFile;

static void logMessage(QtMsgType type, const QMessageLogContext &, const QString &msg) {
    if (!g_logFile.isOpen()) {
        return;
    }

    QString level;
    switch (type) {
        case QtDebugMsg: level = "DEBUG"; break;
        case QtInfoMsg: level = "INFO"; break;
        case QtWarningMsg: level = "WARN"; break;
        case QtCriticalMsg: level = "CRIT"; break;
        case QtFatalMsg: level = "FATAL"; break;
    }

    QTextStream stream(&g_logFile);
    stream << QDateTime::currentDateTime().toString(Qt::ISODate) << " [" << level << "] " << msg << "\n";
    stream.flush();
}

int main(int argc, char *argv[]) {
    QQuickStyle::setStyle("Fusion");
    QGuiApplication app(argc, argv);
    QCoreApplication::setOrganizationName("AADS");
    QCoreApplication::setOrganizationDomain("aads.local");
    QCoreApplication::setApplicationName("AADS UI");

    g_logFile.setFileName(QDir(QCoreApplication::applicationDirPath()).filePath("aads_ui.log"));
    g_logFile.open(QIODevice::Append | QIODevice::Text);
    qInstallMessageHandler(logMessage);
    qInfo().noquote() << "AADS UI starting from" << QCoreApplication::applicationDirPath();

    const QString appDir = QCoreApplication::applicationDirPath();
    QProcessEnvironment env = QProcessEnvironment::systemEnvironment();
    QString apiUrl = envOrDefault(env, "AADS_API_URL", "http://localhost:8001");
    QString wsUrl = envOrDefault(env, "AADS_WS_URL", "ws://localhost:8001/ws");
    QString signalkUrl = envOrDefault(env, "AADS_SIGNALK_URL", "http://localhost:3001");
    QString tilesUrl = envOrDefault(env, "AADS_TILES_URL", "http://localhost:8080/styles/raster/");
    QString wikiPath = envOrDefault(env, "AADS_WIKI_PATH", "/opt/aads/docs/current/AADS_WIKI.md");
    QString logoPath = envOrDefault(env, "AADS_LOGO_PATH", QDir(appDir).filePath("logo aasd.png"));

    AadsClient client;
    client.setApiUrl(apiUrl);
    client.setWsUrl(wsUrl);
    client.setSignalkUrl(signalkUrl);
    client.setWikiPath(wikiPath);

    QQmlApplicationEngine engine;
    engine.addImportPath(appDir);
    engine.addImportPath(QDir(appDir).filePath("qml"));
    QObject::connect(&engine, &QQmlApplicationEngine::warnings, [](const QList<QQmlError> &warnings) {
        for (const QQmlError &warning : warnings) {
            qWarning().noquote() << warning.toString();
        }
    });
    engine.rootContext()->setContextProperty("aadsClient", &client);
    engine.rootContext()->setContextProperty("aadsApiUrl", apiUrl);
    engine.rootContext()->setContextProperty("aadsWsUrl", wsUrl);
    engine.rootContext()->setContextProperty("aadsSignalkUrl", signalkUrl);
    engine.rootContext()->setContextProperty("aadsTilesUrl", tilesUrl);
    engine.rootContext()->setContextProperty("aadsWikiPath", wikiPath);
    engine.rootContext()->setContextProperty("aadsLogoPath", logoPath);
    engine.loadFromModule("AadsUi", "Main");

    if (engine.rootObjects().isEmpty()) {
        qCritical().noquote() << "Failed to load QML module AadsUi/Main.";
        return -1;
    }

    return app.exec();
}
