#include "HumanDetector.h"

HumanDetector::HumanDetector()
{
    hog = cv::HOGDescriptor();
    hog.setSVMDetector(cv::HOGDescriptor::getDefaultPeopleDetector());
    modelLoaded = true;
}

HumanDetector::~HumanDetector() {}

bool HumanDetector::loadModel(const std::string& modelPath)
{
    // 🔴 AÚN NO IMPLEMENTADO
    // Aquí luego irá hog.setSVMDetector(...)
    // modelLoaded = false;
    return modelLoaded;
}

std::vector<cv::Rect> HumanDetector::detect(const cv::Mat& frame)
{
    std::vector<cv::Rect> detections;

    if (!modelLoaded || frame.empty())
        return detections;

    hog.detectMultiScale(
        frame,
        detections,
        0,              // hitThreshold
        cv::Size(8,8),  // winStride
        cv::Size(32,32),// padding
        1.07,           // scale
        3               // groupThreshold
        );

    return detections;
}

bool HumanDetector::isLoaded() const
{
    return modelLoaded;
}
