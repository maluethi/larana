import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.cm as cm
from mpl_toolkits.axes_grid1 import make_axes_locatable


# slice definitions
wire_start = 50
wire_end = 3455
step = 1000

cross_wires = [w for w in range(wire_start, wire_end, step)]

print(cross_wires)

corr_scan_width = 500

offsets = [dist for dist in range(-corr_scan_width,corr_scan_width+1)]

# cmap stuff
cmap = cm.get_cmap('viridis')
norm = mpl.colors.Normalize(vmin=-corr_scan_width, vmax=corr_scan_width+1)
cm = cm.ScalarMappable(norm=norm, cmap=cmap)

# read the data
res = np.load('/home/matthias/workspace/larana/projects/out/time-histo/histo-more-maxima.npy')
df =  np.load('./out/time-histo/time-mean.npz')

wid = df['wid']
cen = df['cen']

# Sort the input
srt = np.argsort(res[:,3])
res = res[srt]

maximas = np.concatenate(res[:,0], axis=1)
amp = np.concatenate(res[:,1], axis=1).T
error = np.concatenate(res[:,2], axis=1)

# Get the 2-D Histogram and calculate the average over the full timescale
w = np.arange(0,3456)
b = np.ones(maximas.shape)
x = np.transpose(w * b.T)

xedges = np.arange(0,3456,1)
yedges = np.arange(0,300,1)

# now we get the 2D histo
H, xedges, yedges = np.histogram2d(x.flatten(), maximas.flatten(), bins=(xedges, yedges))

# make 2D histogrtam plot
fig = plt.figure()
ax = fig.add_subplot(111)

im = mpl.image.NonUniformImage(ax, interpolation='bilinear')
xcenters = xedges[:-1] + 0.5 * (xedges[1:] - xedges[:-1])
ycenters = yedges[:-1] + 0.5 * (yedges[1:] - yedges[:-1])

im.set_data(xcenters, ycenters, H.T)
ax.images.append(im)
ax.set_xlim(xedges[0], xedges[-1])
ax.set_ylim(yedges[0], yedges[-1])
plt.colorbar(im)

# plot the averaged values
plt.errorbar(xedges[1:], cen, yerr=wid, fmt='o')

ax.vlines(cross_wires, 0, 1000)

plt.show()


# Based on the average, filter outliers (few ticks) in individual tracks
# subtract avataged values per wire
max_redu = maximas[:-1,:].T - cen

# exclude everything that has a too high derivative
mask = np.abs(np.diff(max_redu)) > 0.5
mask = np.insert(mask, 0, True, axis=1)

# too big values are not good as well
max = np.abs(max_redu) > 15

# construct the final mask
mask = np.logical_or(mask, max)
max_redu[mask] = np.inf

# lets save this work for other use
np.savez('./out/time-histo/histo-more-maxima-cleaned', max=max_redu)
print("saved cleaned version")

#max
maxs = []
argmaxs = []

# loop over wire range
for idx, cross_wire in enumerate(cross_wires):
    print("processing: {}/{}".format(idx, len(cross_wires)))

    ap = amp[:, cross_wire]
    y = max_redu[:, cross_wire]
    idx = np.isfinite(y)
    x = np.arange(0, y.shape[0], 1)

    y_slice = max_redu[:, cross_wire - 1]
    idx_slice = np.isfinite(y_slice)

    #max
    max_corrs = []
    argmax_corrs = []


    try:
        pol_this = np.polyfit(x[idx_slice], y_slice[idx_slice], 16)
        #ax[0].plot(x, i + np.polyval(pol_this, x), 'x-')
    except:
        print('fail')


    for dist in offsets:
        # handle edge cases
        if (cross_wire - dist) < 0 or (cross_wire - dist) >= xedges[-1]:
            continue

        y_slice = max_redu[:, cross_wire - dist]
        idx_slice = np.isfinite(y_slice)
        try:
            pol_corr = np.polyfit(x[idx_slice], y_slice[idx_slice], 16)
            corr = np.correlate(np.polyval(pol_this, x), np.polyval(pol_corr, x), 'full')
            argmax_corr = np.argmax(corr) - len(x)
            max_corr = np.max(corr)
        except:
            max_corr = np.inf
            argmax_corr = np.inf


        max_corrs.append(max_corr)
        argmax_corrs.append(argmax_corr)

    maxs.append(max_corrs)
    argmaxs.append(argmax_corrs)

np.savez('./out/time-histo/time-corr.npz', max=maxs, dist=argmaxs, wire=cross_wires)

fig, ax = plt.subplots(2, 1)
ax[0].set_title('wire {}'.format(0))
ax[1].scatter(argmaxs[0], maxs[0], c=cm.to_rgba(offsets), alpha=0.3)
ax[0].plot(x, y, '*')
ax[0].plot(x, y_slice, '*')
ax[1].axvline(len(x))
plt.show()


