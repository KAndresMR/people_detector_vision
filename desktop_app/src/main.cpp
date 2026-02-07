#include <opencv2/opencv.hpp>
#include <iostream>
#include <chrono>
#include "camera/camera.hpp"
#include "metrics/metrics.hpp"
#include "network/api_client.hpp"
#include "ui/overlay.hpp"

using namespace std::chrono;

int main() {
    std::cout << "=========================================\n";
    std::cout << "  People Detector Desktop App\n";
    std::cout << "=========================================\n\n";
    
    // ========== INICIALIZAR CÁMARA ==========
    std::cout << "[INFO] Abriendo cámara...\n";
    Camera camera(0);
    
    if (!camera.isOpened()) {
        std::cerr << "[ERROR] No se pudo abrir la cámara\n";
        std::cerr << "Verifica que tu webcam esté conectada.\n";
        return -1;
    }
    
    std::cout << "[INFO] ✓ Cámara abierta\n\n";
    
    // ========== INICIALIZAR API CLIENT ==========
    std::cout << "[INFO] Inicializando cliente API...\n";
    ApiClient api("http://127.0.0.1:5001/api/v1/detect");
    
    // Verificar conexión con backend
    if (!api.testConnection()) {
        std::cerr << "[WARNING] Backend no accesible\n";
        std::cerr << "El programa continuará, pero no enviará detecciones.\n";
        std::cerr << "Asegúrate de iniciar el backend:\n";
        std::cerr << "  cd backend && python app.py\n\n";
    }
    
    // ========== INICIALIZAR MÉTRICAS ==========
    FPSCounter fpsCounter;
    
    // ========== CONFIGURACIÓN DE ENVÍO ==========
    const int COOLDOWN_SECONDS = 10;  // Cooldown entre envíos
    auto last_send_time = steady_clock::now();
    int total_sends = 0;
    
    std::cout << "[INFO] Configuración:\n";
    std::cout << "  - Cooldown entre envíos: " << COOLDOWN_SECONDS << "s\n";
    std::cout << "  - Backend: http://127.0.0.1:5001\n\n";
    
    std::cout << "[INFO] Controles:\n";
    std::cout << "  - ESC o 'q': Salir\n";
    std::cout << "  - 't': Test de conexión con backend\n\n";
    
    std::cout << "[INFO] Iniciando detección...\n\n";
    
    // ========== VARIABLES DE ESTADO ==========
    cv::Mat frame;
    DetectionResponse last_response;  // Última respuesta del backend
    
    // ========== LOOP PRINCIPAL ==========
    while (true) {
        // Actualizar FPS
        fpsCounter.tick();
        
        // Capturar frame
        frame = camera.getFrame();
        
        if (frame.empty()) {
            std::cerr << "[WARNING] Frame vacío, continuando...\n";
            continue;
        }
        
        // ========== ENVÍO AL BACKEND CON COOLDOWN ==========
        auto now = steady_clock::now();
        auto seconds_since_last = duration_cast<seconds>(now - last_send_time).count();
        
        bool should_send = (seconds_since_last >= COOLDOWN_SECONDS);
        
        if (should_send) {
            std::cout << "[SEND] Enviando frame al backend...\n";
            
            // Enviar frame y obtener detecciones
            DetectionResponse response = api.sendFrame(frame);
            
            if (!response.detections.empty()) {
                last_response = response;
                last_send_time = now;
                total_sends++;
                
                std::cout << "[SEND] ✓ Respuesta recibida\n";
                std::cout << "       Detecciones: " << response.detections.size() << "\n";
                std::cout << "       Status: " << response.backend_status << "\n";
                std::cout << "       Total envíos: " << total_sends << "\n\n";
            } else {
                // Si no hay detecciones, actualizar el estado del backend
                if (response.backend_status != "OFFLINE") {
                    last_response.backend_status = response.backend_status;
                }
            }
        }
        
        // ========== DIBUJAR OVERLAY ==========
        // Bounding boxes y detecciones de la última respuesta
        drawOverlay(frame, last_response);
        
        // ========== MÉTRICAS LOCALES ==========
        double fps = fpsCounter.getFPS();
        double ram = getMemoryUsageMB();
        
        // ========== UI OVERLAY CON MÉTRICAS ==========
        std::string backendStatus = last_response.backend_status;
        Overlay::draw(frame, fps, ram, backendStatus);
        
        // Mostrar cooldown restante si está activo
        int cooldown_remaining = COOLDOWN_SECONDS - seconds_since_last;
        if (cooldown_remaining > 0) {
            std::string cooldown_text = "Cooldown: " + std::to_string(cooldown_remaining) + "s";
            cv::putText(frame, cooldown_text, 
                       cv::Point(20, frame.rows - 20),
                       cv::FONT_HERSHEY_SIMPLEX, 0.6,
                       cv::Scalar(255, 255, 0), 2);
        }
        
        // ========== MOSTRAR FRAME ==========
        cv::imshow("People Detector", frame);
        
        // ========== CAPTURAR TECLAS ==========
        char key = static_cast<char>(cv::waitKey(1));
        
        if (key == 27 || key == 'q') {  // ESC o 'q' para salir
            std::cout << "\n[INFO] Saliendo...\n";
            break;
        } else if (key == 't' || key == 'T') {  // Test de conexión
            std::cout << "\n[TEST] Verificando conexión...\n";
            api.testConnection();
            std::cout << "\n";
        }
    }
    
    // ========== CLEANUP ==========
    camera.release();
    cv::destroyAllWindows();
    
    // ========== ESTADÍSTICAS FINALES ==========
    std::cout << "\n=========================================\n";
    std::cout << "  Estadísticas de la sesión\n";
    std::cout << "=========================================\n";
    std::cout << "  Total de envíos al backend: " << total_sends << "\n";
    std::cout << "=========================================\n\n";
    
    return 0;
}
