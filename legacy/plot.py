import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Define the objective function f(x)
def f(x):
    return 0.04811 * x[2] * x[3] * (x[1]**2 + 14) + 1.10471 * x[0]**2 * x[1]

# Define the variable ranges
x1 = np.linspace(0.1, 2, 100)  # x1 range
x2 = np.linspace(0.1, 10, 100)   # x2 range
x3 = np.linspace(0.1, 10, 100)   # x3 range
x4 = np.linspace(0.1, 2, 100)    # x4 range

# Generate the Cartesian product of the variable ranges
X1, X2, X3, X4 = np.meshgrid(x1, x2, x3, x4, indexing='ij')

# Calculate the function values for each point on the grid
Z = f([X1, X2, X3, X4])

# Create constraint functions
def constraint1(xs):
    return xs[..., 0] - xs[..., 3]

def constraint2(xs):
    return 2.1952 / (xs[..., 2]**3 * xs[..., 3]) - 0.25

def constraint3(xs):
    return (4.013 * 30 * 10**6 * xs[..., 2] * xs[..., 3]**3) * (1 - xs[..., 2] / (28 * np.sqrt((30 * 10**6) / (48 * 10**6)))) / (6 * 14**2) - 6000

def constraint4(xs):
    R = np.sqrt(xs[1] ** 2 * 0.25 + ((xs[0] + xs[2]) * 0.5) ** 2)
    M = 6000 * (xs[1] * 0.5 + 14)
    J = 2 * (np.sqrt(2) * xs[0] * xs[1] * ((xs[1] ** 2 / 12) + (xs[0] + xs[2] / 2) ** 2))
    T = 6000 / (np.sqrt(2) * xs[0] * xs[1])
    return (np.sqrt(T ** 2 + (R * M / J) ** 2 + 2 * T * R * M / J * xs[1] / 2 / R)) - 13600

def constraint5(xs):
    return 504000 / (xs[..., 3] * xs[..., 2]**2) - 30000

def constraint6(xs):
    return xs[..., 0] - 0.125

def constraint7(xs):
    return 0.10471 * xs[..., 0]**2 + 0.04811 * xs[..., 2] * xs[..., 3] * (xs[..., 1] + 14) - 5

# Calculate the constraint values for each point on the grid
C1 = constraint1(np.array([X1, X2, X3, X4]))
C2 = constraint2(np.array([X1, X2, X3, X4]))
C3 = constraint3(np.array([X1, X2, X3, X4]))
C4 = constraint4(np.array([X1, X2, X3, X4]))
C5 = constraint5(np.array([X1, X2, X3, X4]))
C6 = constraint6(np.array([X1, X2, X3, X4]))
C7 = constraint7(np.array([X1, X2, X3, X4]))

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.plot_surface(X1[:, :, 0, 0].squeeze(), X2[:, :, 0, 0].squeeze(), Z[:, :, 0, 0].squeeze(), cmap='viridis')
ax.set_xlabel('x1')
ax.set_ylabel('x2')
ax.set_zlabel('f(x)')
ax.set_title('Function f(x)')

# Calculate the constraint values for each point on the grid
C1_resized = np.resize(C1, X1.shape)
C2_resized = np.resize(C2, X1.shape)
C3_resized = np.resize(C3, X1.shape)
C4_resized = np.resize(C4, X1.shape)
C5_resized = np.resize(C5, X1.shape)
C6_resized = np.resize(C6, X1.shape)
C7_resized = np.resize(C7, X1.shape)


# Plot the constraint regions
ax.voxels(X1[:, :, :, 0], X2[:, :, :, 0], X3[:, :, :, 0], C1_resized[..., np.newaxis] > 0, alpha=0.2)
ax.voxels(X1[:, :, :, 0], X2[:, :, :, 0], X3[:, :, :, 0], C2_resized[..., np.newaxis] > 0, alpha=0.2)
ax.voxels(X1[:, :, :, 0], X2[:, :, :, 0], X3[:, :, :, 0], C3_resized[..., np.newaxis] > 0, alpha=0.2)
ax.voxels(X1[:, :, :, 0], X2[:, :, :, 0], X3[:, :, :, 0], C4_resized[..., np.newaxis] > 0, alpha=0.2)
ax.voxels(X1[:, :, :, 0], X2[:, :, :, 0], X3[:, :, :, 0], C5_resized[..., np.newaxis] > 0, alpha=0.2)
ax.voxels(X1[:, :, :, 0], X2[:, :, :, 0], X3[:, :, :, 0], C6_resized[..., np.newaxis] > 0, alpha=0.2)
ax.voxels(X1[:, :, :, 0], X2[:, :, :, 0], X3[:, :, :, 0], C7_resized[..., np.newaxis] > 0, alpha=0.2)

plt.show()

