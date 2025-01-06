"""
6.101 Lab:
Audio Processing
"""

import wave
import struct

# No additional imports allowed!


def backwards(sound):
    """
    Returns a new sound containing the samples of the original in reverse
    order, without modifying the input sound.

    Args:
        sound: a dictionary representing the original mono sound

    Returns:
        A new mono sound dictionary with the samples in reversed order
    """
    dic = {}
    dic["rate"] = sound["rate"]
    list2 = []
    list2 = sound["samples"][::-1]
    dic["samples"] = list2
    return dic


def mix(sound1, sound2, p):
    """
    Returns a new sound with a mix of 2 sounds in accordance
    with a mixing parameter.
    The original sound is unchanged.

    Args:
        sound1: a dictionary representing an original mono sound
        sound2: a dictionary representing an original mono sound
        p: mixing parameter

    Returns:
        A new mono sound dictionary with the samples mixed according
        to the mixing parameter
    """
    # mix 2 good sounds
    if (
    not ("rate" in sound1) or not ("rate" in sound2) or sound1["rate"] != sound2["rate"]
    ):
        print("no")
        return None

    r = sound1["rate"]  # get rate
    #print(sound1 + " " + sound2)
    sound1 = sound1["samples"]
    sound2 = sound2["samples"]
    length = min(len(sound1), len(sound2))
    # if len(sound1) < len(sound2):
    #     l = len(sound1)
    # elif len(sound2) < len(sound1):
    #     l = len(sound2)
    # elif len(sound1) == len(sound2):
    #     l = len(sound1)
    # else:
    #     print("whoops")
    #     return

    sounds = []
    x = 0
    while x <= length:
        s2, s1 = p * sound1[x], sound2[x] * (1 - p)
        sounds.append(s1 + s2)  # add sounds
        x += 1
        if x == length:  # end
            break

    return {"rate": r, "samples": sounds}  # return new sound


def echo(sound, num_echoes, delay, scale):
    """
    Compute a new signal consisting of several scaled-down and delayed versions
    of the input sound. Does not modify input sound.

    Args:
        sound: a dictionary representing the original mono sound
        num_echoes: int, the number of additional copies of the sound to add
        delay: float, the amount of seconds each echo should be delayed
        scale: float, the amount by which each echo's samples should be scaled

    Returns:
        A new mono sound dictionary resulting from applying the echo effect.
    """
    result = {"rate":sound["rate"],
              "samples": sound["samples"].copy()}
    sample_delay = round(delay * sound["rate"])
    for i in range(0, sample_delay * num_echoes):
        result["samples"].append(0)
    #print(result)
    for i in range(1, num_echoes+1):
        for j in range(0, len(sound["samples"])):
            #print(j + (sample_delay * (i - 1)))
            #print(scale ** (i-1) * (j+1))
            result["samples"][j + i * sample_delay] += sound["samples"][j]*(scale ** i)
    return result


def pan(sound):
    '''
    For our first effect using stereo sound, we'll create a really neat spatial effect. 
    We achieve this effect by adjusting the volume
    in the left and right channels separately,
    so that the left channel starts out at full volume 
    and ends at 0 volume (and vice versa for the right channel).

    Args:
        sound: a dictionary representing the original stereo sound
    
    Returns:
        A new stereo sound dictionary resulting from applying the pan effect.
    '''
    stereo= {}
    stereo["rate"] = sound["rate"]
    stereo["left"] = []
    stereo["right"] = []
    samples = len(sound["left"])
    stereo["left"].append(sound["left"][0])
    stereo["right"].append(0)
    for i in range(1, samples - 1):
        stereo["left"].append(sound["left"][i] * (1-(i / (samples - 1))))
        stereo["right"].append(sound["right"][i] * (i / (samples-1)))
    stereo["left"].append(0)
    stereo["right"].append(sound["right"][samples-1])
    return stereo

def remove_vocals(sound):
    res = {}
    res["rate"] = sound["rate"]
    res["samples"] = []
    for i in range(len(sound["left"])):
        res["samples"].append(sound["left"][i] - sound["right"][i])
    return res


