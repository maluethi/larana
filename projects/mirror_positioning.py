from scipy.optimize import curve_fit
import matplotlib.pyplot as plt


laser_pos = [120., 8., 1070.]
drift_speed = 0.11  # cm/us

w = [714, 758, 807, 856]
t = [3273, 3338, 3368, 3398]

z = [0.3 * e for e in w]
x = [(e - 3200) * 0.5 * drift_speed for e in t]
print(x)

def f(x, A, B): # this is your 'straight line' y=f(x)
    return A*x + B

A,B = curve_fit(f, z, t)[0] # your data x, y to fit

print(A, B)
print(f(1036, A,B))


plt.plot(w,t)
plt.show()