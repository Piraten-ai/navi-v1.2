#pragma once

#include <QObject>
#include <QNetworkAccessManager>
#include <QNetworkReply>
#include <QUrl>
#include <QVariantList>
#include <QWebSocket>

class AadsClient : public QObject {
    Q_OBJECT
    Q_PROPERTY(QString apiUrl READ apiUrl WRITE setApiUrl NOTIFY apiUrlChanged)
    Q_PROPERTY(QString wsUrl READ wsUrl WRITE setWsUrl NOTIFY wsUrlChanged)
    Q_PROPERTY(QString signalkUrl READ signalkUrl WRITE setSignalkUrl NOTIFY signalkUrlChanged)
    Q_PROPERTY(QString wikiPath READ wikiPath WRITE setWikiPath NOTIFY wikiPathChanged)
    Q_PROPERTY(bool wsConnected READ wsConnected NOTIFY wsConnectedChanged)
    Q_PROPERTY(QString lastHealthStatus READ lastHealthStatus NOTIFY lastHealthStatusChanged)
    Q_PROPERTY(QString lastWsMessage READ lastWsMessage NOTIFY lastWsMessageChanged)
    Q_PROPERTY(QVariantList healthServices READ healthServices NOTIFY healthServicesChanged)
    Q_PROPERTY(QString appName READ appName NOTIFY appInfoChanged)
    Q_PROPERTY(QString appVersion READ appVersion NOTIFY appInfoChanged)
    Q_PROPERTY(QString appEnvironment READ appEnvironment NOTIFY appInfoChanged)
    Q_PROPERTY(int wsActiveConnections READ wsActiveConnections NOTIFY wsInfoChanged)
    Q_PROPERTY(QVariantList bridgeSignals READ bridgeSignals NOTIFY bridgeSignalsChanged)
    Q_PROPERTY(QString bridgeTimestamp READ bridgeTimestamp NOTIFY bridgeTimestampChanged)
    Q_PROPERTY(QString bridgeSource READ bridgeSource NOTIFY bridgeSourceChanged)
    Q_PROPERTY(QString naviStatus READ naviStatus NOTIFY moduleStatusChanged)
    Q_PROPERTY(QVariantList naviHistory READ naviHistory NOTIFY naviHistoryChanged)
    Q_PROPERTY(bool naviSending READ naviSending NOTIFY naviSendingChanged)
    Q_PROPERTY(QString naviError READ naviError NOTIFY naviErrorChanged)
    Q_PROPERTY(QString nmeaStatus READ nmeaStatus NOTIFY moduleStatusChanged)
    Q_PROPERTY(QString signalkStatus READ signalkStatus NOTIFY moduleStatusChanged)
    Q_PROPERTY(QString autopilotStatus READ autopilotStatus NOTIFY moduleStatusChanged)
    Q_PROPERTY(double autopilotDesiredHeading READ autopilotDesiredHeading NOTIFY moduleStatusChanged)
    Q_PROPERTY(double navHeading READ navHeading NOTIFY navDataChanged)
    Q_PROPERTY(double navSpeed READ navSpeed NOTIFY navDataChanged)
    Q_PROPERTY(double navDepth READ navDepth NOTIFY navDataChanged)
    Q_PROPERTY(double navWind READ navWind NOTIFY navDataChanged)
    Q_PROPERTY(double navLatitude READ navLatitude NOTIFY navPositionChanged)
    Q_PROPERTY(double navLongitude READ navLongitude NOTIFY navPositionChanged)
    Q_PROPERTY(bool signalkConnected READ signalkConnected NOTIFY signalkConnectedChanged)
    Q_PROPERTY(QString wikiContent READ wikiContent NOTIFY wikiContentChanged)
    Q_PROPERTY(QString navtexSummary READ navtexSummary NOTIFY navtexSummaryChanged)
    Q_PROPERTY(int navtexWarningCount READ navtexWarningCount NOTIFY navtexSummaryChanged)
    Q_PROPERTY(QString navtexLatest READ navtexLatest NOTIFY navtexSummaryChanged)

public:
    explicit AadsClient(QObject *parent = nullptr);

    QString apiUrl() const;
    void setApiUrl(const QString &url);

    QString wsUrl() const;
    void setWsUrl(const QString &url);

    QString signalkUrl() const;
    void setSignalkUrl(const QString &url);

    QString wikiPath() const;
    void setWikiPath(const QString &path);

    bool wsConnected() const;

