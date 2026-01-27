#include "aads_client.h"

#include <QJsonArray>
#include <QJsonDocument>
#include <QJsonObject>
#include <QNetworkRequest>
#include <QUrlQuery>
#include <QFile>
#include <algorithm>

AadsClient::AadsClient(QObject *parent)
    : QObject(parent) {
    connect(&m_ws, &QWebSocket::connected, this, &AadsClient::onWsConnected);
    connect(&m_ws, &QWebSocket::disconnected, this, &AadsClient::onWsDisconnected);
    connect(&m_ws, &QWebSocket::textMessageReceived, this, &AadsClient::onWsTextMessage);
    connect(&m_ws, &QWebSocket::errorOccurred, this, &AadsClient::onWsError);
}

QString AadsClient::apiUrl() const {
    return m_apiUrl;
}

void AadsClient::setApiUrl(const QString &url) {
    if (m_apiUrl == url) {
        return;
    }
    m_apiUrl = url;
    emit apiUrlChanged();
}

QString AadsClient::wsUrl() const {
    return m_wsUrl;
}

void AadsClient::setWsUrl(const QString &url) {
    if (m_wsUrl == url) {
        return;
    }
    m_wsUrl = url;
    emit wsUrlChanged();
}

QString AadsClient::signalkUrl() const {
    return m_signalkUrl;
}

void AadsClient::setSignalkUrl(const QString &url) {
    if (m_signalkUrl == url) {
        return;
    }
    m_signalkUrl = url;
    emit signalkUrlChanged();
}

QString AadsClient::wikiPath() const {
    return m_wikiPath;
}

void AadsClient::setWikiPath(const QString &path) {
    if (m_wikiPath == path) {
        return;
    }
    m_wikiPath = path;
    emit wikiPathChanged();
}

bool AadsClient::wsConnected() const {
    return m_wsConnected;
}

QString AadsClient::lastHealthStatus() const {
    return m_lastHealthStatus;
}

QString AadsClient::lastWsMessage() const {
    return m_lastWsMessage;
}

QVariantList AadsClient::healthServices() const {
    return m_healthServices;
}

QString AadsClient::appName() const {
    return m_appName;
}

QString AadsClient::appVersion() const {
    return m_appVersion;
}

QString AadsClient::appEnvironment() const {
    return m_appEnvironment;
}

int AadsClient::wsActiveConnections() const {
    return m_wsActiveConnections;
}

QVariantList AadsClient::bridgeSignals() const {
    return m_bridgeSignals;
}

QString AadsClient::bridgeTimestamp() const {
    return m_bridgeTimestamp;
}

QString AadsClient::bridgeSource() const {
    return m_bridgeSource;
}

QString AadsClient::naviStatus() const {
    return m_naviStatus;
}

QVariantList AadsClient::naviHistory() const {
    return m_naviHistory;
}

bool AadsClient::naviSending() const {
    return m_naviSending;
}

QString AadsClient::naviError() const {
    return m_naviError;
}

QString AadsClient::nmeaStatus() const {
    return m_nmeaStatus;
}

QString AadsClient::signalkStatus() const {
    return m_signalkStatus;
}

QString AadsClient::autopilotStatus() const {
    return m_autopilotStatus;
}

double AadsClient::autopilotDesiredHeading() const {
    return m_autopilotDesiredHeading;
}

double AadsClient::navHeading() const {
    return m_navHeading;
}

double AadsClient::navSpeed() const {
    return m_navSpeed;
}

double AadsClient::navDepth() const {
    return m_navDepth;
}

double AadsClient::navWind() const {
    return m_navWind;
}

double AadsClient::navLatitude() const {
    return m_navLatitude;
}

double AadsClient::navLongitude() const {
    return m_navLongitude;
}

bool AadsClient::signalkConnected() const {
    return m_signalkConnected;
}

QString AadsClient::wikiContent() const {
    return m_wikiContent;
}

QString AadsClient::navtexSummary() const {
    return m_navtexSummary;
}

int AadsClient::navtexWarningCount() const {
    return m_navtexWarningCount;
}

QString AadsClient::navtexLatest() const {
    return m_navtexLatest;
}

