import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

# x = []
# y = []
# z = []
# for i in range(5):
#     for j in range(5):
#         for k in range(5):
#             x.append(i)
#             y.append(j)
#             z.append(k)

fir = plt.figure(figsize=(10, 10))
ax = fir.add_subplot(projection = '3d')


# for i in range(0, 4, 1):
#     for j in range(4):
#         for k in range(4):
#             ax.plot([i, i+1],[j, j], [k, k])
#             if  i > 0:
#                 ax.plot([i, i],[j, j], [k, k+ 1])
#                 ax.plot([i, i],[j, j+1], [k, k])

# for i in range(0, 4, 1):
#     for j in range(4):
#         for k in range(4):
#             ax.plot([i, i+1],[j, j+1], [k, k+1])
#             if k > 0:
#                 ax.plot([i, i+1],[j, j+1], [k, k-1])
#             if i>0:
#                 ax.plot([i, i-1],[j, j+1], [k, k+1])
#             if i>0 and j > 0 and k > 0:
#                 ax.plot([i, i-1],[j, j-1], [k, k+1])

x, y, z = 10, 11, 1
x1, y1, z1 = 9, 9, 9

distance_vector = np.array([x - x1, y - y1, z - z1])
length_distance_vector = np.linalg.norm(distance_vector)
k = 3 / length_distance_vector

project_x = (x - x1) * k
project_y = (y - y1) * k
project_z = (z - z1) * k

plt.plot((0, project_x), (0, project_y), (0, project_z))
plt.plot((0, x - x1), (0, y - y1), (0, z - z1), 'r--')
plt.show()




ax1 = 3 + project_x
ax2 = 3 + project_y
ax3 = 3 + project_z



