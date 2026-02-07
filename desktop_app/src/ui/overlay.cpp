#include "overlay.hpp"

void drawOverlay(cv::Mat& frame, const DetectionResponse& response) {
    for (const auto& det : response.detections) {
        cv::rectangle(frame, det.bbox, cv::Scalar(0, 255, 0), 2);

        std::string label = "Person: " + std::to_string(det.confidence);
        cv::putText(frame, label,
                    cv::Point(det.bbox.x, det.bbox.y - 10),
                    cv::FONT_HERSHEY_SIMPLEX,
                    0.5, cv::Scalar(0, 255, 0), 2);
    }

    if (response.alert_sent) {
        cv::putText(frame, "ALERTA ENVIADA",
                    cv::Point(20, 40),
                    cv::FONT_HERSHEY_SIMPLEX,
                    1.0, cv::Scalar(0, 0, 255), 3);
    }
}

void Overlay::draw(
    cv::Mat& frame,
    double fps,
    double ramMB,
    const std::string& backendStatus
) {
    int x = 10;
    int y = 30;
    int lineHeight = 25;

    cv::Scalar textColor(0, 255, 0);
    cv::Scalar shadowColor(0, 0, 0);
    double fontScale = 0.6;
    int thickness = 1;

    auto drawText = [&](const std::string& text, int posY) {
        cv::putText(frame, text, {x + 1, posY + 1},
                    cv::FONT_HERSHEY_SIMPLEX, fontScale, shadowColor, 2);
        cv::putText(frame, text, {x, posY},
                    cv::FONT_HERSHEY_SIMPLEX, fontScale, textColor, thickness);
    };

    drawText("FPS: " + std::to_string(static_cast<int>(fps)), y);
    drawText("RAM: " + std::to_string(static_cast<int>(ramMB)) + " MB", y + lineHeight);
    drawText("Backend: " + backendStatus, y + 2 * lineHeight);
}