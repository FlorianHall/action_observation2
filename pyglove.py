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
        self.svm = False
        self.recording = False
        self.lib = ctypes.CDLL('glove.so')
        self.glove_id = self.lib[mapping['setup']]('')

        if not self.glove_id:
            raise RuntimeError('Glove failed to initialize!')
        else:
            print "Glove initialized"

    def __getattr__(self, key):
        """
        Map calls to functions that DataGlove does not possess to
        the C-library
        """
        return self.lib[mapping[key]]

    def show_img(self, img):

        self.background.fill((250, 250, 250))
        imgpos = img.get_rect()
        imgpos.center = self.screen.get_rect().center
        self.screen.blit(self.background, (0, 0))
        self.screen.blit(img, imgpos)
        pygame.display.flip()

    def show_start(self):

        self.background.fill((250, 250, 250))
        imgpos = self.start.get_rect()
        imgpos.center = self.screen.get_rect().center
        self.screen.blit(self.background, (0, 0))
        self.screen.blit(self.start, imgpos)
        pygame.display.flip()

    def record(self):

        _a = [0 for x in range(5)]

        for x in range(10):
            _tmp = self.poll_raw()

            for y in range(len(_a)):
                _a[y] = _tmp[y] + _a[y]

            time.sleep(0.1)

        for y in range(len(_a)):
            _a[y] = _a[y] / float(10)

        if self.trials[self.ind] == 0:
            self.flat.append(_a)
        if self.trials[self.ind] == 1:
            self.fist.append(_a)
        if self.trials[self.ind] == 2:
            self.pen.append(_a)
        if self.trials[self.ind] == 3:
            self.mug.append(_a)

        self.ind += 1

    def record_all(self):

        _a = []

        for x in range(10):

            _a.append(self.poll_raw())
            time.sleep(0.1)

        if self.trials[self.ind] == 0:
            self.flat.extend(_a)
        if self.trials[self.ind] == 1:
            self.fist.extend(_a)
        if self.trials[self.ind] == 2:
            self.pen.extend(_a)
        if self.trials[self.ind] == 3:
            self.mug.extend(_a)

        self.ind += 1

    def correct(self):

        if self.ind <= 0:
            return

        ind = self.ind - 1

        if self.trials[ind] == 0:
            self.flat.pop()
        if self.trials[ind] == 1:
            self.fist.pop()
        if self.trials[ind] == 2:
            self.pen.pop()
        if self.trials[ind] == 3:
            self.mug.pop()

        self.ind = ind

    def calibrate(self):
        """
        Calibrates the glove to be able to use normalized output
        """
        pygame.init()

        self.flat = []
        self.fist = []
        self.pen = []
        self.mug = []
        self.screen = pygame.display.set_mode((1920, 1080))
#        pygame.display.toggle_fullscreen()
        self.start = pygame.image.load("start.bmp")
        flat = pygame.image.load("flat.bmp")
        fist = pygame.image.load("fist.bmp")
        pen = pygame.image.load("pen.bmp")
        mug = pygame.image.load("mug.bmp")
        ok = pygame.image.load("ok.bmp")
        ok = pygame.transform.scale(ok, (400, 250))
        screens = [flat, fist, pen, mug]

        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill((250, 250, 250))

        imagepos = self.start.get_rect()
        self.background.blit(self.start, imagepos)

        self.screen.blit(self.background, (0, 0))
        pygame.display.flip()

        trials_nr = 30
        rng_trial = range(4)
        self.trials = []

        for trial in range(trials_nr):

            random.shuffle(rng_trial)
            self.trials.extend(rng_trial)

        running = True

        while running:
            self.show_start()

            for event in pygame.event.get():

                if event.type == pygame.KEYUP:

                    if event.key == pygame.K_RETURN:
                        running = False

        self.ind = 0
        running = True

        while running:

            self.show_img(screens[self.trials[self.ind]])

            for event in pygame.event.get():

                if event.type == pygame.KEYUP:

                    if event.key == pygame.K_RETURN:

                        self.record_all()
                        self.show_img(ok)
                        time.sleep(0.3)

                        if self.ind == len(self.trials):
                            running = False

                    if event.key == pygame.K_ESCAPE:
                        running = False
                        pygame.quit()

                    if event.key == pygame.K_c:
                        self.correct()

                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()

        pygame.quit()

        self.max = [0 for y in range(5)]
        for i in range(len(self.flat)):
            for y in range(5):
                for condition in [self.fist,
                                  self.flat,
                                  self.pen,
                                  self.mug]:
                    if condition[i][y] > self.max[y]:
                        self.max[y] = condition[i][y]

        self.min = [5000 for y in range(5)]
        for i in range(len(self.flat)):
            for y in range(5):
                for condition in [self.fist,
                                  self.flat,
                                  self.pen,
                                  self.mug]:
                    if condition[i][y] < self.min[y]:
                        self.min[y] = condition[i][y]

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
