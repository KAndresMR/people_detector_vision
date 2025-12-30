#ifndef MAINWINDOW_H
#define MAINWINDOW_H

// Qt
#include <QMainWindow>
#include <QTimer>
#include <QElapsedTimer>
#include "vision/HumanDetector.h"

// OpenCV
#include <opencv2/opencv.hpp>

// Forward declarations
class QLabel;
class QPushButton;
class QNetworkAccessManager;

class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    explicit MainWindow(QWidget *parent = nullptr);
    ~MainWindow();

protected:
    void closeEvent(QCloseEvent *event) override;

private slots:
    void onStartCamera();
    void onStopCamera();

private:
    // ===== UI =====
    QLabel* videoLabel;
    QPushButton* startButton;
    QPushButton* stopButton;
    void setupUI();

    // ===== RAM y FPS =====
    QLabel* fpsLabel;
    QLabel* ramLabel;

    // ===== Camera =====
    cv::VideoCapture cap;
    QTimer* cameraTimer;
    bool humanPresent = false;
    bool eventTriggered = false;
    void processFrame();

    // ===== Metrics =====
    QElapsedTimer fpsTimer;
    int frameCount = 0;

    // ===== Human Detector =====
    HumanDetector humanDetector;
    bool detectionEnabled = false;
    void sendImageToAPI(const cv::Mat& frame);
    QElapsedTimer humanLostTimer;
    const int HUMAN_LOST_MS = 1500; // 1.5 segundos
    size_t getCurrentRAMUsageMB();
    QNetworkAccessManager* networkManager;

};

#endif // MAINWINDOW_H
