#pragma once
#include <opencv2/opencv.hpp>
#include "../network/api_client.hpp"

void drawOverlay(cv::Mat& frame, const DetectionResponse& response);

class Overlay {
public:
    static void draw(
        cv::Mat& frame,
        double fps,
        double ramMB,
        const std::string& backendStatus
    );
};

