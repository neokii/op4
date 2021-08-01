#include "selfdrive/ui/qt/widgets/prime.h"

#include <QDebug>
#include <QJsonDocument>
#include <QJsonObject>
#include <QLabel>
#include <QPushButton>
#include <QStackedWidget>
#include <QTimer>
#include <QVBoxLayout>
#include <QrCode.hpp>

#include "selfdrive/ui/qt/request_repeater.h"

using qrcodegen::QrCode;

PairingQRWidget::PairingQRWidget(QWidget* parent) : QWidget(parent) {
  qrCode = new QLabel;
  qrCode->setScaledContents(true);
  QVBoxLayout* main_layout = new QVBoxLayout(this);
  main_layout->addWidget(qrCode, 0, Qt::AlignCenter);

  QTimer* timer = new QTimer(this);
  timer->start(30 * 1000);
  connect(timer, &QTimer::timeout, this, &PairingQRWidget::refresh);
}

void PairingQRWidget::showEvent(QShowEvent *event) {
  refresh();
}

void PairingQRWidget::refresh(){
  Params params;
  QString IMEI = QString::fromStdString(params.get("IMEI"));
  QString serial = QString::fromStdString(params.get("HardwareSerial"));

  if (std::min(IMEI.length(), serial.length()) <= 5) {
    qrCode->setText("Error getting serial: contact support");
    qrCode->setWordWrap(true);
    qrCode->setStyleSheet(R"(font-size: 60px;)");
    return;
  }
  QString pairToken = CommaApi::create_jwt({{"pair", true}});
  
  QString qrString = IMEI + "--" + serial + "--" + pairToken;
  this->updateQrCode(qrString);
}

void PairingQRWidget::updateQrCode(const QString &text) {
  QrCode qr = QrCode::encodeText(text.toUtf8().data(), QrCode::Ecc::LOW);
  qint32 sz = qr.getSize();
  // make the image larger so we can have a white border
  QImage im(sz + 2, sz + 2, QImage::Format_RGB32);
  QRgb black = qRgb(0, 0, 0);
  QRgb white = qRgb(255, 255, 255);

  for (int y = 0; y < sz + 2; y++) {
    for (int x = 0; x < sz + 2; x++) {
      im.setPixel(x, y, white);
    }
  }
  for (int y = 0; y < sz; y++) {
    for (int x = 0; x < sz; x++) {
      im.setPixel(x + 1, y + 1, qr.getModule(x, y) ? black : white);
    }
  }
  // Integer division to prevent anti-aliasing
  int approx500 = (500 / (sz + 2)) * (sz + 2);
  qrCode->setPixmap(QPixmap::fromImage(im.scaled(approx500, approx500, Qt::KeepAspectRatio, Qt::FastTransformation), Qt::MonoOnly));
  qrCode->setFixedSize(approx500, approx500);
}

PrimeUserWidget::PrimeUserWidget(QWidget* parent) : QWidget(parent) {
  mainLayout = new QVBoxLayout(this);
  mainLayout->setMargin(0);
  mainLayout->setSpacing(30);

  QLabel* commaPrime = new QLabel("RetroPilot Online");
  mainLayout->addWidget(commaPrime, 0, Qt::AlignTop);

  username = new QLabel();
  QLabel* RetroPilot = new QLabel("Circuit Pro HKG");
  mainLayout->addWidget(RetroPilot, 0, Qt::AlignTop);
  username->setStyleSheet("font-size: 53px;"); // TODO: fit width

  mainLayout->addWidget(username, 0, Qt::AlignTop);

  mainLayout->addSpacing(50);

  QLabel* commaPoints = new QLabel("Welcome To The Community!");
  commaPoints->setStyleSheet(R"(
    color: #b8b8b8;
    font-size: 43px
  )");

  QLabel* discordMessage = new QLabel("Please Join Our Discord.");
  discordMessage->setStyleSheet(R"(
    color: #b8b8b8;
    font-size: 43px
  )");

  QLabel* discordLink = new QLabel("https://discord.gg/zWSnqJ6rKD");
  discordLink->setStyleSheet(R"(
    color: #b8b8b8;
    font-size: 40px
  )");

  mainLayout->addWidget(commaPoints, 0, Qt::AlignTop);
  mainLayout->addWidget(discordMessage, 0, Qt::AlignTop);
  mainLayout->addWidget(discordLink, 0, Qt::AlignTop);

  QLabel* GitHub = new QLabel("https://github.com/Circuit-Pro/openpilot");
  GitHub->setStyleSheet(R"(
    font-size: 31px;
    color: #b8b8b8;
  )");
  mainLayout->addWidget(GitHub, 0, Qt::AlignTop);

  mainLayout->addWidget(pointsWidget);

  mainLayout->addStretch();

  // set up API requests
  std::string dongleId = Params().get("DongleId");
  if (util::is_valid_dongle_id(dongleId)) {
    std::string url = "https://api.retropilot.org/v1.1/devices/" + dongleId + "/owner";
    RequestRepeater *repeater = new RequestRepeater(this, QString::fromStdString(url), "ApiCache_Owner", 6);
    QObject::connect(repeater, &RequestRepeater::receivedResponse, this, &PrimeUserWidget::replyFinished);
  }
}

void PrimeUserWidget::replyFinished(const QString &response) {
  QJsonDocument doc = QJsonDocument::fromJson(response.toUtf8());
  if (doc.isNull()) {
    qDebug() << "JSON Parse failed on getting points";
    return;
  }

  QJsonObject json = doc.object();
  points->setText(QString::number(json["points"].toInt()));
}

