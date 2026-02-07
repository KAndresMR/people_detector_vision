cmake_minimum_required(VERSION 3.10)
project(PeopleDetector)

# Configuración de C++
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Encontrar OpenCV
find_package(OpenCV REQUIRED)
if(OpenCV_FOUND)
    message(STATUS "OpenCV found: ${OpenCV_VERSION}")
    message(STATUS "OpenCV include dirs: ${OpenCV_INCLUDE_DIRS}")
else()
    message(FATAL_ERROR "OpenCV not found!")
endif()

# Encontrar CURL (para enviar a Telegram API)
find_package(CURL REQUIRED)
if(CURL_FOUND)
    message(STATUS "CURL found: ${CURL_VERSION_STRING}")
else()
    message(FATAL_ERROR "CURL not found!")
endif()

find_package(nlohmann_json REQUIRED)
message(STATUS "nlohmann_json found")

find_package(OpenSSL REQUIRED)
message(STATUS "OpenSSL found")




# Directorios de includes
include_directories(
    ${OpenCV_INCLUDE_DIRS}
    ${CURL_INCLUDE_DIRS}
    ${CMAKE_SOURCE_DIR}/src
)

# Recopilar todos los archivos fuente
file(GLOB_RECURSE SOURCES
    "src/*.cpp"
    "src/**/*.cpp"
)

# Crear ejecutable
add_executable(app ${SOURCES})

# Linkear librerías
target_link_libraries(app
    PRIVATE
        ${OpenCV_LIBS}
        ${CURL_LIBRARIES}
        nlohmann_json::nlohmann_json
        OpenSSL::Crypto
)

# Configuración de instalación
install(TARGETS app DESTINATION bin)

# Mensaje de configuración
message(STATUS "===========================================")
message(STATUS "Project: ${PROJECT_NAME}")
message(STATUS "Build type: ${CMAKE_BUILD_TYPE}")
message(STATUS "C++ Standard: ${CMAKE_CXX_STANDARD}")
message(STATUS "OpenCV version: ${OpenCV_VERSION}")
message(STATUS "Source files found: ${SOURCES}")
message(STATUS "===========================================")
