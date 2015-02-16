import ctypes
import time
import random
import pygame
from sklearn import svm
import numpy as np

mapping = {'setup': '_Z5setupv', 'poll': '_Z4polli',
           'poll_raw': '_Z8poll_rawi',
           'getGesture': '_Z10getGesturev', 'close': '_Z5closev',
           'getAutoCalibration_lower': '_Z24getAutoCalibration_loweri',
           'getAutoCalibration_upper': '_Z24getAutoCalibration_upperi',
           }


def normalize(data, _min, _max):

    tmp = []
    total_output = []
    max_minus_min = [k - j for k, j in zip(_max, _min)]

    for i in data:
        tmp = ([k - j for k, j in zip(i, _min)])
        tmp = [float(k) / float(j) for k, j in zip(tmp, max_minus_min)]
        total_output.append(tmp)
    return total_output


class DataGlove:
    def __init__(self):
        """
        Init C-library and connect to the glove.
        """
        self.calibrated = False
        self.min = 0
        self.max = 5000
        self.flat = []
        self.fist = []
        self.pen = []
        self.mug = []
        self.pca = None
        self.svm = False
        self.recording = False
        self.lib = ctypes.CDLL('glove.so')
        self.glove_id = self.lib[mapping['setup']]('')

        if not self.glove_id:
            print "Glove failed to initialize, check access rigths!"
        else:
            print "Glove initialized"

    def __getattr__(self, key):
        """
        Map calls to functions that DataGlove does not possess to
        the C-library
        """
        return self.lib[mapping[key]]

    def record_single(self, img, screen, background, ok, _time):

        _a = [0 for x in range(5)]

        background.fill((250, 250, 250))
        imgpos = img.get_rect()
        imgpos.center = screen.get_rect().center
        screen.blit(background, (0, 0))
        screen.blit(img, imgpos)
        pygame.display.flip()

        running = True
        # main loop
        while running:
            # event handling, gets all event from the eventqueue
            for event in pygame.event.get():
                # only do something if the event is of type QUIT
                if event.type == pygame.KEYUP:
                    if (event.key == pygame.K_RETURN):
                        for x in range(_time):
                            _tmp = self.poll_raw()
                            for y in range(len(_a)):
                                _a[y] = _tmp[y] + _a[y]
                            time.sleep(0.1)
                        for y in range(len(_a)):
                            _a[y] = _a[y]/_time
                    screen.blit(ok, imgpos)
                    pygame.display.flip()
                    time.sleep(0.06)
                    running = False

                if event.type == pygame.QUIT:
                    # change the value to False, to exit the main loop
                    running = False
                    pygame.quit()
                    # return
        return _a

    def calibrate(self):
        """
        Calibrates the glove to be able to use normalized output
        """
        pygame.init()

        screen = pygame.display.set_mode((1920, 1080))
        pygame.display.toggle_fullscreen()
        start = pygame.image.load("start.bmp")
        flat = pygame.image.load("flat.bmp")
        fist = pygame.image.load("fist.bmp")
        pen = pygame.image.load("pen.bmp")
        mug = pygame.image.load("mug.bmp")
        ok = pygame.image.load("ok.bmp")
        ok = pygame.transform.scale(ok, (400, 250))

        background = pygame.Surface(screen.get_size())
        background = background.convert()
        background.fill((250, 250, 250))

        imagepos = start.get_rect()
        background.blit(start, imagepos)

        screen.blit(background, (0, 0))
        pygame.display.flip()

        running = True
        # main loop
        while running:
            # event handling, gets all event from the eventqueue
            for event in pygame.event.get():
                # only do something if the event is of type QUIT
                if event.type == pygame.KEYUP:
                    if (event.key == pygame.K_RETURN):
                        running = False

                if event.type == pygame.QUIT:
                    # change the value to False, to exit the main loop
                    running = False
                    pygame.quit()
                    # return

        hand_flat = []
        hand_fist = []
        hand_mug = []
        hand_pen = []

        trials = 30
        rng_trial = range(1, 5)

        for trial in range(0, trials):
            random.shuffle(rng_trial)
            for y in rng_trial:
                if y == 1:
                    hand_flat.append(self.record_single(flat, screen,
                                                        background, ok, 10))
                if y == 2:
                    hand_fist.append(self.record_single(fist, screen,
                                                        background, ok, 10))
                if y == 3:
                    hand_pen.append(self.record_single(pen, screen,
                                                       background, ok, 10))
                if y == 4:
                    hand_mug.append(self.record_single(mug, screen,
                                                       background, ok, 10))

        pygame.quit()

        hand_max = [0 for y in range(5)]

        for i in range(len(hand_flat)):
            for y in range(5):
                for condition in [hand_fist, hand_flat, hand_pen, hand_mug]:
                    if condition[i][y] > hand_max[y]:
                        hand_max[y] = condition[i][y]

        hand_min = [5000 for y in range(5)]
        for i in range(len(hand_flat)):
            for y in range(5):
                for condition in [hand_fist, hand_flat, hand_pen, hand_mug]:
                    if condition[i][y] < hand_min[y]:
                        hand_min[y] = condition[i][y]

        self.min = hand_min
        self.max = hand_max
        self.flat = hand_flat
        self.fist = hand_fist
        self.pen = hand_pen
        self.mug = hand_mug
        self.calibrated = True

    def poll_buildIn_calibrated(self):
        """
        Return a list of sensor values for all 15 sensors.
        """
        poll = self.lib._Z4polli
        poll.restype = ctypes.c_float
        return [poll(x) for x in [0, 3, 6, 9, 12]]

    def poll_raw(self):
        """
        Return a list of sensor values for all 15 sensors.
        """
        poll = self.lib._Z8poll_rawi
        poll.restype = ctypes.c_float
        return [poll(x) for x in [0, 3, 6, 9, 12]]

    def poll(self):
        """
        Return a list of sensor values for all 5 sensors.
        poll_raw is returned if glove is not calibrated
        """
        if not self.calibrated:
            return self.poll_raw()

        if self.calibrated:

            _tmp = [0 for x in range(5)]
            _max_minus_min = [k - j for k, j in zip(self.max, self.min)]
            _tmp_poll = self.poll_raw()

        for x in range(len(_tmp)):
            _tmp[x] = _tmp_poll[x] - self.min[x]
            _tmp[x] = _tmp[x] / _max_minus_min[x]

        return _tmp

    def train(self):

        if not self.calibrated:
            raise RuntimeError('Not calibrated')

        self.clf = svm.SVC()

        training_data = []
        for data in [self.flat, self.pen, self.mug, self.fist]:
            training_data.extend(normalize(data[:], self.min, self.max))

        training_classifier = []
        for x in range(0, len(training_data)/4):
            training_classifier.extend(['neutral'])
        for x in range(len(training_data)/4, (len(training_data)*2)/4):
            training_classifier.extend(['precision'])
        for x in range((len(training_data)*2)/4, (len(training_data)*3)/4):
            training_classifier.extend(['power'])
        for x in range((len(training_data)*3)/4, len(training_data)):
            training_classifier.extend(['neutral2'])

        self.clf.fit(training_data, training_classifier)
        self.svm = True

    def is_condition(self, condition):

        if not self.calibrated:
            raise RuntimeError('Not calibrated')

        if not self.svm:
            self.train()

        if self.clf.predict(self.poll()) == condition:
            return True

        else:
            return False

    def get_auto_calibration_parameters(self):

        calib = {}
        lower = self.lib._Z24getAutoCalibration_loweri
        lower.restype = ctypes.c_int
        upper = self.lib._Z24getAutoCalibration_upperi
        upper.restype = ctypes.c_int

        for sensor in [0, 3, 6, 9, 12]:
            calib[sensor] = (lower(sensor), upper(sensor))

        return calib

if __name__ == '__main__':
    pass
