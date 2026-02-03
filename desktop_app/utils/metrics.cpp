#include "metrics.h"
#include <chrono>
#include <fstream>

double getFPS() {
    static auto last = std::chrono::high_resolution_clock::now();
    auto now = std::chrono::high_resolution_clock::now();

    double fps = 1.0 / std::chrono::duration<double>(now - last).count();
    last = now;

    return fps;
}

double getMemoryUsageMB() {
    std::ifstream file("/proc/self/statm");
    long rss;
    file >> rss >> rss;
    return rss * 4.0 / 1024.0;
}