# below are helper functions for converting back-and-forth between WAV files
# and our internal dictionary representation for sounds


def load_wav(filename, stereo=False):
    """
    Load a file and return a sound dictionary.

    Args:
        filename: string ending in '.wav' representing the sound file
        stereo: bool, by default sound is loaded as mono, if True sound will
            have left and right stereo channels.

    Returns:
        A dictionary representing that sound.
    """
    sound_file = wave.open(filename, "r")
    chan, bd, sr, count, _, _ = sound_file.getparams()

    assert bd == 2, "only 16-bit WAV files are supported"

    out = {"rate": sr}

    left = []
    right = []
    for i in range(count):
        frame = sound_file.readframes(1)
        if chan == 2:
            left.append(struct.unpack("<h", frame[:2])[0])
            right.append(struct.unpack("<h", frame[2:])[0])
        else:
            datum = struct.unpack("<h", frame)[0]
            left.append(datum)
            right.append(datum)

    if stereo:
        out["left"] = [i / (2**15) for i in left]
        out["right"] = [i / (2**15) for i in right]
    else:
        samples = [(ls + rs) / 2 for ls, rs in zip(left, right)]
        out["samples"] = [i / (2**15) for i in samples]

    return out


def write_wav(sound, filename):
    """
    Save sound to filename location in a WAV format.

    Args:
        sound: a mono or stereo sound dictionary
        filename: a string ending in .WAV representing the file location to
            save the sound in
    """
    outfile = wave.open(filename, "w")

    if "samples" in sound:
        # mono file
        outfile.setparams((1, 2, sound["rate"], 0, "NONE", "not compressed"))
        out = [int(max(-1, min(1, v)) * (2**15 - 1)) for v in sound["samples"]]
    else:
        # stereo
        outfile.setparams((2, 2, sound["rate"], 0, "NONE", "not compressed"))
        out = []
        for l_val, r_val in zip(sound["left"], sound["right"]):
            l_val = int(max(-1, min(1, l_val)) * (2**15 - 1))
            r_val = int(max(-1, min(1, r_val)) * (2**15 - 1))
            out.append(l_val)
            out.append(r_val)

    outfile.writeframes(b"".join(struct.pack("<h", frame) for frame in out))
    outfile.close()


if __name__ == "__main__":
    # Code placed inside the if __name__ == "__main__" statement will only
    # be executed when you run the lab.py file.

    # Code placed in this special if statement will not be executed when you run
    # the tests in the test.py file or when you submit your code to the submission
    # server.

    # This makes it a good place to put your code for generating and saving
    # sounds, or any other code you write for testing on your computer.

    # Note that your checkoff conversation with a staff member will likely involve
    # showing and discussing the code you wrote to generate the sounds that you
    # submitted on the lab page, so please do not delete that code. However, you
    # can comment it out.

    # Here is an example of loading a file (note that this is specified as
    # sounds/hello.wav, rather than just as hello.wav, to account for the
    # sound files being in a different directory than this file):

    # print("Loading hello file...")
    # hello = load_wav("sounds/hello.wav")
    # mystery = load_wav("sounds/mystery.wav")
    # synth = load_wav("sounds/synth.wav")
    # water = load_wav("sounds/water.wav")
    chord = load_wav("sounds/chord.wav")

    # write_wav(backwards(hello), "hello_reversed.wav")
    # write_wav(backwards(mystery), "mystery_reversed.wav")
    # write_wav(mix(synth, water, 0.2), "synthwater.wav")
    write_wav(echo(chord, 5, 0.3, 0.6), "chordecho.wav")

    # p = load_wav("sounds/car.wav", stereo=True)
    # write_wav(pan(p), "pancar.wav")

    # mountain = load_wav("sounds/lookout_mountain.wav", stereo=True)
    # write_wav(remove_vocals(mountain), "remmountain.wav")
    # s = {
    # 'rate': 8,
    # 'samples': [1, 2, 3, 4, 5],
    # }
    # print(echo(s, 2, 0.4, 0.2))
