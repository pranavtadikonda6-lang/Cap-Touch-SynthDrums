import ulab.numpy as np
import random
import synthio

# Base sample buffer size for waveform generation.
# This controls the length of every custom waveform table.
SAMPLE_SIZE = 200

# Two sine-wave tables with different phase offsets for tonal content.
# `np.linspace(start, stop, num, endpoint=False)` generates evenly spaced values from start to stop.
# `start` is the first angle in radians, `stop` is the end angle, `num` is SAMPLE_SIZE,
# and `endpoint=False` means the stop value is not included.
# `np.sin(...)` converts these angles to sine values, and multiplying by 32767 scales the waveform
# to the signed 16-bit audio range used by the synth.
# `sinwave1` starts at 0 radians.
# `sinwave2` starts at pi/2 radians, which changes the phase and gives a different tone when used.
sinwave1 = np.array(np.sin(np.linspace(0, 2*np.pi, SAMPLE_SIZE, endpoint=False)) * 32767, dtype=np.int16)
sinwave2 = np.array(np.sin(np.linspace(np.pi/2, 2.5*np.pi, SAMPLE_SIZE, endpoint=False)) * 32767, dtype=np.int16)

# A very short downward ramp used for pitch bend / drop effects.
# This wave is used by an LFO to make notes sweep downward quickly.
downwave = np.linspace(32767, -32767, num=3, dtype=np.int16)

# Noise table used for snare and hi-hat textures.
# Random values produce a percussive noise source rather than a musical tone.
noisewave_list = []
for i in range(SAMPLE_SIZE):
    noise_sample = random.randint(-32767, 32767)
    noisewave_list.append(noise_sample)
noisewave = np.array(noisewave_list, dtype=np.int16)

# Two combined waveforms mixing sine content with noise for richer drum tones.
# These are clipped to stay within signed 16-bit audio range.
# w1 combines sinwave1 with half of noisewave, keeping the result within the valid audio range.
w1_list = []
for i in range(SAMPLE_SIZE):
    mixed_value = sinwave1[i] + (noisewave[i] / 2.0)
    clipped_value = int(max(min(mixed_value, 32767), -32767))
    w1_list.append(clipped_value)
w1 = np.array(w1_list, dtype=np.int16)

# w2 combines sinwave2 with half of noisewave, creating a different harmonic blend.
w2_list = []
for i in range(SAMPLE_SIZE):
    mixed_value = sinwave2[i] + (noisewave[i] / 2.0)
    clipped_value = int(max(min(mixed_value, 32767), -32767))
    w2_list.append(clipped_value)
w2 = np.array(w2_list, dtype=np.int16)

# A square wave oscillates between maximum and minimum values.
# The first half of the waveform is at +32767 (maximum), the second half at -32767 (minimum).
# Square waves produce a hollow, bright tone often used in synthesizers and electronic music.
# The sharp transitions between high and low create harmonic-rich overtones.
squarewave_list = []
for i in range(SAMPLE_SIZE):
    if i < SAMPLE_SIZE // 2:
        squarewave_list.append(32767)
    else:
        squarewave_list.append(-32767)
squarewave = np.array(squarewave_list, dtype=np.int16)




class KickDrum:
    # A bass drum instrument using a low frequency sine wave with pitch bend effect.
    def __init__(self, synth):
        # `synth`: the synthio synthesizer instance used to play kick notes.
        # The synth is passed in from code.py so all drums share the same audio output.
        # This constructor creates internal note objects that are retained for reuse.
        self.synth = synth

    def play(self, synth=None):
        if synth is None:
            synth = self.synth

       
        # Create a fresh Low Frequency Oscillator (LFO) for pitch bend effect.
        # A new LFO is created each time to avoid interference with other drums.
        # The LFO uses the downwave waveform which is a quick downward ramp.
        # Pitch bend envelope: a short downward sweep for kick impact.
        lfo = synthio.LFO(waveform=downwave)
        lfo.once = True  # Apply the pitch bend only once per note trigger
        lfo.offset = 0.33  # Offset the starting point of the sweep
        lfo.scale = 0.3  # Scale how much the pitch bends down
        lfo.rate = 20  # Speed of the pitch bend sweep
        lfo.retrigger()  # Start the LFO sweep immediately

        # Create an amplitude envelope that controls how the kick decays over time.
        # attack_time=0.0: no fade-in, note starts at full volume instantly (percussive)
        # decay_time=0.075: the note fades from full volume to silent over 75ms
        # release_time=0: no additional fade after the decay
        # attack_level=1: peak volume (maximum)
        # sustain_level=0: target level to fade to (complete silence)
        amp_env = synthio.Envelope(attack_time=0.0, decay_time=0.075, release_time=0, attack_level=1, sustain_level=0)

        # Create the actual note: low frequency (53 Hz) with the envelope and pitch bend.
        # frequency=53 Hz: sub-bass frequency for a deep kick sound
        # waveform=sinwave2: a sine wave with phase offset for tonal coloring
        # bend=lfo: applies the pitch bend from the LFO
        note = synthio.Note(frequency=53, envelope=amp_env, waveform=sinwave2, bend=lfo)

        # Send the note to the synthesizer to play it immediately.
        synth.press((note,))

           
                  
