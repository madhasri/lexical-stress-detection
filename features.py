import numpy
import feature_extraction
import feature_extraction_stress


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

def get_duration(sound_wave):
    """
    f4 & f5 : Duration of a sound wave. Send input (syllable/vowel) accordingly
    """
    return feature_extraction_stress.get_duration(sound_wave)

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

def get_MFCC(signal, fs, cep_num=27):
    """
    27 Mel-scale energy bands over syllable nucleus
    """
    return feature_extraction.calcMFCC(signal, fs, cep_num)

def pitch_from_zcr(frame, fs):
    M = numpy.round(0.016 * fs) - 1
    #print (frames.shape)
    R = numpy.correlate(frame, frame, mode='full')
    g = R[len(frame)-1]
    R = R[len(frame):-1]
    # estimate m0 (as the first zero crossing of R)
    [a, ] = numpy.nonzero(numpy.diff(numpy.sign(R)))
    if len(a) == 0:
        m0 = len(R)-1
    else:
        m0 = a[0]

    if M > len(R):
        M = len(R) - 1

    M = int(M)
    m0 = int(m0)
    Gamma = numpy.zeros(M)
    CSum = numpy.cumsum(frame ** 2)
    Gamma[m0:M] = R[m0:M] / (numpy.sqrt((g * CSum[M:m0:-1])) + eps)
    ZCR = feature_extraction_stress.zcr(Gamma)
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
        f0 = fs / (blag + eps)
        if f0 > 5000:
            f0 = 0.0
        if HR < 0.1:
            f0 = 0.0
    pitch = f0
    return HR, pitch

def get_energy_for_frame(frame):
    """
    Compute energy value of frame
    """
    return feature_extraction_stress.getEnergy(frame)

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
        pitch_for_Frames.append(pitch_from_zcr(frames[i], fs))
    return pitch_for_frames










