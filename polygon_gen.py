import argparse
import json
import math

import numpy
from scipy import interpolate

# parse args
ap = argparse.ArgumentParser()
ap.add_argument(
    '-i', '--input', help='input json file', type=str, required=True)
ap.add_argument(
    '-o', '--output', help='output json file', type=str, default='mesh.json')
ap.add_argument(
    '-a',
    '--alpha',
    help='alpha value (for branch width)',
    type=float,
    default=0.0008)
ap.add_argument(
    '-b',
    '--beta',
    help='beta value (for branch fluctuation)',
    type=float,
    default=0.25)
ap.add_argument(
    '-c',
    '--gamma',
    help='gamma value (for branch length)',
    type=float,
    default=0.4)
ap.add_argument('-r', '--rep', help='recursive count', type=int, default=3)
ap.add_argument(
    '-ir',
    '--inner_circle_ratio',
    help='ratio of inner circle area',
    type=float,
    default=0.8)
ap.add_argument(
    '-bd',
    '--branch_div',
    help='control resolution of branches',
    type=int,
    default=100)
ap.add_argument(
    '-nd',
    '--central_node_div',
    help='controle resolution of central node',
    type=int,
    default=50)
args = ap.parse_args()


class BranchPoint:

    def __init__(self, x, y, w, v):
        self.x = x  # x-coordinate of this point
        self.y = y  # y-coordinate of this point
        self.w = w  # a width of a branch at this point
        self.v = v  # a value of the co-occurrence metric


def separate_values(values, thres):
    sub1 = []
    sub2 = []
    for val in values:
        if (val < thres):
            sub1.append(val)
        else:
            sub2.append(val)
    return sub1, sub2


def unit_norm_vec(pos_s, pos_e):
    dx = pos_e[0] - pos_s[0]
    dy = pos_e[1] - pos_s[1]
    dist = math.sqrt(dx * dx + dy * dy)
    if (dist == 0):
        dist = 1e-10
    return [-dy / dist, dx / dist]


def gen_branch_points(values, point_s, point_e, alpha, beta, rep):
    '''
    values: values of the co-occurence metric
    point_s: a start branch point
    point_e: an end branch point
    rep: a recursion repetation count
    '''

    # calc vector u in L-System (Fig.2 in the paper)
    sd = 0.0
    if (len(values) != 0):
        sd = numpy.std(values)

    unit_norm = unit_norm_vec([point_s.x, point_s.y], [point_e.x, point_e.y])
    u = list(map(lambda x: beta * sd * x, unit_norm))
    if (rep % 2 == 1):
        u = list(map(lambda x: -1 * x, u))

    # calc middle point M of between point_s and point_e
    pm_x = (point_s.x + point_e.x) * 0.5 + u[0]
    pm_y = (point_s.y + point_e.y) * 0.5 + u[1]
    vm = (point_s.v + point_e.v) * 0.5
    sub_val1, sub_val2 = separate_values(values, vm)
    # wm = alpha * float(len(sub_val2))
    wm = point_s.w - alpha * float(len(sub_val1))

    point_m = BranchPoint(pm_x, pm_y, wm, vm)

    if (rep == 0): return [point_m]

    return gen_branch_points(
        sub_val1, point_s, point_m, alpha, beta, rep - 1) + gen_branch_points(
            sub_val2, point_m, point_e, alpha, beta, rep - 1)


def gen_interp_branch_points(points, div):
    result = []
    x, y, dist, w = [], [], [], []

    for point in points:
        x.append(point.x)
        y.append(point.y)
        dist.append(math.sqrt(point.x * point.x + point.y * point.y))
        w.append(point.w)

    fx = interpolate.interp1d(dist, x, kind="cubic")
    fy = interpolate.interp1d(dist, y, kind="cubic")
    fw = interpolate.PchipInterpolator(dist, w)

    dist_min = min(dist)
    dist_max = max(dist)
    new_dist = []
    for i in range(0, div + 1):
        dist_i = dist_min + (dist_max - dist_min) * i / float(div)
        if (dist_i > dist_max):
            dist_i = dist_max
        new_dist.append(dist_i)
    new_x = fx(new_dist)
    new_y = fy(new_dist)
    new_w = fw(new_dist)

    for (xi, yi, wi) in zip(new_x, new_y, new_w):
        result.append(BranchPoint(xi, yi, wi, float('nan')))
    return result


def is_counter_clock_order(pos1, pos2, pos3):
    result = False
    if (pos1[0] * pos2[1] - pos2[0] * pos1[1] + pos2[0] * pos3[1] -
            pos3[0] * pos2[1] + pos3[0] * pos1[1] - pos1[0] * pos3[1] > 0):
        result = True
    return result


