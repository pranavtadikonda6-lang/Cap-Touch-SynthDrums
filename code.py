import pykit_explorer
import time
import synthio


from cap_touch import CapTouch
from drums import KickDrum, Snare, HighHat, Cowbell


try:
    from audioio import AudioOut
except ImportError:
    from audiopwmio import PWMAudioOut as AudioOut




def make_sine_wave(length=256):
    # Simple sine waveform generator for reference (not used in drum mode)
    import array, math
    wave = array.array("h", [0] * length)
    for i in range(length):
        wave[i] = int(math.sin(2 * math.pi * i / length) * 32767)
    return wave




# Initialize synthesizer
sample_rate = 22050
synth = synthio.Synthesizer(sample_rate=sample_rate)
print(f"Max polyphony: {synth.max_polyphony}")
print(f"Max waveform length: {synthio.waveform_max_length}")



# Create drum instances
# Each pad will trigger a different drum sound
kick = KickDrum(synth)
snare = Snare(synth, runRatio=1.0)
hihat = HighHat(synth, t=0.08)
hihat_open = HighHat(synth, t=0.15)
cowbell = Cowbell(synth)


# Pad configuration: each pad maps to a drum instrument
pads = [
    {"name": "A", "pin": board.A4, "drum": kick},
    {"name": "B", "pin": board.A3, "drum": snare},
    {"name": "C", "pin": board.A2, "drum": hihat},
    {"name": "D", "pin": board.A1, "drum": hihat_open},
    {"name": "E", "pin": board.A0, "drum": cowbell},
]


# Initialize capacitive touch sensors and held state
for pad in pads:
    pad["cap"] = CapTouch(pad["pin"])
    pad["held"] = False


# Start audio playback
audio = AudioOut(board.DAC)
audio.play(synth)


# Main loop: monitor touch and trigger drums
while True:
      for pad in pads:
          pad["cap"].update()

          if pad["cap"].just_touched or pad["held"]:
              if not pad["held"]:
                  pad["drum"].play(synth)
                  print(f"Touched {pad['name']}! Playing {pad['drum'].__class__.__name__}")
                  #print(f"Synth pressed notes: {synth.pressed}")  # DEBUG
              pad["held"] = True

          if pad["cap"].just_released:
              print(f"Released {pad['name']}!")
              pad["held"] = False

      time.sleep(0.1)
