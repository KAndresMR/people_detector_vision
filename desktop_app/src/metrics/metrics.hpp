#pragma once
#include <chrono>

class FPSCounter {
public:
    FPSCounter();

    void tick();
    double getFPS() const;

private:
    int frameCount;
    double fps;
    std::chrono::time_point<std::chrono::high_resolution_clock> lastTime;
};

double getMemoryUsageMB();
