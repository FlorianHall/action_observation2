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

ser = serial.Serial('/dev/ttyACM0', timeout=0)


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

    def send_GloveData(self):

        _tmp = self._glove.poll()
        self._track.sendMessage("Glove %1.4f %1.4f %1.4f %1.4f %1.4f" % (_tmp[0], _tmp[1],_tmp[2] ,_tmp[3], _tmp[4] ))

    def condition_match(self):

        return self._glove.is_condition(self.condition)

    def wait_for_box(self):

        while True:
            self.send_GloveData()
            try:
                rb = int(ser.readline())
            except ValueError:
                rb = 0
                pass

            if rb == self._box:
                self._track.sendMessage("Hand_in_box %i" % (rb))
                break
            pygame.display.flip()

    def wait_for_gesture(self):

        conditions = [False for x in range(20)]
        samples = len(conditions)
        cnt = 0

        while True:
            self.send_GloveData()
            conditions[cnt % samples] = self.condition_match()
            if all(conditions) is True:
                self._track.sendMessage("Gesture %s" % (self.condition))
                break
            self.wait(25)
            cnt += 1

    def wait(self, sec):

        time = pylink.currentTime() + sec
        while pylink.currentTime() < time:
            self.send_GloveData()
            pygame.display.flip()
            pass

    def start_delay(self):

        if self.delay:
            self._track.sendMessage("Start_delay 1")
            self.wait(1500)
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

    def __init__(self, disp, track):
        self._disp = disp
        self._bmp = pygame.image.load("_break.bmp")
        self._track = track

    def run(self):
        surf = self._disp.get_surface()
        surf.blit(self._bmp, (0, 0))
        pygame.display.flip()
        running = True
        calibrate = False

        while running:
            for event in pygame.event.get():
                    if event.type == pygame.KEYUP:
                        if event.key == pygame.K_c:
                            calibrate = True
                            running = False
                        if event.key == pygame.K_RETURN:
                            running = False

        if calibrate:
            self._track.setup()