def gen_branch_meshes(points):
    meshes = []
    if (len(points) >= 2):
        un_s = unit_norm_vec([points[0].x, points[0].y], [0.0, 0.0])
        un_e = unit_norm_vec([0.0, 0.0], [points[0].x, points[0].y])

        for i in range(0, len(points) - 1):
            pt_s = points[i]
            pt_e = points[i + 1]
            if (i > 0):
                un_s = unit_norm_vec([pt_s.x, pt_s.y],
                                     [points[i - 1].x, points[i - 1].y])

            un_e = unit_norm_vec([pt_e.x, pt_e.y], [points[i].x, points[i].y])

            p1 = [
                pt_s.x + 0.5 * pt_s.w * un_s[0],
                pt_s.y + 0.5 * pt_s.w * un_s[1], 0.0
            ]
            p2 = [
                pt_s.x - 0.5 * pt_s.w * un_s[0],
                pt_s.y - 0.5 * pt_s.w * un_s[1], 0.0
            ]
            p3 = [
                pt_e.x - 0.5 * pt_e.w * un_e[0],
                pt_e.y - 0.5 * pt_e.w * un_e[1], 0.0
            ]
            p4 = [
                pt_e.x + 0.5 * pt_e.w * un_e[0],
                pt_e.y + 0.5 * pt_e.w * un_e[1], 0.0
            ]

            if (is_counter_clock_order(p1, p2, p3)):
                meshes += [
                    p1[0], p1[1], p1[2], p2[0], p2[1], p2[2], p3[0], p3[1],
                    p3[2]
                ]
            else:
                meshes += [
                    p3[0], p3[1], p3[2], p2[0], p2[1], p2[2], p1[0], p1[1],
                    p1[2]
                ]

            if (is_counter_clock_order(p3, p4, p1)):
                meshes += [
                    p3[0], p3[1], p3[2], p4[0], p4[1], p4[2], p1[0], p1[1],
                    p1[2]
                ]
            else:
                meshes += [
                    p1[0], p1[1], p1[2], p4[0], p4[1], p4[2], p3[0], p3[1],
                    p3[2]
                ]

    return meshes


def gen_central_node_meshes(r, div):
    meshes = []
    unit_angle = 2.0 * math.pi / float(div)

    prevPos = [0.0, 0.0, 0.0]
    for i in range(0, div + 1):
        x = r * math.cos(unit_angle * i)
        y = r * math.sin(unit_angle * i)
        z = 0.0
        meshes += [0.0, 0.0, 0.0, prevPos[0], prevPos[1], prevPos[2], x, y, z]
        prevPos = [x, y, z]
    return meshes


def output_polygon_json(in_json, out_json, alpha, beta, gamma, rep,
                        inner_circle_ratio):
    """
    in_json: input json file
    out_json: output json file
    alpha: a parameter for width of branches
    beta: a parameter for a vector u which produces fluctuation
    gamma: a parameter for unit length for a value v of co-occurence metric
    rep: a recursion count
    """
    with open(in_json, 'r') as f:
        dataset = json.load(f)

        # obtain these lists as a result
        meshes_list = []
        mesh_categories_list = []
        num_meshes_each_branch = 0
        category_to_name = {}
        central_node_category = 0
        central_node_meshes = []
        central_node_mesh_categories = []

        # calculate radius of the center node and an angle assigned for one item
        total_n = 0
        for data in dataset:
            if (data['type'] == "branch"):
                total_n += len(data['values'])

        r = alpha * float(total_n) / (2.0 * math.pi)
        unit_angle = 2.0 * math.pi / float(total_n)

        angle = 0
        prev_n = 0
        for (idx, data) in enumerate(dataset):
            category_to_name[str(idx)] = data['name']

            if (data['type'] == "branch"):
                # calculate point_s and point_e
                n = len(data['values'])
                angle += float(prev_n + n) * 0.5 * unit_angle
                prev_n = n

                branch_length = gamma * max(data['values'])
                point_s = BranchPoint(r * math.cos(angle), r * math.sin(angle),
                                      alpha * float(n), 0.0)
                point_e = BranchPoint((r + branch_length) * math.cos(angle),
                                      (r + branch_length) * math.sin(angle),
                                      alpha * 1.0, max(data['values']))

                # generate branch points
                branch_points = [point_s] + gen_branch_points(
                    data["values"], point_s, point_e, alpha, beta,
                    rep) + [point_e]

                # generate branch meshes
                interp_branch_points = gen_interp_branch_points(
                    branch_points, args.branch_div)
                meshes = gen_branch_meshes(interp_branch_points)
                meshes_list += meshes
                num_meshes_each_branch = int(len(meshes) / 9)
                mesh_categories_list += [idx] * num_meshes_each_branch
            else:
                # genrate center node meshes
                # TODO: need to find better way to fullfill the blank space
                central_node_category = idx
                central_node_meshes = gen_central_node_meshes(
                    r * 1.5, args.central_node_div)
                central_node_mesh_categories = [idx] * int(
                    len(central_node_meshes) / 9)

        # add center node meshes at last
        meshes_list += central_node_meshes
        mesh_categories_list += central_node_mesh_categories

        # add inner circle meshes for central node
        if (inner_circle_ratio > 0.0):
            inner_circle_meshes = gen_central_node_meshes(
                inner_circle_ratio * r * 1.5, args.central_node_div)
            meshes_list += inner_circle_meshes
            mesh_categories_list += [-1] * int(len(inner_circle_meshes) / 9)

    # output results
    # reduce precision in order to reduce file size (6 significant digits)
    meshes_list = list(
        map(lambda x: float(format(x, '.5g').replace("'", "")), meshes_list))
    out_data = {
        "categoryToName": category_to_name,
        "centralNodeCategory": central_node_category,
        "numMeshesForEachBranch": num_meshes_each_branch,
        "meshes": meshes_list,
        "meshCategories": mesh_categories_list
    }
    with open(out_json, 'w') as f:
        json.dump(out_data, f, indent=4)


output_polygon_json(args.input, args.output, args.alpha, args.beta, args.gamma,
                    args.rep, args.inner_circle_ratio)
