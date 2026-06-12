import numpy as np
import matplotlib.pyplot as plt

x = np.array([62, 95, 83, 100, 72, 71, 55, 85, 67, 75])   # english
y = np.array([62, 80, 85, 95, 58, 76, 52, 84, 67, 71])    # math

plt.scatter(x,y,color="blue",label="score")

p = np.polyfit(x,y,1)
f = np.poly1d(p)

plt.plot(x , f(x) , color="r" , label="lsm")
plt.xlabel("english")
plt.ylabel("math")
plt.legend(loc="upper left")

plt.show()