import argparse
import json
import math

import numpy

import polygon_gen as pg

# parse args
ap = argparse.ArgumentParser()
ap.add_argument('-i',
                '--input',
                help='input json file',
                type=str,
                required=True)
ap.add_argument('-a',
                '--alpha',
                help='alpha value (for branch width)',
                type=float,
                default=0.0008)
ap.add_argument('-c',
                '--gamma',
                help='gamma value (for branch length)',
                type=float,
                default=0.4)
args = ap.parse_args()


def calc_beta_thresholds(in_json, alpha, gamma):
    thresholds = []

    total_n = 0
    with open(in_json, 'r') as f:
        dataset = json.load(f)

        for data in dataset:
            if (data['type'] == "branch"):
                total_n += len(data['values'])
        r = alpha * float(total_n) / (2.0 * math.pi)

        for data in dataset:
            thres = float("inf")
            sd = 0.0
            n = len(data['values'])
            if (n > 0):
                sd = numpy.std(data['values'])

            if (sd > 0.0 and r > 0.0):
                val_max = max(data['values'])
                l = gamma * val_max
                ws = alpha * float(n)
                sub_data1, sub_data2 = pg.separate_values(
                    data['values'], val_max * 0.5)
                wm = alpha * float(len(sub_data1))
                thres = 0.5 * (ws + (0.5 * ws * l / r) - wm) / sd

            thresholds.append(thres)

    return min(thresholds), thresholds


min_thres, thresholds = calc_beta_thresholds(args.input, args.alpha,
                                             args.gamma)

print("minimum thres: ", min_thres)
print("thresholds: ", thresholds)
