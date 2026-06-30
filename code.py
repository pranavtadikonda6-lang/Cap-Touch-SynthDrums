# Import CircuitPython libraries for hardware interaction and audio synthesis
import pykit_explorer  # Board-specific library for hardware setup
import synthio  # Adafruit's synthesizer library for generating audio

# Import capacitive touch sensor driver
from cap_touch import CapTouch
# Import drum classes from the drums module
from drums import KickDrum, Snare, HighHat, Cowbell

# Try to import AudioOut from audioio (preferred), fall back to PWMAudioOut if unavailable
try:
    from audioio import AudioOut
except ImportError:
    from audiopwmio import PWMAudioOut as AudioOut









# ============================================================================
# SYNTHESIZER INITIALIZATION
# ============================================================================

# Initialize the synthesizer with a standard CD-quality sample rate
sample_rate = 22050  # 22,050 samples per second (standard audio sample rate)
synth = synthio.Synthesizer(sample_rate=sample_rate)

# Print debug information about synthesizer capabilities
print(f"Max polyphony: {synth.max_polyphony}")  # How many notes can play simultaneously
print(f"Max waveform length: {synthio.waveform_max_length}")  # Maximum waveform table size



# ============================================================================
# DRUM INSTANCE CREATION
# ============================================================================

# Create drum instances - each drum shares the same synthesizer for audio output
kick = KickDrum(synth)  # Kick drum (low frequency bass)
snare = Snare(synth)  # Snare drum (noise-based percussive sound)
hihat = HighHat(synth, t=0.08)  # Closed hi-hat (tight, short decay)
hihat_open = HighHat(synth, t=0.15)  # Open hi-hat (longer, ringing decay)
cowbell = Cowbell(synth)  # Cowbell (bright, metallic sound)


# ============================================================================
# PAD CONFIGURATION
# ============================================================================

# Configure each capacitive touch pad: assign a name, GPIO pin, and drum instrument.
# When a pad is touched, its corresponding drum sound will play.
pads = [
    {"name": "A", "pin": board.A4, "drum": kick},  # Pad A → Kick drum
    {"name": "B", "pin": board.A3, "drum": snare},  # Pad B → Snare drum
    {"name": "C", "pin": board.A2, "drum": hihat},  # Pad C → Closed hi-hat
    {"name": "D", "pin": board.A1, "drum": hihat_open},  # Pad D → Open hi-hat
    {"name": "E", "pin": board.A0, "drum": cowbell},  # Pad E → Cowbell
]


# ============================================================================
# CAPACITIVE TOUCH SENSOR INITIALIZATION
# ============================================================================

# Initialize capacitive touch sensors for each pad and track their held state
for pad in pads:
    # Create a capacitive touch sensor instance for this pad's GPIO pin
    pad["cap"] = CapTouch(pad["pin"])
    # Track whether this pad is currently being held (for continuous vs. single-press handling)
    pad["held"] = False


# ============================================================================
# AUDIO OUTPUT SETUP
# ============================================================================

# Initialize the audio output device (speaker via DAC - Digital-to-Analog Converter)
audio = AudioOut(board.DAC)  # Send audio to the board's DAC pin
audio.play(synth)  # Connect the synthesizer to the audio output and start playback


# ============================================================================
# MAIN CONTROL LOOP
# ============================================================================

# Continuously monitor touch input and trigger drum sounds
while True:
    # Iterate through all configured pads
    for pad in pads:
        # Update the capacitive touch sensor state for this pad
        pad["cap"].update()

        # Check if this pad is newly touched OR is being held down
        if pad["cap"].just_touched or pad["held"]:
            # Only trigger the drum sound once when first touched (not repeatedly while held)
            if not pad["held"]:
                # Play the drum associated with this pad by calling its play() method
                pad["drum"].play(synth)
                # Print a message to the serial console for debugging/feedback
                print(f"Touched {pad['name']}! Playing {pad['drum'].__class__.__name__}")
                # Uncomment below to see which notes are currently pressed in the synthesizer:
                # print(f"Synth pressed notes: {synth.pressed}")
            # Mark this pad as being held so we don't retrigger the drum repeatedly
            pad["held"] = True

        # Check if this pad was just released (finger lifted off)
        if pad["cap"].just_released:
            # Print a message to the serial console
            print(f"Released {pad['name']}!")
            # Clear the held state so the pad can trigger again when touched next
            pad["held"] = False

    # Small delay between loop iterations to prevent overwhelming the processor
    time.sleep(0.1)  # Wait 100 milliseconds before checking sensors again