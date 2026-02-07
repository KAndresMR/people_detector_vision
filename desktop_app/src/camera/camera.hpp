#pragma once
#include <opencv2/opencv.hpp>

class Camera {
public:
    Camera(int index = 0);
    bool isOpened() const;
    cv::Mat getFrame();
    void release();

private:
    cv::VideoCapture cap;
};
