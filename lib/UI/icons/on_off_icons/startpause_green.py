import matplotlib
from matplotlib import pyplot as plt
import numpy as np
from numpy import sin, cos, pi

phi = np.linspace(0, 2 * pi, 100)
fig, ax = plt.subplots(1)

a, b = 5, 5
ax.fill(a*sin(phi), a*cos(phi), 'green')
ax.plot(a*sin(phi), a*cos(phi), 'k' '-')

ax.fill([2/3.*cos(pi/6.)*b, -1/3.*cos(pi/6.)*b, -1/3.*cos(pi/6.)*b, 2/3.*cos(pi/6.)*b], [0, b/2., -b/2., 0 ], 'white')
ax.plot([2/3.*cos(pi/6.)*b, -1/3.*cos(pi/6.)*b, -1/3.*cos(pi/6.)*b, 2/3.*cos(pi/6.)*b], [0, b/2., -b/2., 0 ], 'k' '-')

ax.axis('equal')
ax.axis('off')

plt.savefig("StartGreen", dpi=None, facecolor='w', edgecolor='w',
        orientation='portrait', bbox_inches='tight', pad_inches=0, transparent = True)


fig, ax = plt.subplots(1)

a, b = 5, 5
ax.fill(a*sin(phi), a*cos(phi), 'k')
ax.plot(a*sin(phi), a*cos(phi), 'k' '-')

ax.fill([2/3.*cos(pi/6.)*b, -1/3.*cos(pi/6.)*b, -1/3.*cos(pi/6.)*b, 2/3.*cos(pi/6.)*b], [0, b/2., -b/2., 0 ], 'white')
ax.plot([2/3.*cos(pi/6.)*b, -1/3.*cos(pi/6.)*b, -1/3.*cos(pi/6.)*b, 2/3.*cos(pi/6.)*b], [0, b/2., -b/2., 0 ], 'k' '-')

ax.axis('equal')
ax.axis('off')

plt.savefig("StartBlack", dpi=None, facecolor='w', edgecolor='w',
        orientation='portrait', bbox_inches='tight', pad_inches=0, transparent = True)


fig, ax = plt.subplots(1)
a, b, c = 5, 5, 2
ax.fill(5*sin(phi), 5*cos(phi), 'darkred')
ax.plot(a*sin(phi), a*cos(phi), 'k' '-')

ax.fill([b/2.-c, c, c, b/2.-c, b/2.-c], [b/2.,b/2.,-b/2.,-b/2.,b/2.],'white')
ax.fill([-b/2.+c, -c, -c, -b/2.+c, -b/2.+c], [b/2.,b/2.,-b/2.,-b/2.,b/2.],'white')
ax.plot([b/2.-c, c, c, b/2.-c, b/2.-c], [b/2.,b/2.,-b/2.,-b/2.,b/2.],'k' '-')
ax.plot([-b/2.+c, -c, -c, -b/2.+c, -b/2.+c], [b/2.,b/2.,-b/2.,-b/2.,b/2.], 'k' '-')
ax.axis('equal')
ax.axis('off')

plt.savefig("PauseRed", dpi=None, facecolor='w', edgecolor='w',
        orientation='portrait', bbox_inches='tight', pad_inches=0, transparent = True)

fig, ax = plt.subplots(1)
a, b = 5, 5
ax.fill(a*sin(phi), a*cos(phi), 'darkred')
ax.plot(a*sin(phi), a*cos(phi), 'k' '-')

ax.fill([b/2., -b/2., -b/2., b/2., b/2.], [b/2., b/2.,-b/2.,-b/2.,b/2.],'white')
ax.plot([b/2., -b/2., -b/2., b/2., b/2.], [b/2., b/2.,-b/2.,-b/2.,b/2.],'k' '-')

ax.axis('equal')
ax.axis('off')

plt.savefig("StopRed", dpi=None, facecolor='w', edgecolor='w',
        orientation='portrait', bbox_inches='tight', pad_inches=0, transparent = True)


fig, ax = plt.subplots(1)
a, b = 5, 5
ax.fill(a*sin(phi), a*cos(phi), 'k')
ax.plot(a*sin(phi), a*cos(phi), 'k' '-')

ax.fill([b/2., -b/2., -b/2., b/2., b/2.], [b/2., b/2.,-b/2.,-b/2.,b/2.],'white')
ax.plot([b/2., -b/2., -b/2., b/2., b/2.], [b/2., b/2.,-b/2.,-b/2.,b/2.],'k' '-')

ax.axis('equal')
ax.axis('off')

plt.savefig("StopBlack", dpi=None, facecolor='w', edgecolor='w',
        orientation='portrait', bbox_inches='tight', pad_inches=0, transparent = True)
