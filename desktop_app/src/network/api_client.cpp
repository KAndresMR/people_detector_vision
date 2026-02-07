#include "api_client.hpp"
#include "../utils/image_utils.hpp"
#include <curl/curl.h>
#include <nlohmann/json.hpp>
#include <iostream>

using json = nlohmann::json;

// ========== CALLBACK PARA CAPTURAR RESPUESTA ==========
static size_t WriteCallback(void* contents, size_t size, size_t nmemb, void* userp) {
    ((std::string*)userp)->append((char*)contents, size * nmemb);
    return size * nmemb;
}

// ========== CONSTRUCTOR ==========
ApiClient::ApiClient(const std::string& endpoint)
    : api_url(endpoint) {
    std::cout << "[API] Cliente inicializado: " << api_url << "\n";
}

// ========== ENVIAR FRAME AL BACKEND ==========
DetectionResponse ApiClient::sendFrame(const cv::Mat& frame) {
    DetectionResponse result;
    result.alert_sent = false;
    result.backend_status = "OFFLINE";
    
    // Validar frame
    if (frame.empty()) {
        std::cerr << "[API] Frame vacío, no se envía\n";
        return result;
    }
    
    // Codificar imagen a base64
    std::string encoded;
    try {
        encoded = encodeImageBase64(frame);
    } catch (const std::exception& e) {
        std::cerr << "[API] Error al codificar imagen: " << e.what() << "\n";
        return result;
    }
    
    // Crear payload JSON
    json payload;
    try {
        payload["source"] = "desktop_app";
        payload["image"]["encoded"] = true;
        payload["image"]["format"] = "jpg";
        payload["image"]["data"] = encoded;
    } catch (const std::exception& e) {
        std::cerr << "[API] Error al crear JSON: " << e.what() << "\n";
        return result;
    }
    
    // Inicializar CURL
    CURL* curl = curl_easy_init();
    if (!curl) {
        std::cerr << "[API] Error: No se pudo inicializar CURL\n";
        return result;
    }
    
    std::string response_string;
    struct curl_slist* headers = nullptr;
    
    // Configurar headers
    headers = curl_slist_append(headers, "Content-Type: application/json");
    
    // Convertir payload a string
    std::string payload_str = payload.dump();
    
    // Configurar CURL
    curl_easy_setopt(curl, CURLOPT_URL, api_url.c_str());
    curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);
    curl_easy_setopt(curl, CURLOPT_POSTFIELDS, payload_str.c_str());
    curl_easy_setopt(curl, CURLOPT_POSTFIELDSIZE, payload_str.length());
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteCallback);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, &response_string);
    
    // Timeouts
    curl_easy_setopt(curl, CURLOPT_TIMEOUT, 10L);         // 10 segundos total
    curl_easy_setopt(curl, CURLOPT_CONNECTTIMEOUT, 5L);   // 5 segundos para conectar
    
    // Ejecutar request
    CURLcode res = curl_easy_perform(curl);
    
    // Obtener código de respuesta HTTP
    long http_code = 0;
    curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, &http_code);
    
    // ⚠️ IMPORTANTE: Liberar headers y curl
    curl_slist_free_all(headers);
    curl_easy_cleanup(curl);
    
    // Evaluar respuesta
    if (res != CURLE_OK) {
        std::cerr << "[API] Error en request: " << curl_easy_strerror(res) << "\n";
        return result;
    }
    
    if (http_code != 200) {
        std::cerr << "[API] Código HTTP no exitoso: " << http_code << "\n";
        std::cerr << "[API] Respuesta: " << response_string << "\n";
        return result;
    }
    
    // Parsear respuesta JSON
    try {
        auto resp = json::parse(response_string);
        
        // Obtener campos básicos con valores por defecto
        result.alert_sent = resp.value("alert_sent", false);
        result.backend_status = resp.value("backend_status", "UNKNOWN");
        
        // Parsear detecciones
        if (resp.contains("detections") && resp["detections"].is_array()) {
            for (const auto& det : resp["detections"]) {
                Detection d;
                d.person_detected = det.value("person_detected", true);
                d.confidence = det.value("confidence", 0.0);
                
                // Parsear bbox con validación
                if (det.contains("bbox") && det["bbox"].is_array()) {
                    auto bb = det["bbox"];
                    
                    // Verificar que tenga 4 elementos
                    if (bb.size() >= 4) {
                        int x = bb[0].get<int>();
                        int y = bb[1].get<int>();
                        int w = bb[2].get<int>();
                        int h = bb[3].get<int>();
                        
                        // Validar valores positivos
                        if (x >= 0 && y >= 0 && w > 0 && h > 0) {
                            d.bbox = cv::Rect(x, y, w, h);
                            result.detections.push_back(d);
                        } else {
                            std::cerr << "[API] Bbox con valores inválidos, ignorando\n";
                        }
                    } else {
                        std::cerr << "[API] Bbox no tiene 4 elementos, ignorando\n";
                    }
                } else {
                    std::cerr << "[API] Detección sin bbox válido\n";
                }
            }
        }
        
        std::cout << "[API] Respuesta OK - " << result.detections.size() 
                  << " detecciones - Status: " << result.backend_status << "\n";
        
    } catch (const json::parse_error& e) {
        std::cerr << "[API] Error al parsear JSON: " << e.what() << "\n";
        std::cerr << "[API] Respuesta raw: " << response_string << "\n";
    } catch (const std::exception& e) {
        std::cerr << "[API] Error inesperado: " << e.what() << "\n";
    }
    
    return result;
}

// ========== VERIFICAR CONEXIÓN CON BACKEND ==========
bool ApiClient::testConnection() {
    std::cout << "[API] Probando conexión con: " << api_url << "\n";
    
    CURL* curl = curl_easy_init();
    if (!curl) {
        return false;
    }
    
    // Solo hacer HEAD request para verificar
    curl_easy_setopt(curl, CURLOPT_URL, api_url.c_str());
    curl_easy_setopt(curl, CURLOPT_NOBODY, 1L);  // Solo headers
    curl_easy_setopt(curl, CURLOPT_TIMEOUT, 5L);
    
    CURLcode res = curl_easy_perform(curl);
    
    long http_code = 0;
    curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, &http_code);
    
    curl_easy_cleanup(curl);
    
    if (res == CURLE_OK && http_code != 0) {
        std::cout << "[API] ✓ Backend accesible (HTTP " << http_code << ")\n";
        return true;
    } else {
        std::cout << "[API] ✗ Backend no accesible\n";
        return false;
    }
}
