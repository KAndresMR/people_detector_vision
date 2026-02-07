#ifndef API_CLIENT_HPP
#define API_CLIENT_HPP

#include <string>
#include <vector>
#include <opencv2/opencv.hpp>

// ========== ESTRUCTURA DE DETECCIÓN ==========
struct Detection {
    bool person_detected;
    double confidence;
    cv::Rect bbox;
    
    Detection() : person_detected(false), confidence(0.0), bbox(0, 0, 0, 0) {}
};

// ========== RESPUESTA DEL BACKEND ==========
struct DetectionResponse {
    bool alert_sent;
    std::string backend_status;
    std::vector<Detection> detections;
    
    DetectionResponse() : alert_sent(false), backend_status("OFFLINE") {}
};

// ========== CLIENTE API ==========
class ApiClient {
public:
    ApiClient(const std::string& endpoint);
    
    // Enviar frame al backend y obtener detecciones
    DetectionResponse sendFrame(const cv::Mat& frame);
    
    // Verificar conexión con el backend
    bool testConnection();
    
private:
    std::string api_url;
};

#endif // API_CLIENT_HPP