void AadsClient::fetchHealth() {
    if (m_apiUrl.isEmpty()) {
        return;
    }

    QUrl url(m_apiUrl + "/health");
    QNetworkRequest request(url);
    QNetworkReply *reply = m_network.get(request);
    connect(reply, &QNetworkReply::finished, this, [this, reply]() { onHealthFinished(reply); });
}

void AadsClient::fetchSystemStatus() {
    if (m_apiUrl.isEmpty()) {
        return;
    }

    QUrl url(m_apiUrl + "/api/v1/status");
    QNetworkRequest request(url);
    QNetworkReply *reply = m_network.get(request);
    connect(reply, &QNetworkReply::finished, this, [this, reply]() { onStatusFinished(reply); });
}

void AadsClient::fetchBridgeLatest() {
    if (m_apiUrl.isEmpty()) {
        return;
    }

    QUrl url(m_apiUrl + "/api/v1/bridge/analog");
    QNetworkRequest request(url);
    QNetworkReply *reply = m_network.get(request);
    connect(reply, &QNetworkReply::finished, this, [this, reply]() { onBridgeFinished(reply); });
}

void AadsClient::fetchModuleStatuses() {
    if (m_apiUrl.isEmpty()) {
        return;
    }

    QNetworkReply *naviReply = m_network.get(QNetworkRequest(QUrl(m_apiUrl + "/api/v1/navi/status")));
    connect(naviReply, &QNetworkReply::finished, this, [this, naviReply]() { onNaviFinished(naviReply); });

    QNetworkReply *nmeaReply = m_network.get(QNetworkRequest(QUrl(m_apiUrl + "/api/v1/nmea/status")));
    connect(nmeaReply, &QNetworkReply::finished, this, [this, nmeaReply]() { onNmeaFinished(nmeaReply); });

    QNetworkReply *signalkReply = m_network.get(QNetworkRequest(QUrl(m_apiUrl + "/api/v1/signalk/status")));
    connect(signalkReply, &QNetworkReply::finished, this, [this, signalkReply]() { onSignalKStatusFinished(signalkReply); });

    QNetworkReply *autopilotReply = m_network.get(QNetworkRequest(QUrl(m_apiUrl + "/api/v1/autopilot/status")));
    connect(autopilotReply, &QNetworkReply::finished, this, [this, autopilotReply]() { onAutopilotFinished(autopilotReply); });
}

void AadsClient::fetchSignalKNav() {
    if (m_signalkUrl.isEmpty()) {
        return;
    }

    QNetworkReply *reply = m_network.get(QNetworkRequest(QUrl(m_signalkUrl + "/api/v1/navigation")));
    connect(reply, &QNetworkReply::finished, this, [this, reply]() { onSignalKNavFinished(reply); });
}

void AadsClient::fetchNavtexSummary() {
    if (m_apiUrl.isEmpty()) {
        return;
    }

    QUrl url(m_apiUrl + "/api/v1/navigator/navtex/summary");
    QUrlQuery query;
    query.addQueryItem("limit", "10");
    url.setQuery(query);
    QNetworkReply *reply = m_network.get(QNetworkRequest(url));
    connect(reply, &QNetworkReply::finished, this, [this, reply]() { onNavtexSummaryFinished(reply); });
}

void AadsClient::loadWiki() {
    if (m_wikiPath.isEmpty()) {
        return;
    }
    QFile file(m_wikiPath);
    if (!file.open(QIODevice::ReadOnly | QIODevice::Text)) {
        return;
    }
    QString content = QString::fromUtf8(file.readAll());
    file.close();
    if (m_wikiContent != content) {
        m_wikiContent = content;
        emit wikiContentChanged();
    }
}

void AadsClient::fetchNaviHistory(int limit) {
    if (m_apiUrl.isEmpty()) {
        return;
    }

    QUrl url(m_apiUrl + "/api/v1/navi/history");
    QUrlQuery query;
    query.addQueryItem("limit", QString::number(limit));
    url.setQuery(query);
    QNetworkReply *reply = m_network.get(QNetworkRequest(url));
    connect(reply, &QNetworkReply::finished, this, [this, reply]() { onNaviHistoryFinished(reply); });
}

