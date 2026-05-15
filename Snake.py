import numpy as np

# 定义目标函数
def objective_function(x):
    return 0.04811 * x[2] * x[3] * (x[1] ** 2 + 14) + 1.10471

# 定义约束条件函数
def constraint1(x):
    return x[0] - x[3]

def constraint2(x):
    return 6 - x[0] * x[2]

def constraint3(x):
    return x[1] - x[4]

def constraint4(x):
    return x[4] - 13.600

def constraint5(x):
    return x[2] - 0.25

# 初始化蛇群
def initialize_snakes(num_snakes, num_dimensions, bounds):
    snakes = []
    for _ in range(num_snakes):
        snake = np.random.uniform(bounds[:, 0], bounds[:, 1])
        snakes.append(snake)
    return np.array(snakes)

# 更新蛇的位置和方向
def update_snakes(snakes, alpha, bounds):
    new_snakes = snakes + alpha * np.random.uniform(-1, 1, size=snakes.shape)
    new_snakes = np.clip(new_snakes, bounds[:, 0], bounds[:, 1])
    return new_snakes

# 蛇优化算法
def snake_optimization(num_iterations, num_snakes, num_dimensions, bounds):
    snakes = initialize_snakes(num_snakes, num_dimensions, bounds)
    best_solution = None
    best_fitness = float('inf')

    for iteration in range(num_iterations):
        # 更新蛇的位置和方向
        snakes = update_snakes(snakes, 0.1, bounds)

        # 计算每条蛇的适应度
        fitness_values = [objective_function(snake) for snake in snakes]

        # 更新最优解
        min_index = np.argmin(fitness_values)
        if fitness_values[min_index] < best_fitness:
            best_solution = snakes[min_index]
            best_fitness = fitness_values[min_index]

        print("Iteration:", iteration+1, "Best Fitness:", best_fitness)

    return best_solution, best_fitness

# 设置算法参数和变量边界
num_iterations = 100
num_snakes = 20
num_dimensions = 5

bounds = np.array([[0, None], [0, None], [0, None], [0, None], [0, None]])

# 运行蛇优化算法
best_solution, best_fitness = snake_optimization(num_iterations, num_snakes, num_dimensions, bounds)

print("Optimal Solution:", best_solution)
print("Optimal Objective Value:", best_fitness)
