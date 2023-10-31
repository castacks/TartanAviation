import sounddevice as sd
from scipy.io.wavfile import write
import wave
import Queue as queue
from utils import *
import time
import soundfile as sf
import numpy as np

CHUNK = 2048
CHANNELS = 1
RATE = 44100


class GetRadio:
    def __init__(self, base_path):
        self.base_path = base_path
        self.stream = sd.InputStream(samplerate = RATE , channels = CHANNELS, dtype='float32', callback=self.callback)
        self.frames = []
        self.is_record = False
        self.loopback = False

    def start_recording(self):
        if not self.is_record :
            self.frames = []
            self.stream.start()
            self.is_record = True
        # print("Started")

    def stop_recording(self):
        if (self.is_record):
            self.stream.stop()
            filename = getNextFilePath(self.base_path,'.wav') + '.wav'
            # filename = "test.wav"
            self.is_record = False
            f = np.concatenate(self.frames, axis=0)
            write(filename,RATE,f)


    def callback(self,in_data, frame_count , time_info , status):
        self.frames.append(in_data.copy())
        # print(in_data.shape)
        # if self.loopback:
        #     out_data[:] = in_data
        # else:
        #     out_data[:] = np.zeros(in_data.shape)


if __name__ == "__main__":

    radio = GetRadio("haha")
    radio.start_recording()
    time.sleep(30)
    radio.start_recording()
    time.sleep(30)
    radio.stop_recording()


    

