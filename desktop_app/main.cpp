#include <opencv2/opencv.hpp>
#include <iostream>
#include <chrono>

#include "detector/hog_detector.h"
#include "utils/metrics.h"
#include "sender/rest_client.h"

using namespace cv;
using namespace std;
using namespace std::chrono;

int main() {

    VideoCapture cap(0);

    if(!cap.isOpened()){
        cout << " No se pudo abrir la camara\n";
        return -1;
    }

    HogDetector detector;

    int width  = (int)cap.get(CAP_PROP_FRAME_WIDTH);
    int height = (int)cap.get(CAP_PROP_FRAME_HEIGHT);

    // ------------ Grabacion evidencia -------------
    bool recording = false;
    VideoWriter writer;
    int frame_record = 0;
    int max_frames = 150;   // ~5 segundos a 30 FPS

    // ------------ Control anti-spam -------------
    auto last_send = steady_clock::now();
    int cooldown_sec = 10;

    Mat frame;

    while(true){

        cap >> frame;
        if(frame.empty()) break;

        // -------- DETECCION --------
        vector<Rect> boxes = detector.detect(frame);

        // -------- METRICAS --------
        double fps = getFPS();
        double mem = getMemoryUsageMB();

        // -------- DIBUJAR BOXES --------
        for(auto& r : boxes)
            rectangle(frame, r, Scalar(0,255,0), 2);

        // -------- OVERLAY TEXTO --------
        putText(frame,
                "FPS: " + to_string((int)fps),
                Point(20,40),
                FONT_HERSHEY_SIMPLEX,
                1,
                Scalar(0,255,0),
                2);

        putText(frame,
                "Personas: " + to_string(boxes.size()),
                Point(20,80),
                FONT_HERSHEY_SIMPLEX,
                1,
                Scalar(0,255,0),
                2);

        putText(frame,
                "RAM: " + to_string((int)mem) + " MB",
                Point(20,120),
                FONT_HERSHEY_SIMPLEX,
                1,
                Scalar(0,255,0),
                2);

        // -------- DETECCION POSITIVA --------
        bool detected = !boxes.empty();

        auto now = steady_clock::now();
        int seconds_since_last =
            duration_cast<seconds>(now - last_send).count();

        if(detected && !recording && seconds_since_last > cooldown_sec){

            cout << " Persona detectada - guardando evidencia\n";

            imwrite("deteccion.png", frame);

            writer.open(
                "deteccion_video.mp4",
                VideoWriter::fourcc('m','p','4','v'),
                30,
                Size(width, height)
            );

            recording = true;
            frame_record = 0;

            last_send = now;
        }

        // -------- GRABAR VIDEO --------
        if(recording){

            writer.write(frame);
            frame_record++;

            if(frame_record >= max_frames){

                writer.release();
                recording = false;

                // -------- CONFIANZA SIMULADA --------
                double confidence = 1.0;

                cout << " Enviando evidencia al bot...\n";

                sendToBot(
                    "deteccion.png",
                    "deteccion_video.mp4",
                    fps,
                    confidence
                );
            }
        }

        // -------- MOSTRAR --------
        imshow("Desktop App - Vision", frame);

        if(waitKey(1) == 27) break;   // ESC
    }

    cap.release();
    destroyAllWindows();

    return 0;
}
