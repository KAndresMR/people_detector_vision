#include "metrics.hpp"
#include <sys/resource.h>

FPSCounter::FPSCounter()
    : frameCount(0), fps(0.0),
      lastTime(std::chrono::high_resolution_clock::now()) {}

void FPSCounter::tick() {
    frameCount++;
    auto now = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> elapsed = now - lastTime;

    if (elapsed.count() >= 1.0) {
        fps = frameCount / elapsed.count();
        frameCount = 0;
        lastTime = now;
    }
}

double FPSCounter::getFPS() const {
    return fps;
}

double getMemoryUsageMB() {
    struct rusage usage;
    getrusage(RUSAGE_SELF, &usage);

    // macOS devuelve KB
    return usage.ru_maxrss / 1024.0;
}