    QString lastHealthStatus() const;
    QString lastWsMessage() const;
    QVariantList healthServices() const;
    QString appName() const;
    QString appVersion() const;
    QString appEnvironment() const;
    int wsActiveConnections() const;
    QVariantList bridgeSignals() const;
    QString bridgeTimestamp() const;
    QString bridgeSource() const;
    QString naviStatus() const;
    QVariantList naviHistory() const;
    bool naviSending() const;
    QString naviError() const;
    QString nmeaStatus() const;
    QString signalkStatus() const;
    QString autopilotStatus() const;
    double autopilotDesiredHeading() const;
    double navHeading() const;
    double navSpeed() const;
    double navDepth() const;
    double navWind() const;
    double navLatitude() const;
    double navLongitude() const;
    bool signalkConnected() const;
    QString wikiContent() const;
    QString navtexSummary() const;
    int navtexWarningCount() const;
    QString navtexLatest() const;

    Q_INVOKABLE void fetchHealth();
    Q_INVOKABLE void fetchSystemStatus();
    Q_INVOKABLE void fetchBridgeLatest();
    Q_INVOKABLE void fetchModuleStatuses();
    Q_INVOKABLE void fetchSignalKNav();
    Q_INVOKABLE void fetchNavtexSummary();
    Q_INVOKABLE void loadWiki();
    Q_INVOKABLE void fetchNaviHistory(int limit = 30);
    Q_INVOKABLE void sendNaviMessage(const QString &message);
    Q_INVOKABLE void clearNaviHistory();
    Q_INVOKABLE void connectWs();
    Q_INVOKABLE void disconnectWs();

signals:
    void apiUrlChanged();
    void wsUrlChanged();
    void wsConnectedChanged();
    void lastHealthStatusChanged();
    void lastWsMessageChanged();
    void healthServicesChanged();
    void appInfoChanged();
    void wsInfoChanged();
    void bridgeSignalsChanged();
    void bridgeTimestampChanged();
    void bridgeSourceChanged();
    void moduleStatusChanged();
    void navDataChanged();
    void navPositionChanged();
    void signalkUrlChanged();
    void signalkConnectedChanged();
    void wikiPathChanged();
    void wikiContentChanged();
    void navtexSummaryChanged();
    void naviHistoryChanged();
    void naviSendingChanged();
    void naviErrorChanged();

private slots:
    void onHealthFinished(QNetworkReply *reply);
    void onStatusFinished(QNetworkReply *reply);
    void onBridgeFinished(QNetworkReply *reply);
    void onNaviFinished(QNetworkReply *reply);
    void onNmeaFinished(QNetworkReply *reply);
    void onSignalKStatusFinished(QNetworkReply *reply);
    void onAutopilotFinished(QNetworkReply *reply);
    void onSignalKNavFinished(QNetworkReply *reply);
    void onNavtexSummaryFinished(QNetworkReply *reply);
    void onNaviHistoryFinished(QNetworkReply *reply);
    void onNaviChatFinished(QNetworkReply *reply, const QString &message);
    void onNaviClearFinished(QNetworkReply *reply);
    void onWsConnected();
    void onWsDisconnected();
    void onWsTextMessage(const QString &message);
    void onWsError(QAbstractSocket::SocketError error);

private:
    QNetworkAccessManager m_network;
    QWebSocket m_ws;
    QString m_apiUrl;
    QString m_wsUrl;
    QString m_signalkUrl;
    QString m_wikiPath;
    QString m_lastHealthStatus;
    QString m_lastWsMessage;
    QVariantList m_healthServices;
    QString m_appName;
    QString m_appVersion;
    QString m_appEnvironment;
    int m_wsActiveConnections = 0;
    QVariantList m_bridgeSignals;
    QString m_bridgeTimestamp;
    QString m_bridgeSource;
    QString m_naviStatus;
    QVariantList m_naviHistory;
    bool m_naviSending = false;
    QString m_naviError;
    QString m_nmeaStatus;
    QString m_signalkStatus;
    QString m_autopilotStatus;
    double m_autopilotDesiredHeading = 0.0;
    double m_navHeading = 0.0;
    double m_navSpeed = 0.0;
    double m_navDepth = 0.0;
    double m_navWind = 0.0;
    double m_navLatitude = 0.0;
    double m_navLongitude = 0.0;
    bool m_signalkConnected = false;
    bool m_wsConnected = false;
    QString m_wikiContent;
    QString m_navtexSummary;
    int m_navtexWarningCount = 0;
    QString m_navtexLatest;
};
