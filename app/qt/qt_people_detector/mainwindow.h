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
    QLabel* fpsLabel;
    QLabel* ramLabel;

    void setupUI();

    // ===== Camera =====
    cv::VideoCapture cap;
    QTimer* cameraTimer;

    void processFrame();

    // ===== Metrics =====
    QElapsedTimer fpsTimer;
    int frameCount = 0;

    // ===== Human Detector =====
    HumanDetector humanDetector;
    bool detectionEnabled = false;

    size_t getCurrentRAMUsageMB();
};

#endif // MAINWINDOW_H
