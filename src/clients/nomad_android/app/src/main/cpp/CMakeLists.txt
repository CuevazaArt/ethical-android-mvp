cmake_minimum_required(VERSION 3.22.1)
project("nomad_llama")

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)

# Add your native library
add_library(nomad_llama SHARED
        llama-jni.cpp)

# Locate Android logging library
find_library(log-lib log)

# Link your native library with the logging library
target_link_libraries(nomad_llama
        ${log-lib})
