#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pygame
import pylink
import pytrack
from pylink import *   
import serial


pygame.init()

LEFT_EYE = 0
RIGHT_EYE = 1
BINOCULAR = 2

# Show eye trace?
show_eyes = False

ser = serial.Serial('/dev/ttyACM0')


class InstructionImage(pytrack.Trial.BasicTrial):

    def __init__(self, disp, track, filename, box, delay, glove, condition):

        pytrack.Trial.BasicTrial.__init__(self, disp, track, filename)
        self._bmp = pygame.image.load(filename)
        instruction = "stimuli/box%i.bmp" % box
        self._inst = pygame.image.load(instruction)
        self._box = box
        self._glove = glove
        self.delay = delay
        self.condition = condition
        self.glove_cnt = 0

    def send_GloveData(self):

        _tmp = self._glove.poll()
        self._track.sendMessage("Glove %i %1.4f %1.4f %1.4f %1.4f %1.4f" % (self.glove_cnt, _tmp[0], _tmp[1],_tmp[2] ,_tmp[3], _tmp[4] ))
        self.glove_cnt += 1

    def condition_match(self):

        return self._glove.is_condition(self.condition)

    def wait_for_box(self):

        while True:
            self.send_GloveData()
            rb = int(ser.readline())
            if rb == self._box:
                self._track.sendMessage("Hand_in_box %i" % (rb))
                break
            pygame.display.flip()

    def wait_for_gesture(self):

        conditions = [False for x in range(30)]
        samples = len(conditions)
        cnt = 0

        while True:
            self.send_GloveData()
            conditions[cnt % samples] = self.condition_match()
            if all(conditions) is True:
                self._track.sendMessage("Gesture %s" % (self.condition))
                break
            pygame.display.flip()
            cnt += 1

    def start_delay(self):

        if self.delay:
            self._track.sendMessage("Start_delay 1")
            for x in range(120):
                self.send_GloveData()
                pygame.display.flip()
            self._track.sendMessage("Stop_delay 1")
        else:
            self._track.sendMessage("Start_delay 0")
            self._track.sendMessage("Stop_delay 0")

    def run(self, duration=10000):
        surf = self._disp.get_surface()
        ser.flushInput()
        self._track.start_trial()
        start = pylink.currentTime()
        surf.blit(self._inst, (0, 0))
        pygame.display.flip()

        self.wait_for_box()
        self.wait_for_gesture()
        self.start_delay()

        surf.blit(self._bmp, (0, 0))
        pygame.display.flip()
        self._track.sendMessage("Image_shown 1")

        target = pylink.currentTime()
        self._track.sendMessage("SYNCTIME %d" % (target - start))
        target = pylink.currentTime()
        target += duration

        while self._track.recording() and pylink.currentTime() < target:
            self.send_GloveData()
            pygame.display.flip()
            pass

        self._track.end_trial()


class Break(pytrack.Trial.BasicTrial):

    def __init__(self, track, filename):
        pytrack.Trial.BasicTrial.__init__(self, None, track, filename)
        self._bmp = pygame.image.load(filename)

    def run(self, duration=10000000):
        duration = 10000000000
        surf = pygame.display.get_surface()
        self._track.start_trial()
        start = pylink.currentTime()
        surf.blit(self._bmp, (0, 0))
        pygame.display.flip()
        target = pylink.currentTime()
        self._track.sendMessage("SYNCTIME %d" % (target-start))
        target += duration
        while self._track.recording() and pylink.currentTime() < target:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_c:
                        self._track.end_trial()
                        return
