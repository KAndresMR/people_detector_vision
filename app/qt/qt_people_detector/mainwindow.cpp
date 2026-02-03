#include "mainwindow.h"

#include <QLabel>
#include <QPushButton>
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QStatusBar>
#include <QDebug>
#include <QCloseEvent>

#include <QNetworkAccessManager>
#include <QNetworkRequest>
#include <QNetworkReply>
#include <QHttpMultiPart>
#include <QBuffer>

#ifdef __APPLE__
#include <mach/mach.h>
#elif defined(_WIN32)
#include <windows.h>
#include <psapi.h>
#endif


MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent),
    cameraTimer(new QTimer(this)),
    networkManager(new QNetworkAccessManager(this))
{
    setupUI();

    connect(cameraTimer, &QTimer::timeout,
            this, &MainWindow::processFrame);
}


MainWindow::~MainWindow(){}

void MainWindow::processFrame()
{
    cv::Mat frame;
    cap >> frame;

    if (frame.empty()) return;

    // ---------- HOG Detection ----------
    if (detectionEnabled && humanDetector.isLoaded()) {
        // Reducimos el frame ya que HOG es carisimo
        cv::Mat resized;
        cv::resize(frame, resized, cv::Size(), 0.5, 0.5);

        // Deteccion sobre el frame pequeño
        auto boxes = humanDetector.detect(resized);

        bool detectedNow = !boxes.empty();
        if (detectedNow) {
            humanPresent = true;
            humanLostTimer.restart();
        } else {
            if (humanPresent && humanLostTimer.elapsed() > HUMAN_LOST_MS) {
                humanPresent = false;
                eventTriggered = false;
            }
        }

        if (humanPresent && !eventTriggered) {
            eventTriggered = true;

            cv::Mat frameBGR = frame.clone();
            sendImageToAPI(frameBGR);
        }


        // Escalado de las cajas
        for (const auto& box : boxes) {
            cv::Rect scaledBox(
                box.x * 2,
                box.y * 2,
                box.width * 2,
                box.height * 2
                );
            // Dibujo Final
            cv::rectangle(frame, scaledBox, cv::Scalar(0, 255, 0), 2);
        }
    }

    // ---------- Convert for Qt ----------
    cv::Mat rgbFrame;
    cv::Mat frameBGR = frame.clone();
    cv::cvtColor(frame, rgbFrame, cv::COLOR_BGR2RGB);

    QImage image(
        rgbFrame.data,
        rgbFrame.cols,
        rgbFrame.rows,
        rgbFrame.step,
        QImage::Format_RGB888
        );

    // Renderizado en la UI
    videoLabel->setPixmap(
        QPixmap::fromImage(image)
            .scaled(videoLabel->size(),
                    Qt::KeepAspectRatio,
                    Qt::SmoothTransformation)
        );



    // ---------- FPS & RAM ----------
    frameCount++;
    qint64 elapsed = fpsTimer.elapsed();

    if (elapsed >= 1000) {
        double fps = frameCount * 1000.0 / elapsed;
        fpsLabel->setText(QString("FPS: %1").arg(fps, 0, 'f', 1));

        size_t ramMB = getCurrentRAMUsageMB();
        ramLabel->setText(QString("RAM: %1 MB").arg(ramMB));

        frameCount = 0;
        fpsTimer.restart();
    }
}


void MainWindow::sendImageToAPI(const cv::Mat& frame){
    static bool sending = false;
    if (sending) return;   // protección extra
    sending = true;

    // Codificar imagen a JPG
    std::vector<uchar> buffer;
    cv::imencode(".jpg", frame, buffer);

    QByteArray imageData(reinterpret_cast<const char*>(buffer.data()), buffer.size());

    // Multipart
    QHttpMultiPart* multiPart = new QHttpMultiPart(QHttpMultiPart::FormDataType);

    QHttpPart imagePart;
    imagePart.setHeader(QNetworkRequest::ContentDispositionHeader,
                        QVariant("form-data; name=\"file\"; filename=\"frame.jpg\""));
    imagePart.setBody(imageData);

    multiPart->append(imagePart);

    // Request
    QNetworkRequest request(QUrl("http://127.0.0.1:8000/send/image"));

    QNetworkReply* reply = networkManager->post(request, multiPart);
    multiPart->setParent(reply);

    connect(reply, &QNetworkReply::finished, this, [reply]() {
        reply->deleteLater();
        qDebug() << "[API] Image sent";
        sending = false;
    });
}