class Snare:
    # A snare drum instrument using a noise-based waveform for a crisp, percussive hit.
    def __init__(self, synth):
        # Store the synthesizer instance for use when playing the snare.
        self.synth = synth

    def play(self, synth=None):
        # Play the snare drum sound.
        # Use the provided synth, or fall back to the stored instance.
        if synth is None:
            synth = self.synth

        # Create a fresh Low Frequency Oscillator (LFO) for pitch bend effect.
        # A new LFO is created each time to avoid interference with other drums.
        lfo = synthio.LFO(waveform=downwave)
        lfo.once = True  # Apply the pitch bend only once per note trigger
        lfo.offset = 0.33  # Offset the starting point of the sweep
        lfo.scale = 0.3  # Scale how much the pitch bends down
        lfo.rate = 20  # Speed of the pitch bend sweep
        lfo.retrigger()  # Start the LFO sweep immediately

        # Create an amplitude envelope for the snare's decay.
        # attack_time=0.0: instant onset for a sharp snare attack
        # decay_time=0.115: the note fades over 115ms (slightly longer than kick)
        amp_env = synthio.Envelope(attack_time=0.0, decay_time=0.115, release_time=0, attack_level=1, sustain_level=0)

        # Create the snare note using a mixed sine/noise waveform for natural tone.
        # frequency=90 Hz: mid-range frequency for the snare body
        # waveform=w1: mixed sine and noise waveform for crisp snare texture
        # bend=lfo: applies the pitch bend from the LFO
        note = synthio.Note(frequency=90, envelope=amp_env, waveform=w1, bend=lfo)

        # Send the note to the synthesizer to play it immediately.
        synth.press((note,))



class HighHat:
       # A hi-hat drum instrument using noise for a crisp, bright percussive sound.
       # The decay time can be adjusted to create different hi-hat textures (closed vs open).
       def __init__(self, synth, t=0.115):
           # Store the synthesizer instance for later use.
           self.synth = synth
           # Store the decay time parameter. Different values create different hi-hat sounds:
           # t=0.08 creates a tight, closed hi-hat sound
           # t=0.15 creates a longer, more open hi-hat sound
           self.t = t

       def play(self, synth=None):
           # Play the hi-hat by triggering a noise-based note.
           # Use the provided synth, or fall back to the stored instance.
           if synth is None:
               synth = self.synth

           # Create an amplitude envelope using the stored decay time (self.t).
           # attack_time=0.0: instant onset for a crisp attack
           # decay_time=self.t: the note fades over the configured time (0.08s or 0.15s)
           amp_env = synthio.Envelope(attack_time=0.0, decay_time=self.t, release_time=0, attack_level=1, sustain_level=0)

           # Create the hi-hat note using pure noise for a natural hi-hat texture.
           # frequency=90 Hz: the frequency is less important for noise-based sounds
           # waveform=noisewave: random noise samples create the percussive hi-hat tone
           note = synthio.Note(frequency=90, envelope=amp_env, waveform=noisewave)

           # Send the note to the synthesizer to play it immediately.
           synth.press((note,))

class Cowbell:
      # A cowbell instrument using a square wave for a metallic, bright tone.
      def __init__(self, synth):
          # Store the synthesizer instance for use when playing the cowbell.
          # The synth is passed in from code.py so all drums share the same audio output.
          self.synth = synth

      def play(self, synth=None):
          # Play the cowbell sound.
          # Use the provided synth, or fall back to the stored instance.
          if synth is None:
              synth = self.synth

          # Create a fresh Low Frequency Oscillator (LFO) for pitch bend effect.
          # A new LFO is created each time to avoid interference with other drums.
          # The LFO uses the downwave waveform which is a quick downward ramp.
          lfo = synthio.LFO(waveform=downwave)
          lfo.once = True  # Apply the pitch bend only once per note trigger
          lfo.offset = 0.33  # Offset the starting point of the sweep
          lfo.scale = 0.3  # Scale how much the pitch bends down
          lfo.rate = 20  # Speed of the pitch bend sweep
          lfo.retrigger()  # Start the LFO sweep immediately

          # Create an amplitude envelope for the cowbell's decay.
          # attack_time=0.0: instant onset for a sharp, punchy attack
          # decay_time=0.055: short decay of 55ms for a bright, percussive cowbell sound
          # release_time=0: no additional fade after the decay
          # attack_level=1: peak volume (maximum)
          # sustain_level=0: target level to fade to (complete silence)
          amp_env = synthio.Envelope(attack_time=0.0, decay_time=0.055, release_time=0, attack_level=1, sustain_level=0)

          # Create the cowbell note using a square wave for a bright, metallic tone.
          # frequency=540 Hz: mid-high frequency produces the characteristic metallic cowbell sound
          # waveform=squarewave: square wave creates the bright, hollow timbre of a cowbell
          # bend=lfo: applies the pitch bend from the LFO for added character
          note = synthio.Note(frequency=540, envelope=amp_env, waveform=squarewave, bend=lfo)

          # Send the note to the synthesizer to play it immediately.
          synth.press((note,))