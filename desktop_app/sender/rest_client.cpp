#include "rest_client.h"
#include <curl/curl.h>
#include <iostream>
#include <ctime>

void sendToBot(const std::string& imagePath,
               const std::string& videoPath,
               double fps,
               double confidence) {

    CURL* curl = curl_easy_init();

    if (!curl) {
        std::cerr << "No se pudo inicializar CURL\n";
        return;
    }

    curl_mime* form = curl_mime_init(curl);
    curl_mimepart* part;

    // ---------- IMAGEN ----------
    part = curl_mime_addpart(form);
    curl_mime_name(part, "image");
    curl_mime_filedata(part, imagePath.c_str());

    // ---------- VIDEO ----------
    part = curl_mime_addpart(form);
    curl_mime_name(part, "video");
    curl_mime_filedata(part, videoPath.c_str());

    // ---------- FPS ----------
    part = curl_mime_addpart(form);
    curl_mime_name(part, "fps");
    curl_mime_data(
        part,
        std::to_string(fps).c_str(),
        CURL_ZERO_TERMINATED
    );

    // ---------- TIMESTAMP ----------
    std::time_t now = std::time(nullptr);

    part = curl_mime_addpart(form);
    curl_mime_name(part, "timestamp");
    curl_mime_data(
        part,
        std::to_string(now).c_str(),
        CURL_ZERO_TERMINATED
    );

    // ---------- CONFIANZA ----------
    part = curl_mime_addpart(form);
    curl_mime_name(part, "confidence");
    curl_mime_data(
        part,
        std::to_string(confidence).c_str(),
        CURL_ZERO_TERMINATED
    );

    // ---------- URL CORRECTA ----------
    curl_easy_setopt(
        curl,
        CURLOPT_URL,
        "http://127.0.0.1:5000/upload"
    );

    curl_easy_setopt(curl, CURLOPT_MIMEPOST, form);
    curl_easy_setopt(curl, CURLOPT_TIMEOUT, 30L);

    CURLcode res = curl_easy_perform(curl);

    if (res != CURLE_OK) {
        std::cerr << "❌ Error HTTP: "
                  << curl_easy_strerror(res)
                  << std::endl;
    } else {
        long response_code;
        curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, &response_code);

        if(response_code == 200)
            std::cout << " Evidencia enviada al bot correctamente\n";
        else
            std::cout << " Respuesta HTTP: " << response_code << "\n";
    }

    curl_mime_free(form);
    curl_easy_cleanup(curl);
}
