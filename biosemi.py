"""
Builds on example code by Ilya Kuzovkin
https://github.com/kuz/pyactivetwo/blob/master/pyactivetwo/pyactivetwo.py
"""

import socket
import numpy as np


class ActiveTwo():
    def __init__(self, host='127.0.0.1', sfreq=1024, 
                 port=1111, nchannels=65, tcpsamples=4):
        """
        Initialize connection and parameters of the signal
        :param host: IP address where ActiView is running
        :param port: Port ActiView is listening on
        :param nchannels: Number of EEG channels
        """
        
        self.host = host
        self.port = port
        self.nchannels = nchannels
        self.sfreq = sfreq
        self.tcpsamples = tcpsamples
        self.buffer_size = self.nchannels * self.tcpsamples * 3

        # open connection
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.host, self.port))

    def read(self, duration):
        """
        Read signal from the EEG device
        :param duration: How long to read in seconds
        :return: Signal in the matrix form: (samples, channels)
        """

        # initialize final data array
        rawdata = np.empty((0, self.nchannels))

        # The reader process will run until requested amount of data is collected
        samples = 0
        while samples < duration * self.sfreq:

            # Create a 16-sample signal_buffer
            signal_buffer = np.zeros((self.nchannels, self.tcpsamples))

            # Read the next packet from the network
            # sometimes there is an error and packet is smaller than needed
            # read until get a good one
            data = []
            while len(data) != self.buffer_size:
                data = self.s.recv(self.buffer_size)


            # Extract 16 samples from the packet (ActiView sends them in 16-sample chunks)
            for m in range(self.tcpsamples):
                # extract samples for each channel
                for ch in range(self.nchannels):
                    offset = m * 3 * self.nchannels + (ch * 3)

                    # The 3 bytes of each sample arrive in reverse order
                    sample = (data[offset+2] << 16)
                    sample += (data[offset+1] << 8)
                    sample += data[offset]

                    # Store sample to signal buffer
                    signal_buffer[ch, m] = sample

            # update sample counter
            samples += self.tcpsamples

            # transpose matrix so that rows are samples
            signal_buffer = np.transpose(signal_buffer)

            # add to the final dataset
            rawdata = np.concatenate((rawdata, signal_buffer), axis=0)
            
        self.s.close()
        return rawdata
