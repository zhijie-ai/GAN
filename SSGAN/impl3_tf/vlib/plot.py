#----------------------------------------------
# -*- encoding=utf-8 -*-                      #
# __author__:'xiaojie'                        #
# CreateTime:                                 #
#       2019/5/13 11:37                       #
#                                             #
#               天下风云出我辈，                 #
#               一入江湖岁月催。                 #
#               皇图霸业谈笑中，                 #
#               不胜人生一场醉。                 #
#----------------------------------------------
import numpy as np

import matplotlib
import matplotlib.pyplot as plt


import collections
import pickle

'''
Example:
import numpy as np
import plot
for i in range(1000):
    t = np.arctan(i)
    plot.plot('arctan', t)
    if i%10==0:#choose the time when flush the plot 
        plot.flush()
    plot.tick()
'''

_since_beginning = collections.defaultdict(lambda: {})
_since_last_flush = collections.defaultdict(lambda: {})

_iter = [0]
def tick():
    _iter[0] += 1

def plot(name, value):
    _since_last_flush[name][_iter[0]] = value


def flush():
    prints = []
    for name, vals in _since_last_flush.items():
        prints.append("{}\t{}".format(name, np.mean(vals.values())))
        _since_beginning[name].update(vals)

        x_vals = np.sort(_since_beginning[name].keys())
        y_vals = [_since_beginning[name][x] for x in x_vals]

        plt.clf()
        plt.plot(x_vals, y_vals)
        plt.xlabel('iteration')
        plt.ylabel(name)
        plt.savefig(name.replace(' ', '_') + '.jpg')

    print ("iter {}\t{}".format(_iter[0], "\t".join(prints)))
    _since_last_flush.clear()

    with open('log.pkl', 'wb') as f:
        pickle.dump(dict(_since_beginning), f, pickle.HIGHEST_PROTOCOL)