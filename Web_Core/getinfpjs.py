import matplotlib.pyplot as plt


x = []
y = []
z = []

for i in range(5):
    for j in range(5):
        for k in range(5):
            x.append(i)
            y.append(j)
            z.append(k)

fir = plt.figure(figsize=(10, 10))
ax = fir.add_subplot(projection = '3d')


for i in range(0, 4, 1):
     for j in range(4):
         for k in range(4):
             ax.plot([i, i+1],[j, j], [k, k])
             if  i > 0:
                 ax.plot([i, i],[j, j], [k, k+ 1])
                 ax.plot([i, i],[j, j+1], [k, k])


for i in range(0, 4, 1):
     for j in range(4):
         for k in range(4):
             ax.plot([i, i+1],[j, j+1], [k, k+1])
             if k > 0:
                 ax.plot([i, i+1],[j, j+1], [k, k-1])
             if i>0:
                 ax.plot([i, i-1],[j, j+1], [k, k+1])
             if i>0 and j > 0 and k > 0:
                 ax.plot([i, i-1],[j, j-1], [k, k+1])

plt.show()


