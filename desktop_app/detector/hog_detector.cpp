#include "hog_detector.h"
#include <opencv2/opencv.hpp>

using namespace cv;
using namespace std;

HogDetector::HogDetector() {

    //  Tamaño estándar para personas
    hog.winSize = Size(64, 128);

    //  Detector de personas preentrenado OpenCV
    hog.setSVMDetector(HOGDescriptor::getDefaultPeopleDetector());
}

vector<Rect> HogDetector::detect(Mat& frame){

    vector<Rect> boxes;

    Mat img;

    //  Reducir imagen mejora detección y velocidad
    resize(frame, img, Size(), 0.5, 0.5);

    hog.detectMultiScale(
        img,
        boxes,
        0,
        Size(8,8),
        Size(32,32),
        1.05,
        2
    );

    //  Escalar de vuelta a tamaño original
    for(auto &r : boxes){
        r.x *= 2;
        r.y *= 2;
        r.width *= 2;
        r.height *= 2;
    }

    return boxes;
}
