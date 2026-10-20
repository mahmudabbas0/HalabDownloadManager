cmake_minimum_required(VERSION 3.21)
project(HalabDownloadManager VERSION 1.0.3 LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_AUTOMOC ON)
find_package(Qt6 REQUIRED COMPONENTS Widgets Network)
qt_add_executable(HalabDownloadManager WIN32 main.cpp)
target_link_libraries(HalabDownloadManager PRIVATE Qt6::Widgets Qt6::Network)

qt_add_resources(HalabDownloadManager "translations" PREFIX "/i18n" FILES languages.json)

qt_add_executable(HalabNativeHost native_host.cpp)
target_link_libraries(HalabNativeHost PRIVATE Qt6::Core Qt6::Network)

if(WIN32 AND MINGW)
  get_filename_component(MINGW_BIN "${CMAKE_CXX_COMPILER}" DIRECTORY)
  add_custom_command(OUTPUT "${CMAKE_CURRENT_BINARY_DIR}/halab-icon.o"
    COMMAND "${MINGW_BIN}/windres.exe" --use-temp-file -i halab.rc -o "${CMAKE_CURRENT_BINARY_DIR}/halab-icon.o"
    WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}"
    DEPENDS halab.rc halab.ico VERBATIM)
  target_sources(HalabDownloadManager PRIVATE "${CMAKE_CURRENT_BINARY_DIR}/halab-icon.o")
elseif(WIN32)
  target_sources(HalabDownloadManager PRIVATE halab.rc)
endif()
