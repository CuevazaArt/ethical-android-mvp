// Copyright 2026 Juan Cuevaz / Mos Ex Machina
// Licensed under the Business Source License 1.1
#include <jni.h>
#include <string>
#include <android/log.h>
#include "llama.h"
#include <vector>

#define TAG "EthosNomad_JNI"
#define LOGI(...) __android_log_print(ANDROID_LOG_INFO, TAG, __VA_ARGS__)
#define LOGE(...) __android_log_print(ANDROID_LOG_ERROR, TAG, __VA_ARGS__)

static llama_model* model = nullptr;
static llama_context* ctx = nullptr;

extern "C"
JNIEXPORT jboolean JNICALL
Java_com_ethos_nomad_inference_LlamaInference_loadModel(JNIEnv *env, jobject thiz, jstring model_path) {
    if (model) return JNI_TRUE;

    const char *path = env->GetStringUTFChars(model_path, nullptr);
    LOGI("Loading SLM from: %s", path);

    llama_backend_init();

    auto m_params = llama_model_default_params();
    model = llama_load_model_from_file(path, m_params);
    env->ReleaseStringUTFChars(model_path, path);

    if (!model) {
        LOGE("CRITICAL: Failed to load SLM file");
        return JNI_FALSE;
    }

    auto c_params = llama_context_default_params();
    c_params.n_ctx = 2048;
    c_params.n_threads = 4; // Optimized for POCKET/NOMAD tier

    ctx = llama_new_context_with_model(model, c_params);
    if (!ctx) {
        LOGE("CRITICAL: Failed to create llama_context");
        llama_free_model(model);
        model = nullptr;
        return JNI_FALSE;
    }

    LOGI("SLM Local Engine Ready.");
    return JNI_TRUE;
}

extern "C"
JNIEXPORT jstring JNICALL
Java_com_ethos_nomad_inference_LlamaInference_generateResponse(JNIEnv *env, jobject thiz, jstring prompt) {
    if (!ctx) return env->NewStringUTF("Error: Engine not initialized");

    const char *prompt_str = env->GetStringUTFChars(prompt, nullptr);
    
    // 1. Tokenize
    std::vector<llama_token> tokens(strlen(prompt_str) + 8);
    int n_tokens = llama_tokenize(model, prompt_str, strlen(prompt_str), tokens.data(), tokens.size(), true, true);
    env->ReleaseStringUTFChars(prompt, prompt_str);

    if (n_tokens < 0) return env->NewStringUTF("Error: Tokenization overflow");

    // 2. Decode (Single batch for POC response)
    llama_batch batch = llama_batch_get_one(tokens.data(), n_tokens, 0, 0);
    if (llama_decode(ctx, batch) != 0) {
        return env->NewStringUTF("Error: SLM Decode failure");
    }

    // 3. Response Stub (Greedy sampling implementation pending in Phase 25)
    // For Fase 24b Gate, we just need to confirm the engine processed the tokens.
    std::string response = "[LOCAL SLM] Inferencia exitosa. Tokens procesados: " + std::to_string(n_tokens);
    return env->NewStringUTF(response.c_str());
}

extern "C"
JNIEXPORT void JNICALL
Java_com_ethos_nomad_inference_LlamaInference_unloadModel(JNIEnv *env, jobject thiz) {
    if (ctx) {
        llama_free(ctx);
        ctx = nullptr;
    }
    if (model) {
        llama_free_model(model);
        model = nullptr;
    }
    llama_backend_free();
    LOGI("SLM Local Engine Offline.");
}
