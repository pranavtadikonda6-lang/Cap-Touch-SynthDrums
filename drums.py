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
        self.synth = synth
        
        # Pitch bend envelope: a short downward sweep for kick impact.
        self.lfo = synthio.LFO(waveform=downwave)
        self.lfo.once = True
        self.lfo.offset = 0.33
        self.lfo.scale = 0.3
        self.lfo.rate = 20

        # Note definitions used to create fresh notes on every play.
        self.note_template = [
            (53, sinwave2, 0.075),
            (72, sinwave1, 0.055),
            (41, sinwave2, 0.095),
        ]

    def _make_note(self, frequency, waveform, decay_time):
        envelope = synthio.Envelope(attack_time=0.0, decay_time=decay_time, release_time=0, attack_level=1, sustain_level=0)
        return synthio.Note(frequency=frequency, envelope=envelope, waveform=waveform, bend=self.lfo)

    def setLPF(self, fr):
        # Placeholder for filter control (not supported in this version of synthio)
        pass
    
    def play(self, synth=None):
        # Trigger the kick drum sound by creating fresh notes each time.
        if synth is None:
            synth = self.synth
        self.lfo.retrigger()
        notes = tuple(self._make_note(freq, wave, decay) for freq, wave, decay in self.note_template)
        synth.press(notes)

class Snare:
    # A snare instrument using noise-based waveforms and a bright sound.
    def __init__(self, synth, runRatio=1.0):
        # `synth`: the synthio synthesizer instance that will play the snare notes.
        # `runRatio`: scales the decay time of the snare envelopes.
        self.synth = synth
        
        self.runRatio = runRatio

        # Pitch drop LFO used to add snare hit character.
        self.lfo = synthio.LFO(waveform=downwave)
        self.lfo.once = True
        self.lfo.offset = 0.33
        self.lfo.scale = 0.3
        self.lfo.rate = 20

        self.note_template = [
            (90, w1, 0.115 * self.runRatio),
            (135, w2, 0.095 * self.runRatio),
            (165, w2, 0.115 * self.runRatio),
        ]

    def _make_note(self, frequency, waveform, decay_time):
        envelope = synthio.Envelope(attack_time=0.0, decay_time=decay_time, release_time=0, attack_level=1, sustain_level=0)
        return synthio.Note(frequency=frequency, envelope=envelope, waveform=waveform, bend=self.lfo)

    def setLPF(self, fr):
        # Placeholder for filter control (not supported in this version of synthio)
        pass

    def play(self, synth=None):
        # Trigger the snare sound using fresh notes.
        if synth is None:
            synth = self.synth
        self.lfo.retrigger()
        notes = tuple(self._make_note(freq, wave, decay) for freq, wave, decay in self.note_template)
        synth.press(notes)
        
class HighHat:
    # A hi-hat instrument using noise for a crisp attack.
    def __init__(self, synth, t=0.115):
        # `synth`: the synthio synthesizer instance that will play the hi-hat notes.
        # `t`: the decay time in seconds for the hi-hat envelope.
        self.synth = synth
        self.t = t

        self.lfo = synthio.LFO(waveform=downwave)
        self.lfo.once = True
        self.lfo.offset = 0.33
        self.lfo.scale = 0.3
        self.lfo.rate = 20

        self.note_template = [
            (90, noisewave, t),
            (135, noisewave, t - 0.02),
            (165, noisewave, t),
        ]

    def _make_note(self, frequency, waveform, decay_time):
        envelope = synthio.Envelope(attack_time=0.0, decay_time=decay_time, release_time=0, attack_level=1, sustain_level=0)
        return synthio.Note(frequency=frequency, envelope=envelope, waveform=waveform, bend=self.lfo)

    def setHPF(self, fr):
        # Placeholder for filter control (not supported in this version of synthio)
        pass

    def setTime(self, t):
        # Update the hi-hat envelope decay time.
        self.t = t
        self.note_template = [
            (90, noisewave, t),
            (135, noisewave, t - 0.02),
            (165, noisewave, t),
        ]
        
    def play(self, synth=None):
        # Play the hi-hat by pressing fresh note objects.
        if synth is None:
            synth = self.synth
        self.lfo.retrigger()
        notes = tuple(self._make_note(freq, wave, decay) for freq, wave, decay in self.note_template)
        synth.press(notes)

class Cowbell:
    # A cowbell instrument using a single note with a short decay.
    def __init__(self, synth):
        # `synth`: the synthio synthesizer instance that will play the cowbell.
        self.synth = synth

        self.lfo = synthio.LFO(waveform=downwave)
        self.lfo.once = True
        self.lfo.offset = 0.33
        self.lfo.scale = 0.3
        self.lfo.rate = 20

        self.note_template = (540, squarewave, 0.055)

    def _make_note(self, frequency, waveform, decay_time):
        envelope = synthio.Envelope(attack_time=0.0, decay_time=decay_time, release_time=0, attack_level=1, sustain_level=0)
        return synthio.Note(frequency=frequency, envelope=envelope, waveform=waveform, bend=self.lfo)

    def play(self, synth=None):
        # Play the cowbell by pressing a fresh note object.
        if synth is None:
            synth = self.synth
        self.lfo.retrigger()
        frequency, waveform, decay = self.note_template
        synth.press((self._make_note(frequency, waveform, decay),))
        