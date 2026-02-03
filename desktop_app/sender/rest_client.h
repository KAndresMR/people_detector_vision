#pragma once
#include <string>

void sendToBot(const std::string& imagePath,
               const std::string& videoPath,
               double fps,
               double confidence);
