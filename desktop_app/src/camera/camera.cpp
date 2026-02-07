#include "camera.hpp"

Camera::Camera(int index) {
    cap.open(index);
}

bool Camera::isOpened() const {
    return cap.isOpened();
}

cv::Mat Camera::getFrame() {
    cv::Mat frame;
    cap >> frame;
    return frame;
}

void Camera::release() {
    if (cap.isOpened()) {
        cap.release();
    }
}
