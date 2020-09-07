# Copyright (c) 2020 by Terry Greeniaus.
# Based on:
#   https://toyplot.readthedocs.io/en/stable/_modules/toyplot/locator.html#Extended
import math
import numpy as np


class TickResults:
    '''
    Tick results.  Variables are as follows:

        score  - what our tick labels scored, higher is better
        d_min  - domain minimum value
        d_max  - domain maximum value
        l_min  - label minimum value
        l_max  - label maximum value
        l_step - label increment
        q      - "nice" value that was used as a basis
        k      - number of labels
        locs   - label values as float
    '''
    def __init__(self, score, d_min, d_max, l_min, l_max, l_step, q, k):
        lm_fpart, _ = math.modf(l_min)
        ls_fpart, _ = math.modf(l_step)
        self.is_integer = (lm_fpart < 1e-10 and ls_fpart < 1e-10)

        self.score   = score
        self.d_min   = d_min
        self.d_max   = d_max
        self.l_min   = int(l_min) if self.is_integer else l_min
        self.l_max   = int(l_max) if self.is_integer else l_max
        self.l_step  = int(l_step) if self.is_integer else l_step
        self.extents = (min(d_min, l_min), max(d_max, l_max))
        self.q       = q
        self.k       = k

    def get_locs(self):
        '''
        Returns the list of tick values in numeric (integral or floating-point
        format, depending on the limits) format.
        '''
        return [self.l_min + t * self.l_step for t in range(self.k)]

    def get_d_locs(self):
        '''
        Returns the list of tick values that lie within the original domain.
        '''
        locs = self.get_locs()
        return [l for l in locs if self.d_min <= l <= self.d_max]

    def _get_labels(self, locs, fmt=None):
        if self.is_integer:
            return ['%s' % l for l in locs]

        if fmt:
            labels = [fmt % l for l in locs]
        else:
            labels = ['%s' % np.format_float_positional(l) for l in locs]
        max_dec = max(len(l.split('.')[1]) for l in labels)
        return [l + '0'*(max_dec - len(l.split('.')[1])) for l in labels]

    def get_labels(self, fmt=None):
        '''
        Returns text labels for the tick values.
        '''
        return self._get_labels(self.get_locs(), fmt=fmt)

    def get_d_labels(self, fmt=None):
        '''
        Returns text labels for the tick values.
        '''
        return self._get_labels(self.get_d_locs(), fmt=fmt)


def _simplicity_max(q, Q, j):
    n = len(Q)
    i = Q.index(q) + 1
    v = 1
    return (n - i) / (n - 1.0) + v - j


def _simplicity(q, Q, j, l_min, l_max, l_step):
    eps = 1e-10
    n   = len(Q)
    i   = Q.index(q) + 1
    v   = 1 if ((l_min % l_step < eps or (l_step - l_min % l_step) < eps) and
                l_min <= 0 <= l_max) else 0
    return (n - i) / (n - 1.0) + v - j


def _density_max(k, m):
    return 1 if k < m else 2 - (k - 1.0) / (m - 1.0)


def _density(k, m, d_min, d_max, l_min, l_max):
    r  = (k - 1.0) / (l_max - l_min)
    rt = (m - 1.0) / (max(l_max, d_max) - min(l_min, d_min))
    return 2 - max(r / rt, rt / r)


def _coverage_max(d_min, d_max, span):
    range_ = d_max - d_min
    if span <= range_:
        return 1

    half = (span - range_) / 2.0
    return 1 - np.power(half, 2) / np.power(0.1 * range_, 2)


def _coverage(d_min, d_max, l_min, l_max):
    range_ = d_max - d_min
    return (1 - 0.5 * (np.power(d_max - l_max, 2) +
                       np.power(d_min - l_min, 2)) / np.power(0.1 * range_, 2))


def _legibility(_l_min, _l_max, _l_step):
    return 1


def _extended(d_min, d_max, m, Q, w, flexible):
    best       = None
    j          = 0
    while True:
        j += 1
        for q in Q:
            sm = _simplicity_max(q, Q, j)
            if best and np.dot(w, (sm, 1, 1, 1)) < best.score:
                return best

            k = 1
            while True:
                k += 1
                dm = _density_max(k, m)
                if best and np.dot(w, (sm, 1, dm, 1)) < best.score:
                    break

                delta = ((d_max - d_min) * j) / ((k + 1) * q)
                z     = int(np.ceil(np.log10(delta))) - 1
                while True:
                    z   += 1
                    step = j * q * np.power(10., z)
                    cm   = _coverage_max(d_min, d_max, step * (k - 1))

                    if best and np.dot(w, (sm, cm, dm, 1)) < best.score:
                        break

                    min_start = np.floor(d_max / step) * j - (k - 1) * j
                    max_start = np.ceil(d_min / step) * j
                    if min_start > max_start:
                        break

                    for start in range(int(min_start), int(max_start) + 1):
                        l_min  = start * (step / j)
                        l_max  = l_min + step * (k - 1)
                        l_step = step

                        s = _simplicity(q, Q, j, l_min, l_max, l_step)
                        c = _coverage(d_min, d_max, l_min, l_max)
                        d = _density(k, m, d_min, d_max, l_min, l_max)
                        l = _legibility(l_min, l_max, l_step)

                        score = np.dot(w, (s, c, d, l))
                        if best and score <= best.score:
                            continue
                        if not flexible and (l_min > d_min or l_max < d_max):
                            continue

                        best = TickResults(score, d_min, d_max, l_min, l_max,
                                           l_step, q, k)


def gen_ticks_extended(d_min, d_max, m=4, Q=(1, 5, 2, 2.5, 4, 3),
                       w=(0.25, 0.2, 0.5, 0.05), flexible=True):
    '''
    Generate tick labels using the algorithm described in:

    "An Extension of Wilkinson’s Algorithm for Positioning Tick Labels on Axes"
        by Justin Talbot, Sharon Lin, Pat Hanrahan, InfoVis 2010.

    Parameters:
        d_min, d_max - axis domain
        m            - density (number of ticks)
        Q            - sequence of nice values to use
        w            - (simplicity, coverage, density, legibility) weights
        flexible     - True if the extreme ticks may be inside or outside the
                       data range; False if the extreme ticks must be outside
                       the data range.
    '''
    return _extended(d_min, d_max, m, Q, w, flexible)
