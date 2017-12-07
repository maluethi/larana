
import numpy as np
import matplotlib.pyplot as plt


def opening_ang(x, d, l):
    phi1 = np.arctan(x/l)
    phi2 = np.arctan((d-x)/l)
    return phi1 + phi2

d = 100
l = 107.7

y_2 = np.arange(0,101,1)

angs = np.abs(np.rad2deg(opening_ang(y_2, d , l)))
plt.plot( angs, y_2 )

plt.show()