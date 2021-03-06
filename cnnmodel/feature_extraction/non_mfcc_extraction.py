import numpy
import math

EPS = 1e-8  # 0.00000001
win_length = 0.025
win_step = 0.01


def audio2frame(signal, frame_length, frame_step, winfunc=lambda x: numpy.ones((x,))):
    """
    Frame a signal into overlapping frames.
    :param signal: the audio signal to frame.
    :param frame_length: length of each frame measured in samples.
    :param frame_step: number of samples after the start of the previous frame that the next frame should begin.
    :param winfunc: the analysis window to apply to each frame. By default no window is applied.
    :returns: an array of frames. Size is NUMFRAMES by frame_len.
    """
    signal_length = len(signal)
    frame_length = int(round(frame_length))
    frame_step = int(round(frame_step))
    if signal_length <= frame_length:
        frames_num = 1
    else:
        frames_num = 1 + int(math.ceil((1.0 * signal_length - frame_length) / frame_step))

    pad_length = int((frames_num - 1) * frame_step + frame_length)

    zeros = numpy.zeros((pad_length - signal_length,))
    pad_signal = numpy.concatenate((signal, zeros))

    indices = numpy.tile(numpy.arange(0, frame_length), (frames_num, 1)) + numpy.tile(
        numpy.arange(0, frames_num * frame_step, frame_step), (frame_length, 1)).T
    indices = numpy.array(indices, dtype=numpy.int32)
    frames = pad_signal[indices]
    win = numpy.tile(winfunc(frame_length), (frames_num, 1))

    return frames * win


def get_p2pamplitude(signal):
    """
    f1 : Compute the peak-to-peak amplitude of the signal
    """
    return numpy.max(signal) - numpy.min(signal)


def get_mean_energy_over_syllable_nucleus(energy):
    """
    f2 : Mean energy over syllable nucleus
    """
    return numpy.mean(energy)


def get_max_energy_over_syllable_nucleus(energy):
    """
    f3 : Max energy over syllable nucleus
    """
    return numpy.max(energy)


def get_duration(signal, samplerate):
    """
    f4 & f5 : Duration of a sound wave. Send input (syllable/vowel) accordingly
    """
    len_frames = len(signal)
    return len_frames / samplerate


def get_max_pitch_over_syllable_nucleus(pitch_for_frames):
    """
    f6 : Maximum pitch over syllable nucleus
    """
    return numpy.max(pitch_for_frames)


def get_mean_pitch_over_syllable_nucleus(pitch_for_frames):
    """
    f7 : Mean pitch over syllable nucleus
    """
    return numpy.mean(pitch_for_frames)


def pitch_from_zcr(frame, fs):
    """
    The function detects the F0 of isolated phoneme by zero-crossing
    """
    M = numpy.round(0.016 * fs) - 1
    # print (frames.shape)
    R = numpy.correlate(frame, frame, mode='full')
    g = R[len(frame) - 1]
    R = R[len(frame):-1]
    # estimate m0 (as the first zero crossing of R)
    [a, ] = numpy.nonzero(numpy.diff(numpy.sign(R)))
    if len(a) == 0:
        m0 = len(R) - 1
    else:
        m0 = a[0]

    if M > len(R):
        M = len(R) - 1

    M = int(M)
    m0 = int(m0)
    Gamma = numpy.zeros(M)
    CSum = numpy.cumsum(frame ** 2)
    Gamma[m0:M] = R[m0:M] / (numpy.sqrt((g * CSum[M:m0:-1])) + EPS)
    ZCR = zcr(Gamma)
    if ZCR[1] > 0.15:
        HR = 0.0
        f0 = 0.0
    else:
        if len(Gamma) == 0:
            HR = 1.0
            blag = 0.0
            Gamma = numpy.zeros((M), dtype=numpy.float64)
        else:
            HR = numpy.max(Gamma)
            blag = numpy.argmax(Gamma)
        # Get fundamental frequency:
        f0 = fs / (blag + EPS)
        if f0 > 5000:
            f0 = 0.0
        if HR < 0.1:
            f0 = 0.0
    pitch = f0
    return HR, pitch


def zcr(frame):
    """
    Compute the number and rate of sign-changes of the signal during the duration of a particular frame
    """
    count = len(frame)
    countZC = numpy.sum(numpy.abs(numpy.diff(numpy.sign(frame)))) / 2
    return countZC, (numpy.float64(countZC) / numpy.float64(count - 1.0))


def get_energy_for_frame(frame):
    """
    Compute energy value of frame
    """
    return numpy.sum(frame ** 2) / numpy.float64(len(frame))


def get_energy_for_frames(frames):
    """
    Compute energy value for all frames
    """
    energy = []
    for i in range(len(frames)):
        energy.append(get_energy_for_frame(frames[i]))
    return energy


def get_pitch_values(frames, fs):
    """
    Compute pitch values for all frames
    """
    pitch_for_frames = []
    for i in range(len(frames)):
        pitch_for_frames.append(pitch_from_zcr(frames[i], fs))
    return pitch_for_frames


def get_non_mfcc(signal, samplerate):
    """
    Compute the non-MFCC features of the signal, these include:
    f1 : Compute the peak-to-peak amplitude of the signal
    f2 : Mean energy over syllable nucleus
    f3 : Max energy over syllable nucleus
    f4 : Duration of a vowel nucleus
    f5 : Maximum pitch over syllable nucleus
    f6 : Mean pitch over syllable nucleus
    """

    non_mfcc_features = numpy.zeros(6)
    frames = audio2frame(signal, win_length * samplerate, win_step * samplerate)
    energy = get_energy_for_frames(frames)
    pitch_vals = get_pitch_values(frames, samplerate)
    non_mfcc_features[0] = get_p2pamplitude(signal)
    non_mfcc_features[1] = get_mean_energy_over_syllable_nucleus(energy)
    non_mfcc_features[2] = get_max_energy_over_syllable_nucleus(energy)
    non_mfcc_features[3] = get_duration(signal, samplerate)
    non_mfcc_features[4] = get_max_pitch_over_syllable_nucleus(pitch_vals)
    non_mfcc_features[5] = get_mean_pitch_over_syllable_nucleus(pitch_vals)
    return non_mfcc_features
