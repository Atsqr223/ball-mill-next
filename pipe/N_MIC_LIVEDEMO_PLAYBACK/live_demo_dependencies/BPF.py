from scipy.signal import butter, lfilter, filtfilt

def butter_bandpass_filter(data,lowcut, highcut, fs, order=5):
    #return butter(order, [lowcut, highcut], fs=fs, btype='band')
    b,a= butter(order, [lowcut/(fs/2), highcut/(fs/2)], btype='band')
    y = filtfilt(b,a,data)
    return y
def butter_lowpass_filter(data, highcut, fs, order=5):
    #b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    #y = lfilter(b, a, data)
    #y = filtfilt(b, a, data)

    b,a = butter(order,highcut/(fs/2), btype='low')
    y = filtfilt(b,a,data)
    return y

