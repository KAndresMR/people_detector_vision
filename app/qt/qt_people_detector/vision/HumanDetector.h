#ifndef HUMAN_DETECTOR_H
#define HUMAN_DETECTOR_H

#include <opencv2/opencv.hpp>
#include <vector>

class HumanDetector
{
public:
    HumanDetector();
    ~HumanDetector();

    // Carga del modelo entrenado (HOG + SVM)
    bool loadModel(const std::string& modelPath);

    // Ejecuta detección sobre un frame
    std::vector<cv::Rect> detect(const cv::Mat& frame);

    bool isLoaded() const;

private:
    cv::HOGDescriptor hog;
    bool modelLoaded = false;
};

#endif // HUMAN_DETECTOR_H