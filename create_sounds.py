import numpy as np
from scipy.io import wavfile

def create_tone(freq, duration, sample_rate=44100):
    """Create a simple tone at the given frequency"""
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    tone = 0.5 * np.sin(2 * np.pi * freq * t)
    return tone

def create_drum_sound(duration=0.5, sample_rate=44100):
    """Create a simple drum sound"""
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    # Create a percussive sound with fast decay
    drum = np.random.uniform(-0.5, 0.5, int(sample_rate * duration))
    envelope = np.exp(-5 * t)
    return drum * envelope

def create_cymbal_sound(duration=1.0, sample_rate=44100):
    """Create a cymbal-like sound"""
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    # Mix of high frequencies with noise
    cymbal = np.zeros_like(t)
    for freq in [3000, 4500, 6000, 7500]:
        cymbal += 0.1 * np.sin(2 * np.pi * freq * t)
    noise = np.random.uniform(-0.3, 0.3, int(sample_rate * duration))
    envelope = np.exp(-3 * t)
    return (cymbal + noise) * envelope

def create_guitar_strum(duration=1.0, sample_rate=44100):
    """Create a guitar strum sound"""
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    # Mix of frequencies for a chord
    guitar = np.zeros_like(t)
    for freq in [196, 247, 294, 370, 440]:
        guitar += 0.15 * np.sin(2 * np.pi * freq * t)
    envelope = np.exp(-2 * t)
    return guitar * envelope

def create_bass_sound(duration=1.0, sample_rate=44100):
    """Create a bass sound"""
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    # Low frequency tone
    bass = 0.7 * np.sin(2 * np.pi * 60 * t) + 0.3 * np.sin(2 * np.pi * 120 * t)
    envelope = np.exp(-1 * t)
    return bass * envelope

def create_chorus_sound(duration=3.0, sample_rate=44100):
    """Create a chorus sound (multiple voices)"""
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    # Mix of frequencies with slight variations for chorus effect
    chorus = np.zeros_like(t)
    for freq in [261.63, 329.63, 392.00]:  # C4, E4, G4 (C major chord)
        chorus += 0.2 * np.sin(2 * np.pi * freq * t)
        chorus += 0.1 * np.sin(2 * np.pi * (freq+2) * t)  # Slight detuning
        chorus += 0.1 * np.sin(2 * np.pi * (freq-2) * t)  # Slight detuning
    envelope = np.ones_like(t)
    envelope[-int(sample_rate*0.5):] = np.linspace(1, 0, int(sample_rate*0.5))
    return chorus * envelope

def save_wav(data, filename, sample_rate=44100):
    """Save audio data as WAV file"""
    # Normalize to prevent clipping
    normalized = data / np.max(np.abs(data)) * 0.9
    # Convert to 16-bit PCM
    audio_data = (normalized * 32767).astype(np.int16)
    wavfile.write(filename, sample_rate, audio_data)

def main():
    """Create all sound files"""
    # Create and save drum sound
    drum = create_drum_sound()
    save_wav(drum, "drum.wav")
    
    # Create and save bass sound
    bass = create_bass_sound()
    save_wav(bass, "bass.wav")
    
    # Create and save guitar strum sound
    guitar = create_guitar_strum()
    save_wav(guitar, "guitar.wav")
    
    # Create and save cymbal sound
    cymbal = create_cymbal_sound()
    save_wav(cymbal, "cymbal.wav")
    
    # Create and save chorus sound
    chorus = create_chorus_sound()
    save_wav(chorus, "chorus.wav")
    
    print("All sound files created successfully!")

if __name__ == "__main__":
    main()