void MainWindow::setupUI()
{
    // ---------- Central Widget ----------
    QWidget* centralWidget = new QWidget(this);
    setCentralWidget(centralWidget);

    // ---------- Video Area ----------
    videoLabel = new QLabel("Camera not started");
    videoLabel->setAlignment(Qt::AlignCenter);
    videoLabel->setStyleSheet(
        "QLabel { background-color: black; color: white; font-size: 16px; }"
    );
    videoLabel->setMinimumSize(640, 480);

    // ---------- Buttons ----------
    QHBoxLayout* buttonLayout = new QHBoxLayout();
    startButton = new QPushButton("Start Camera");
    stopButton  = new QPushButton("Stop Camera");
    connect(startButton, &QPushButton::clicked, this, &MainWindow::onStartCamera);
    connect(stopButton, &QPushButton::clicked, this, &MainWindow::onStopCamera);
    buttonLayout->addStretch();
    buttonLayout->addWidget(startButton);
    buttonLayout->addWidget(stopButton);
    buttonLayout->addStretch();


    // ---------- Main Layout ----------
    QVBoxLayout* mainLayout = new QVBoxLayout();
    mainLayout->addWidget(videoLabel);
    mainLayout->addLayout(buttonLayout);
    centralWidget->setLayout(mainLayout);

    // ---------- Status Bar ----------
    fpsLabel = new QLabel("FPS: --");
    ramLabel = new QLabel("RAM: --");
    statusBar()->addPermanentWidget(fpsLabel);
    statusBar()->addPermanentWidget(ramLabel);

    // ---------- Window Properties ----------
    setWindowTitle("Human Detection System");
    resize(800, 600);
}

// ===== RAM monitoring =====

size_t MainWindow::getCurrentRAMUsageMB()
{
#ifdef __APPLE__
    mach_task_basic_info info;
    mach_msg_type_number_t count = MACH_TASK_BASIC_INFO_COUNT;

    if (task_info(mach_task_self(),
                  MACH_TASK_BASIC_INFO,
                  reinterpret_cast<task_info_t>(&info),
                  &count) != KERN_SUCCESS) {
        return 0;
    }

    return info.resident_size / (1024 * 1024);

#elif defined(_WIN32)
    PROCESS_MEMORY_COUNTERS pmc;
    if (GetProcessMemoryInfo(GetCurrentProcess(), &pmc, sizeof(pmc))) {
        return pmc.WorkingSetSize / (1024 * 1024);
    }
    return 0;

#else
    return 0;
#endif
}

void MainWindow::closeEvent(QCloseEvent *event)
{
    if (cameraTimer->isActive()) {
        cameraTimer->stop();
    }
    if (cap.isOpened()) {
        cap.release();
    }
    event->accept();
}


void MainWindow::onStartCamera()
{
    if (!cap.open(0)) {
        qDebug() << "[ERROR] Cannot open camera";
        return;
    }
    detectionEnabled = true;

    frameCount = 0;
    fpsTimer.restart();

    cameraTimer->start(30); // ~33 FPS
    qDebug() << "[INFO] Camera started";
    statusBar()->showMessage("Camera started");
}

void MainWindow::onStopCamera()
{
    cameraTimer->stop();
    cap.release();

    videoLabel->setText("Camera stopped");
    qDebug() << "[INFO] Camera stopped";
    statusBar()->showMessage("Camera stopped");
}



