import math

def aim_function(xs):
    return 0.04811 * xs[2] * xs[3] * (xs[1] + 14) + 1.10471 * xs[0] ** 2 * xs[1]

# 定义约束条件函数
def constraint1(xs):
    return xs[0] - xs[3]

def constraint2(xs):
    return 2.1952/(xs[2]**3 * xs[3]) - 0.25

def constraint3(xs):
    return 6000 - ((4.013 * 30 * 10**6 * xs[2] * xs[3]**3) * (1 - xs[2] / 28 * math.sqrt((30 * 10**6)/(48 * 10**6)))/(6 * 14**2))


def constraint4(xs):
    R = math.sqrt(xs[1] ** 2 * 0.25 + ((xs[0] + xs[2]) * 0.5) ** 2)
    M = 6000 * (xs[1] * 0.5 + 14)
    J = 2 * (math.sqrt(2) * xs[0] * xs[1] * ((xs[1] ** 2 / 12) + ((xs[0] + xs[2]) / 2) ** 2))
    T = 6000 / (math.sqrt(2) * xs[0] * xs[1])
    return (math.sqrt(T ** 2 + (R * M / J) ** 2 + 2 * T * (R * M / J) * xs[1] / (2 * R))) - 13600

def constraint5(xs):
    return 504000/(xs[3] * xs[2]**2) - 30000

def constraint6(xs):
    return xs[0] - 0.125

def constraint7(xs):
    return (0.10471 * xs[0]**2 + 0.04811 * xs[2] * xs[3] * (xs[1] + 14) - 5)

if __name__ == '__main__':
    xs = [0.205986, 3.471328, 9.020224, 0.206480]
    print(aim_function(xs))
    print(constraint1(xs))
    print(constraint2(xs))
    print(constraint3(xs))
    print(constraint4(xs))
    print(constraint5(xs))