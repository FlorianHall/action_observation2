#!/usr/bin/python

import sys
from pytrack import *
import pytrack
import trials

from pytrack.tracker import EyeLinkError
import os
import cPickle
import pyglove

box = 1
box_mapping = {'precision': 1, 'neutral': 2, 'power': 3}
# box_mapping = {'power':1, 'neutral':2, 'precision':3}


def change_boxmapping(box):

    if box == 1:

        box_mapping = {'power': 1, 'neutral': 2, 'precision': 3}
        box = 2
        return box, box_mapping

    if box == 2:

        box_mapping = {'precision': 1, 'neutral': 2, 'power': 3}
        box = 1
        return box, box_mapping

# Ask user for index of current subject
sel = Dialog.Int("Subject Index")
block_list = cPickle.load(open('rand/%i.rand' % sel))
filename = Dialog.Str("EDF File:", "SUB%03d.EDF" % sel)

# Initiate/calibrate/train the glove
glove = pyglove.DataGlove()
if not glove.use_cal_data(sel):
    glove.calibrate()
glove.train()

# Setup the system
disp = Display((1920, 1080))
track = Tracker(disp, filename)

#eyelink.sendCommand("screen_phys_coords = -266, 149, 266, -149")
#eyelink.sendCommand("screen_pixel_coords = 0.0, 0.0, 1920.0, 1080.0")

# Send subject index as metadata to EDF
track.metadata("SUBJECTINDEX", sel)

# Calibration (eyetracker)
track.setup()

# write glove calibration to files
for x, y in zip([glove.min, glove.max, glove.fist,
                 glove.flat, glove.pen, glove.mug],
                ['min', 'max', 'fist', 'flat', 'pen', 'mug']):
    cPickle.dump(x, open('gloveData/subject%03d/%s' % (sel, y), 'w'))

B = trials.Break(disp, track)

try:

    for trial_list in block_list:

        for i, t in enumerate(trial_list):
            # announce the trial to the tracker
            t['box'] = box_mapping[t['condition']]
            track.trial(i, t)
            gloveData = []
            T = trials.InstructionImage(disp, track,
                                        "stimuli/%i.bmp" % t['image'],
                                        t['box'], t['delay'], glove,
                                        t['condition'])
            track.drift()
            # try to run trial. If error occurs wait 1 sec and try again
            for n in range(1, 20):
                try:
                    T.run(6000)
                    break
                except EyeLinkError:
                    import time
                    time.sleep(1)
                    T.run(6000)
                    break

        box, box_mapping = change_boxmapping(box)
        B.run()

finally:
    # whatever happens:
    # we shutdown the display
    disp.finish()
    # and save the EDF
    track.finish()
    trials.ser.close()
