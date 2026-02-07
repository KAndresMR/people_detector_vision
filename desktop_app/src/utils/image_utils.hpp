#ifndef IMAGE_UTILS_HPP
#define IMAGE_UTILS_HPP

#include <string>
#include <opencv2/core.hpp>

// Codifica una imagen cv::Mat a base64 (formato JPEG)
std::string encodeImageBase64(const cv::Mat& image);

#endif // IMAGE_UTILS_HPP