void AadsClient::sendNaviMessage(const QString &message) {
    if (m_apiUrl.isEmpty() || message.trimmed().isEmpty()) {
        return;
    }

    if (!m_naviSending) {
        m_naviSending = true;
        emit naviSendingChanged();
    }

    QUrl url(m_apiUrl + "/api/v1/navi/chat");
    QNetworkRequest request(url);
    request.setHeader(QNetworkRequest::ContentTypeHeader, "application/json");

    QJsonObject payload;
    payload.insert("message", message.trimmed());
    QNetworkReply *reply = m_network.post(request, QJsonDocument(payload).toJson());
    connect(reply, &QNetworkReply::finished, this, [this, reply, message]() { onNaviChatFinished(reply, message); });
}

void AadsClient::clearNaviHistory() {
    if (m_apiUrl.isEmpty()) {
        return;
    }

    QUrl url(m_apiUrl + "/api/v1/navi/clear");
    QNetworkReply *reply = m_network.post(QNetworkRequest(url), QByteArray());
    connect(reply, &QNetworkReply::finished, this, [this, reply]() { onNaviClearFinished(reply); });
}

void AadsClient::connectWs() {
    if (m_wsUrl.isEmpty()) {
        return;
    }
    if (m_ws.state() == QAbstractSocket::ConnectedState ||
        m_ws.state() == QAbstractSocket::ConnectingState) {
        return;
    }
    m_ws.open(QUrl(m_wsUrl));
}

void AadsClient::disconnectWs() {
    if (m_ws.state() == QAbstractSocket::ConnectedState ||
        m_ws.state() == QAbstractSocket::ConnectingState) {
        m_ws.close();
    }
}

void AadsClient::onHealthFinished(QNetworkReply *reply) {
    QByteArray body = reply->readAll();
    reply->deleteLater();

    QString status = "unknown";
    QVariantList services;
    if (!body.isEmpty()) {
        QJsonDocument doc = QJsonDocument::fromJson(body);
        if (doc.isObject()) {
            QJsonObject obj = doc.object();
            if (obj.contains("status")) {
                status = obj.value("status").toString("unknown");
            }
            if (obj.contains("services") && obj.value("services").isObject()) {
                QJsonObject serviceObj = obj.value("services").toObject();
                QStringList keys = serviceObj.keys();
                keys.sort();
                for (const QString &key : keys) {
                    QVariantMap entry;
                    entry["name"] = key;
                    entry["status"] = serviceObj.value(key).toString("unknown");
                    services.append(entry);
                }
            }
        }
    }

    if (m_lastHealthStatus != status) {
        m_lastHealthStatus = status;
        emit lastHealthStatusChanged();
    }

    if (!services.isEmpty()) {
        m_healthServices = services;
        emit healthServicesChanged();
    }
}

void AadsClient::onStatusFinished(QNetworkReply *reply) {
    QByteArray body = reply->readAll();
    reply->deleteLater();

    if (body.isEmpty()) {
        return;
    }

    QJsonDocument doc = QJsonDocument::fromJson(body);
    if (!doc.isObject()) {
        return;
    }

    QJsonObject obj = doc.object();
    if (obj.contains("application") && obj.value("application").isObject()) {
        QJsonObject app = obj.value("application").toObject();
        QString name = app.value("name").toString();
        QString version = app.value("version").toString();
        QString env = app.value("environment").toString();

        bool changed = false;
        if (m_appName != name) {
            m_appName = name;
            changed = true;
        }
        if (m_appVersion != version) {
            m_appVersion = version;
            changed = true;
        }
        if (m_appEnvironment != env) {
            m_appEnvironment = env;
            changed = true;
        }
        if (changed) {
            emit appInfoChanged();
        }
    }

    if (obj.contains("websocket") && obj.value("websocket").isObject()) {
        QJsonObject ws = obj.value("websocket").toObject();
        int active = ws.value("active_connections").toInt(m_wsActiveConnections);
        if (m_wsActiveConnections != active) {
            m_wsActiveConnections = active;
            emit wsInfoChanged();
        }
    }

    if (obj.contains("health") && obj.value("health").isObject()) {
        QJsonObject healthObj = obj.value("health").toObject();
        if (healthObj.contains("services") && healthObj.value("services").isObject()) {
            QJsonObject serviceObj = healthObj.value("services").toObject();
            QStringList keys = serviceObj.keys();
            keys.sort();
            QVariantList services;
            for (const QString &key : keys) {
                QVariantMap entry;
                entry["name"] = key;
                entry["status"] = serviceObj.value(key).toString("unknown");
                services.append(entry);
            }
            m_healthServices = services;
            emit healthServicesChanged();
        }
    }
}

