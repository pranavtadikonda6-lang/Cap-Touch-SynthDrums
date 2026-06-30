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
    # A bass drum instrument built from a few pitched notes and a pitch-drop LFO.
    def __init__(self, synth):
        # `synth`: the synthio synthesizer instance used to play kick notes.
        # This constructor creates internal note objects that are retained for reuse.
        self.synth = synth

    def play(self, synth=None):
        if synth is None:
            synth = self.synth

        # Create a fresh LFO for this note (not reused)
        # Pitch bend envelope: a short downward sweep for kick impact.
        # The LFO is used as a bend source for each note.
        lfo = synthio.LFO(waveform=downwave)
        lfo.once = True
        lfo.offset = 0.33
        lfo.scale = 0.3
        lfo.rate = 20
        lfo.retrigger()

        # One short envelope note creates a kick sound.
        # Envelope parameters:
        # - attack_time: time in seconds to reach full level (0.0 means immediate)
        # - decay_time: time in seconds to fall from attack level to sustain level
        # - release_time: time in seconds to fall from sustain level to zero after note release
        # - attack_level: peak level reached at the end of the attack phase
        # - sustain_level: level held after decay until release

        amp_env = synthio.Envelope(attack_time=0.0, decay_time=0.075, release_time=0, attack_level=1, sustain_level=0)
        note = synthio.Note(frequency=53, envelope=amp_env, waveform=sinwave2, bend=lfo)

        synth.press((note,))

class Snare:
    # A snare instrument using noise-based waveforms and a bright low-pass filter.
    def __init__(self, synth):
        # `synth`: the synthio synthesizer instance that will play the snare notes.
        # The constructor builds noise-based note objects and stores them internally.
        self.synth = synth
        
        # Noise-based notes to give the snare its body and snap.
        # `frequency` is the base pitch of the note in Hz.
        # `waveform` selects the sample table used for the sound.
        # `bend` applies the LFO pitch sweep.
        

    def play(self, synth=None):
        
        if synth is None:
            synth = self.synth

        # Create a fresh LFO for this note (not reused)
        # Pitch drop LFO used to add snare hit character.
        lfo = synthio.LFO(waveform=downwave)
        lfo.once = True
        lfo.offset = 0.33
        lfo.scale = 0.3
        lfo.rate = 20
        lfo.retrigger()

        amp_env = synthio.Envelope(attack_time=0.0, decay_time=0.115, release_time=0, attack_level=1, sustain_level=0)
        note = synthio.Note(frequency=90, envelope=amp_env, waveform=w1, bend=lfo)


        synth.press((note,))
        
class HighHat:
      def __init__(self, synth, t=0.115):
          self.synth = synth
          self.t = t

      def setHPF(self, fr):
          pass

      def setTime(self, t):
          self.t = t

      def play(self, synth=None):
          if synth is None:
              synth = self.synth

          amp_env = synthio.Envelope(attack_time=0.0, decay_time=self.t, release_time=0, attack_level=1, sustain_level=0)
          note = synthio.Note(frequency=90, envelope=amp_env, waveform=noisewave)

          synth.press((note,))


class Cowbell:
    # A cowbell instrument using a single note with a short decay.
    def __init__(self, synth):
        # `synth`: the synthio synthesizer instance that will play the cowbell.
        # `runRatio`: the duration of the cowbell sound in seconds, relative to the default.
        self.synth = synth

        


        # A single note for the cowbell.
        

    def play(self, synth=None):
        
        if synth is None:
            synth = self.synth

        # Create a fresh LFO for this note
        lfo = synthio.LFO(waveform=downwave)
        lfo.once = True
        lfo.offset = 0.33
        lfo.scale = 0.3
        lfo.rate = 20
        lfo.retrigger()

        # Create the cowbell note
        amp_env = synthio.Envelope(attack_time=0.0, decay_time=0.055, release_time=0, attack_level=1, sustain_level=0)
        note = synthio.Note(frequency=540, envelope=amp_env, waveform=squarewave, bend=lfo)

        # Release all and press the new note
        synth.press((note,))
        