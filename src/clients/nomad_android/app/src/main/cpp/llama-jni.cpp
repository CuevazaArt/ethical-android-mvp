#include <jni.h>
#include <string>
#include <android/log.h>

#define TAG "NomadLlamaJNI"
#define LOGD(...) __android_log_print(ANDROID_LOG_DEBUG, TAG, __VA_ARGS__)
#define LOGE(...) __android_log_print(ANDROID_LOG_ERROR, TAG, __VA_ARGS__)

extern "C" JNIEXPORT jstring JNICALL
Java_com_ethos_nomad_inference_LlamaInference_stringFromJNI(
        JNIEnv* env,
        jobject /* this */) {
    return env->NewStringUTF("Llama JNI Bridge Operational");
}

extern "C" JNIEXPORT jboolean JNICALL
Java_com_ethos_nomad_inference_LlamaInference_loadModel(
        JNIEnv* env,
        jobject /* this */,
        jstring modelPath) {
    const char* path = env->GetStringUTFChars(modelPath, nullptr);
    LOGD("Attempting to load model from: %s", path);
    
    // TODO: Real llama_init_from_file goes here
    
    env->ReleaseStringUTFChars(modelPath, path);
    return JNI_TRUE;
}

extern "C" JNIEXPORT jstring JNICALL
Java_com_ethos_nomad_inference_LlamaInference_generateResponse(
        JNIEnv* env,
        jobject /* this */,
        jstring prompt) {
    const char* p = env->GetStringUTFChars(prompt, nullptr);
    LOGD("Inference call with prompt: %s", p);

    // TODO: Real llama_decode / sampling goes here
    std::string mockResponse = "[MOCK] Ethos local: Entiendo perfectamente. Estoy procesando tu mensaje de forma local.";

    env->ReleaseStringUTFChars(prompt, p);
    return env->NewStringUTF(mockResponse.c_str());
}

extern "C" JNIEXPORT void JNICALL
Java_com_ethos_nomad_inference_LlamaInference_unloadModel(
        JNIEnv* env,
        jobject /* this */) {
    LOGD("Unloading model...");
    // TODO: Real llama_free goes here
}
