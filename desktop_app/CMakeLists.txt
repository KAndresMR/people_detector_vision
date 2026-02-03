cmake_minimum_required(VERSION 3.10)
project(desktop_app)

set(CMAKE_CXX_STANDARD 17)

find_package(OpenCV REQUIRED)
find_package(CURL REQUIRED)

include_directories(
    ${OpenCV_INCLUDE_DIRS}
    detector
    sender
    utils
)

add_executable(app
    main.cpp
    detector/hog_detector.cpp
    sender/rest_client.cpp
    utils/metrics.cpp
)

target_link_libraries(app
    ${OpenCV_LIBS}
    CURL::libcurl
)
