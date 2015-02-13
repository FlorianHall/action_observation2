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
        self.box = box
        self.glove = glove
        self.delay = delay
        self.condition = condition

    def send_GloveData(self):

        _tmp = self.glove.poll()
        for s, v in enumerate(_tmp):
            self._track.sendMessage("GLOVE%i %f" % (s, v))

    def run(self, duration=10000):
        surf = self._disp.get_surface()
        ser.flushInput()
        self._track.start_trial()
        start = pylink.currentTime()
        surf.blit(self._inst, (0, 0))
        pygame.display.flip()

        while True:
            rb = int(ser.readline())
            self.send_GloveData()
            if rb == self.box:
                self._track.sendMessage("BOX %i" % (rb))
                break

        conditions = [False for x in range(10)]
        cnt = 0

        while True:
            self.send_GloveData()
            conditions[cnt % 10] = self.glove.is_condition(self.condition)
            if all(conditions) is True:
                break
            pygame.display.flip()
            cnt += 1

        if self.delay:
            self._track.sendMessage("Delay 1s")
            for x in range(60):
                self.send_GloveData()
                pygame.display.flip()

        surf.blit(self._bmp, (0, 0))
        pygame.display.flip()
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
