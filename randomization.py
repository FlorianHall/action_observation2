# -*- coding: utf-8 -*-
"""
Created on Fri Jan 23 14:34:56 2015

@author: Ariane Hall, Florian Mäschig
"""

import random


def make_blocks():

    _conditions = ['precision', 'power', 'neutral']
    _all_blocks = [[[]for x in range(2)]for y in range(48)]
    _blocks = [[{} for y in range(48)] for x in range(6)]

    for x in range(len(_all_blocks)):
        _all_blocks[x][0] = x
        for condition in _conditions:
            for y in range(2):
                _all_blocks[x][1].append([condition, y])
        random.shuffle(_all_blocks[x][1])

    random.shuffle(_all_blocks)

    for block in range(len(_blocks)):
        for pic in range(len(_blocks[block])):
            _blocks[block][pic]['condition'] = _all_blocks[pic][1][block][0]
            _blocks[block][pic]['image'] = _all_blocks[pic][0]
            _blocks[block][pic]['delay'] = _all_blocks[pic][1][block][1]
    for i, t in enumerate(_blocks):
        random.shuffle(_blocks[i])
    return _blocks

if __name__ == '__main__':
    import cPickle

    for k in range(1, 100):
        blocks = make_blocks()

        cPickle.dump(blocks, open('rand/%i.rand' % k, 'w'))