void AadsClient::onBridgeFinished(QNetworkReply *reply) {
    QByteArray body = reply->readAll();
    reply->deleteLater();

    if (body.isEmpty()) {
        return;
    }

    QJsonDocument doc = QJsonDocument::fromJson(body);
    if (!doc.isObject()) {
        return;
    }

    QJsonObject obj = doc.object();
    if (obj.contains("status") && obj.value("status").toString() == "empty") {
        return;
    }

    onWsTextMessage(QString::fromUtf8(body));
}

static QString readStatusField(const QByteArray &body) {
    QJsonDocument doc = QJsonDocument::fromJson(body);
    if (!doc.isObject()) {
        return QString();
    }
    QJsonObject obj = doc.object();
    return obj.value("status").toString();
}

void AadsClient::onNaviFinished(QNetworkReply *reply) {
    QByteArray body = reply->readAll();
    reply->deleteLater();

    QString status = readStatusField(body);
    if (!status.isEmpty() && m_naviStatus != status) {
        m_naviStatus = status;
        emit moduleStatusChanged();
    }
}

void AadsClient::onNmeaFinished(QNetworkReply *reply) {
    QByteArray body = reply->readAll();
    reply->deleteLater();

    QString status = readStatusField(body);
    if (!status.isEmpty() && m_nmeaStatus != status) {
        m_nmeaStatus = status;
        emit moduleStatusChanged();
    }
}

void AadsClient::onSignalKStatusFinished(QNetworkReply *reply) {
    QByteArray body = reply->readAll();
    reply->deleteLater();

    QString status = readStatusField(body);
    if (!status.isEmpty() && m_signalkStatus != status) {
        m_signalkStatus = status;
        emit moduleStatusChanged();
    }
}

void AadsClient::onAutopilotFinished(QNetworkReply *reply) {
    QByteArray body = reply->readAll();
    reply->deleteLater();

    QJsonDocument doc = QJsonDocument::fromJson(body);
    if (!doc.isObject()) {
        return;
    }
    QJsonObject obj = doc.object();
    QString status = obj.value("status").toString();
    double desiredHeading = obj.value("desired_heading_deg").toDouble(m_autopilotDesiredHeading);
    bool changed = false;
    if (!status.isEmpty() && m_autopilotStatus != status) {
        m_autopilotStatus = status;
        changed = true;
    }
    if (m_autopilotDesiredHeading != desiredHeading) {
        m_autopilotDesiredHeading = desiredHeading;
        changed = true;
    }
    if (changed) {
        emit moduleStatusChanged();
    }
}

void AadsClient::onSignalKNavFinished(QNetworkReply *reply) {
    QByteArray body = reply->readAll();
    reply->deleteLater();

    QJsonDocument doc = QJsonDocument::fromJson(body);
    if (!doc.isObject()) {
        if (m_signalkConnected) {
            m_signalkConnected = false;
            emit signalkConnectedChanged();
        }
        return;
    }

    QJsonObject obj = doc.object();
    auto readNumber = [&obj](const char *key, double fallback) {
        if (!obj.contains(key)) {
            return fallback;
        }
        QJsonValue value = obj.value(key);
        if (value.isDouble()) {
            return value.toDouble();
        }
        if (value.isString()) {
            bool ok = false;
            double parsed = value.toString().toDouble(&ok);
            return ok ? parsed : fallback;
        }
        return fallback;
    };

    bool changed = false;
    double heading = readNumber("heading", m_navHeading);
    double speed = readNumber("speed", m_navSpeed);
    double depth = readNumber("depth", m_navDepth);
    double wind = readNumber("wind", m_navWind);
    double latitude = readNumber("latitude", m_navLatitude);
    double longitude = readNumber("longitude", m_navLongitude);

    if (m_navHeading != heading) {
        m_navHeading = heading;
        changed = true;
    }
    if (m_navSpeed != speed) {
        m_navSpeed = speed;
        changed = true;
    }
    if (m_navDepth != depth) {
        m_navDepth = depth;
        changed = true;
    }
    if (m_navWind != wind) {
        m_navWind = wind;
        changed = true;
    }
    if (m_navLatitude != latitude || m_navLongitude != longitude) {
        m_navLatitude = latitude;
        m_navLongitude = longitude;
        emit navPositionChanged();
    }

    if (!m_signalkConnected) {
        m_signalkConnected = true;
        emit signalkConnectedChanged();
    }

    if (changed) {
        emit navDataChanged();
    }
}

