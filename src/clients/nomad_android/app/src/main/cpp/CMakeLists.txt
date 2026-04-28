cmake_minimum_required(VERSION 3.22.1)
project("nomad_llama")

set(CMAKE_CXX_STANDARD 17)
set(LLAMA_DIR ${CMAKE_CURRENT_SOURCE_DIR}/llama_cpp)

# Minimal sources for inference
add_library(nomad_llama SHARED
        llama-jni.cpp
        ${LLAMA_DIR}/ggml.c
        ${LLAMA_DIR}/ggml-alloc.c
        ${LLAMA_DIR}/ggml-backend.c
        ${LLAMA_DIR}/ggml-quants.c
        ${LLAMA_DIR}/llama.cpp
)

target_include_directories(nomad_llama PRIVATE ${LLAMA_DIR})

find_library(log-lib log)
target_link_libraries(nomad_llama ${log-lib})
