#!/usr/bin/python

import sys
from pytrack import *
import pytrack
import trials

from pytrack.tracker import EyeLinkError
import os
import cPickle
import pyglove

glove = pyglove.DataGlove()
glove.calibrate()
glove.train()


# Ask user for index of current subject
sel = Dialog.Int("Subject Index")
block_list = cPickle.load(open('rand/%i.rand' % sel))
filename = Dialog.Str("EDF File:", "SUB%03d.EDF" % sel)

# write glove calibration to files
for x, y in zip([glove.min, glove.max, glove.fist,
                 glove.flat, glove.pen, glove.mug],
                ['min', 'max', 'fist', 'flat', 'pen', 'mug']):
    cPickle.dump(x, open('gloveData/subject%03d/%s' % (sel, y), 'w'))

# Setup the system
disp = Display((1920, 1080))
track = Tracker(disp, filename)

# Send subject index as metadata to EDF
track.metadata("SUBJECTINDEX", sel)
# Calibration
track.setup()

box_mapping = {'precision': 1, 'neutral': 2, 'power': 3}
# box_mapping = {'power':1, 'neutral':2, 'precision':3}


# enumerate all trials:
# i runs from 0 to number of trials-1
# t is the trial description from the matlab file

try:

    for trial_list in block_list:

        for i, t in enumerate(trial_list):
            # announce the trial to the tracker
            print i, t
            t['box'] = box_mapping[t['condition']]
            track.trial(i, t)
            gloveData = []
            T = trials.InstructionImage(disp, track,
                                        "stimuli/%i.bmp" % t['image'],
                                        t['box'], t['delay'], glove,
                                        t['condition'], gloveData)
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

        # if you want only one block
        break
finally:
    # whatever happens:
    # we shutdown the display
    disp.finish()
    # and save the EDF
    track.finish()
    trials.ser.close()