void AadsClient::onNavtexSummaryFinished(QNetworkReply *reply) {
    QByteArray body = reply->readAll();
    reply->deleteLater();

    QJsonDocument doc = QJsonDocument::fromJson(body);
    if (!doc.isObject()) {
        return;
    }
    QJsonObject obj = doc.object();
    int total = obj.value("total").toInt(0);
    QJsonObject severity = obj.value("counts_by_severity").toObject();
    int warnings = severity.value("WARNING").toInt(0) + severity.value("CRITICAL").toInt(0);
    QJsonObject latest = obj.value("latest").toObject();

    QString latestText;
    if (!latest.isEmpty()) {
        latestText = QString("%1 %2 [%3]")
                         .arg(latest.value("type").toString())
                         .arg(latest.value("id").toString())
                         .arg(latest.value("severity").toString());
    }

    QString summary = QString("NAVTEX: %1 msgs, %2 warnings").arg(total).arg(warnings);
    bool changed = false;
    if (m_navtexSummary != summary) {
        m_navtexSummary = summary;
        changed = true;
    }
    if (m_navtexWarningCount != warnings) {
        m_navtexWarningCount = warnings;
        changed = true;
    }
    if (m_navtexLatest != latestText) {
        m_navtexLatest = latestText;
        changed = true;
    }
    if (changed) {
        emit navtexSummaryChanged();
    }
}

void AadsClient::onNaviHistoryFinished(QNetworkReply *reply) {
    QByteArray body = reply->readAll();
    reply->deleteLater();

    QJsonDocument doc = QJsonDocument::fromJson(body);
    if (!doc.isObject()) {
        return;
    }

    QJsonObject obj = doc.object();
    if (!obj.contains("history") || !obj.value("history").isArray()) {
        return;
    }

    QJsonArray history = obj.value("history").toArray();
    QVariantList list;
    for (const QJsonValue &entry : history) {
        if (!entry.isObject()) {
            continue;
        }
        QJsonObject msg = entry.toObject();
        QVariantMap row;
        row["role"] = msg.value("role").toString();
        row["content"] = msg.value("content").toString();
        row["timestamp"] = msg.value("timestamp").toString();
        list.append(row);
    }

    m_naviHistory = list;
    emit naviHistoryChanged();
}

void AadsClient::onNaviChatFinished(QNetworkReply *reply, const QString &message) {
    QByteArray body = reply->readAll();
    QNetworkReply::NetworkError netError = reply->error();
    reply->deleteLater();

    if (m_naviSending) {
        m_naviSending = false;
        emit naviSendingChanged();
    }

    QString error;
    if (netError != QNetworkReply::NoError) {
        error = reply->errorString();
    }
    QJsonDocument doc = QJsonDocument::fromJson(body);
    if (!doc.isObject()) {
        if (error.isEmpty()) {
            error = "Invalid response";
        }
    }

    if (error.isEmpty()) {
        QJsonObject obj = doc.object();
        QString response = obj.value("response").toString();
        QString timestamp = obj.value("timestamp").toString();

        QVariantMap userMsg;
        userMsg["role"] = "user";
        userMsg["content"] = message.trimmed();
        userMsg["timestamp"] = timestamp;

        QVariantMap botMsg;
        botMsg["role"] = "assistant";
        botMsg["content"] = response;
        botMsg["timestamp"] = timestamp;

        m_naviHistory.append(userMsg);
        m_naviHistory.append(botMsg);
        emit naviHistoryChanged();
        if (!m_naviError.isEmpty()) {
            m_naviError.clear();
            emit naviErrorChanged();
        }
    } else {
        m_naviError = error;
        emit naviErrorChanged();
    }
}

