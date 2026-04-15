import numpy as np

def apply_adversarial_noise(image_data, epsilon=0.03):
    """Inyecta ruido adversarial (Fast Gradient Sign Method sim) para testear KEL."""
    noise = np.random.sign(np.random.normal(size=image_data.shape)) * epsilon
    return image_data + noise

def simulate_spoofed_command(audio_buffer):
    """Inserta comandos de voz falsificados en el buffer de audio."""
    pass
