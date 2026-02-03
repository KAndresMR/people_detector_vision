#ifndef HOG_DETECTOR_H
#define HOG_DETECTOR_H

#include <opencv2/opencv.hpp>
#include <vector>

class HogDetector {

public:
    HogDetector();
    std::vector<cv::Rect> detect(cv::Mat& frame);

private:
    cv::HOGDescriptor hog;
};

#endif