void AadsClient::onNaviClearFinished(QNetworkReply *reply) {
    reply->deleteLater();
    m_naviHistory.clear();
    emit naviHistoryChanged();
}

void AadsClient::onWsConnected() {
    if (!m_wsConnected) {
        m_wsConnected = true;
        emit wsConnectedChanged();
    }
}

void AadsClient::onWsDisconnected() {
    if (m_wsConnected) {
        m_wsConnected = false;
        emit wsConnectedChanged();
    }
}

void AadsClient::onWsTextMessage(const QString &message) {
    m_lastWsMessage = message.left(400);
    emit lastWsMessageChanged();

    QJsonDocument doc = QJsonDocument::fromJson(message.toUtf8());
    if (!doc.isObject()) {
        return;
    }

    QJsonObject obj = doc.object();
    QString type = obj.value("type").toString();
    if (type != "bridge") {
        if (type == "nmea" && obj.contains("data") && obj.value("data").isObject()) {
            QJsonObject data = obj.value("data").toObject();
            if (data.contains("latitude") && data.contains("longitude")) {
                double lat = data.value("latitude").toDouble(m_navLatitude);
                double lon = data.value("longitude").toDouble(m_navLongitude);
                if (m_navLatitude != lat || m_navLongitude != lon) {
                    m_navLatitude = lat;
                    m_navLongitude = lon;
                    emit navPositionChanged();
                }
            }
            if (data.contains("heading")) {
                double heading = data.value("heading").toDouble(m_navHeading);
                if (m_navHeading != heading) {
                    m_navHeading = heading;
                    emit navDataChanged();
                }
            }
        }
        if (type == "signalk" && obj.contains("data") && obj.value("data").isObject()) {
            QJsonObject data = obj.value("data").toObject();
            if (data.contains("navigation") && data.value("navigation").isObject()) {
                QJsonObject nav = data.value("navigation").toObject();
                if (nav.contains("latitude") && nav.contains("longitude")) {
                    double lat = nav.value("latitude").toDouble(m_navLatitude);
                    double lon = nav.value("longitude").toDouble(m_navLongitude);
                    if (m_navLatitude != lat || m_navLongitude != lon) {
                        m_navLatitude = lat;
                        m_navLongitude = lon;
                        emit navPositionChanged();
                    }
                }
                if (nav.contains("heading")) {
                    double heading = nav.value("heading").toDouble(m_navHeading);
                    if (m_navHeading != heading) {
                        m_navHeading = heading;
                        emit navDataChanged();
                    }
                }
            }
        }
        return;
    }

    QString timestamp = obj.value("timestamp").toString();
    if (m_bridgeTimestamp != timestamp) {
        m_bridgeTimestamp = timestamp;
        emit bridgeTimestampChanged();
    }

    if (obj.contains("data") && obj.value("data").isObject()) {
        QJsonObject data = obj.value("data").toObject();
        QString source = data.value("source").toString();
        if (m_bridgeSource != source) {
            m_bridgeSource = source;
            emit bridgeSourceChanged();
        }

        if (data.contains("signals") && data.value("signals").isObject()) {
            QJsonObject signalObj = data.value("signals").toObject();
            QStringList keys = signalObj.keys();
            keys.sort();
            QVariantList list;
            for (const QString &key : keys) {
                QVariantMap entry;
                entry["name"] = key;
                entry["value"] = signalObj.value(key).toVariant();
                list.append(entry);
            }
            m_bridgeSignals = list;
            emit bridgeSignalsChanged();
        }
    }
}

void AadsClient::onWsError(QAbstractSocket::SocketError error) {
    Q_UNUSED(error);
    if (m_wsConnected) {
        m_wsConnected = false;
        emit wsConnectedChanged();
    }
}