PrimeAdWidget::PrimeAdWidget(QWidget* parent) : QFrame(parent) {
  QVBoxLayout* main_layout = new QVBoxLayout(this);
  main_layout->setContentsMargins(80, 90, 80, 60);
  main_layout->setSpacing(0);

  main_layout->addWidget(new QLabel("RetroPilot is Down."), 1, Qt::AlignTop);

  QLabel* description = new QLabel("If you are seeing this somethings not right!");
  description->setStyleSheet(R"(
    font-size: 50px;
    color: #b8b8b8;
  )");
  description->setWordWrap(true);
  main_layout->addWidget(description, 2, Qt::AlignTop);

  QVector<QString> features = {"Not Right", "RetroPilot", "Services Down"};
  for (auto &f: features) {
    QLabel* feature = new QLabel(f);
    feature->setStyleSheet(R"(font-size: 40px;)");
    main_layout->addWidget(feature, 0, Qt::AlignBottom);
  }

  setStyleSheet(R"(
    PrimeAdWidget {
      border-radius: 10px;
      background-color: #333333;
    }
  )");
}


SetupWidget::SetupWidget(QWidget* parent) : QFrame(parent) {
  mainLayout = new QStackedWidget;

  // Unpaired, registration prompt layout

  QWidget* finishRegistration = new QWidget;
  finishRegistration->setObjectName("primeWidget");
  QVBoxLayout* finishRegistationLayout = new QVBoxLayout(finishRegistration);
  finishRegistationLayout->setContentsMargins(30, 75, 30, 45);
  finishRegistationLayout->setSpacing(0);

  QLabel* registrationDescription = new QLabel("Pair your device at api.RetroPilot.org/useradmin");
  registrationDescription->setWordWrap(true);
  registrationDescription->setAlignment(Qt::AlignCenter);
  registrationDescription->setStyleSheet(R"(
    font-size: 55px;
    font-weight: 400;
  )");

  finishRegistationLayout->addSpacing(30);

  QLabel* registrationDescription = new QLabel("Pair your device with comma connect (connect.comma.ai) and claim your comma prime offer.");
  registrationDescription->setWordWrap(true);
  registrationDescription->setStyleSheet("font-size: 55px; font-weight: light; margin-left: 55px;");
  finishRegistationLayout->addWidget(registrationDescription);

  finishRegistationLayout->addStretch();

  QPushButton* finishButton = new QPushButton("Pair device");
  finishButton->setFixedHeight(220);
  finishButton->setStyleSheet(R"(
    QPushButton {
      font-size: 55px;
      font-weight: 400;
      border-radius: 10px;
      background-color: #465BEA;
    }
    QPushButton:pressed {
      background-color: #3049F4;
    }
  )");
  finishRegistationLayout->addWidget(finishButton);
  QObject::connect(finishButton, &QPushButton::clicked, this, &SetupWidget::showQrCode);

  mainLayout->addWidget(finishRegistration);

  // Pairing QR code layout

  QWidget* q = new QWidget;
  q->setObjectName("primeWidget");
  QVBoxLayout* qrLayout = new QVBoxLayout(q);
  qrLayout->setContentsMargins(90, 90, 90, 90);

  QLabel* qrLabel = new QLabel("Scan the QR code to pair.");
  qrLabel->setAlignment(Qt::AlignHCenter);
  qrLabel->setStyleSheet("font-size: 47px; font-weight: light;");
  qrLayout->addWidget(qrLabel);
  qrLayout->addSpacing(50);

  qrLayout->addWidget(new PairingQRWidget);
  qrLayout->addStretch();

  // setup widget
  QVBoxLayout *outer_layout = new QVBoxLayout(this);
  outer_layout->setContentsMargins(0, 0, 0, 0);
  outer_layout->addWidget(mainLayout);

  mainLayout->addWidget(q);

  primeAd = new PrimeAdWidget;
  mainLayout->addWidget(primeAd);

  primeUser = new PrimeUserWidget;
  mainLayout->addWidget(primeUser);

  mainLayout->setCurrentWidget(primeAd);

  setFixedWidth(750);
  setStyleSheet(R"(
    #primeWidget {
      border-radius: 10px;
      background-color: #333333;
    }
  )");

  // Retain size while hidden
  QSizePolicy sp_retain = sizePolicy();
  sp_retain.setRetainSizeWhenHidden(true);
  setSizePolicy(sp_retain);

  // set up API requests
  std::string dongleId = Params().get("DongleId");
  if (util::is_valid_dongle_id(dongleId)) {
    std::string url = "https://api.retropilot.org/v1.1/devices/" + dongleId + "/";
    RequestRepeater* repeater = new RequestRepeater(this, QString::fromStdString(url), "ApiCache_Device", 5);

    QObject::connect(repeater, &RequestRepeater::receivedResponse, this, &SetupWidget::replyFinished);
    QObject::connect(repeater, &RequestRepeater::failedResponse, this, &SetupWidget::parseError);
  }
  hide(); // Only show when first request comes back
}

void SetupWidget::parseError(const QString &response) {
  show();
  if (mainLayout->currentIndex() == 1) {
    showQr = false;
    mainLayout->setCurrentIndex(0);
  }
}

void SetupWidget::showQrCode() {
  showQr = true;
  mainLayout->setCurrentIndex(1);
}

void SetupWidget::replyFinished(const QString &response) {
  show();
  QJsonDocument doc = QJsonDocument::fromJson(response.toUtf8());
  if (doc.isNull()) {
    qDebug() << "JSON Parse failed on getting pairing and prime status";
    return;
  }

  QJsonObject json = doc.object();
  if (!json["is_paired"].toBool()) {
    mainLayout->setCurrentIndex(showQr);
  } else if (!json["prime"].toBool()) {
    showQr = false;
    mainLayout->setCurrentWidget(primeAd);
  } else {
    showQr = false;
    mainLayout->setCurrentWidget(primeUser);
  }
}
