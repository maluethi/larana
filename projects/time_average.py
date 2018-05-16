import numpy as np
from lmfit.models import GaussianModel

res = np.load('/home/matthias/workspace/larana/projects/out/time-histo/histo-more-maxima.npy')

# Sort the input
srt = np.argsort(res[:,3])
res = res[srt]

maximas = np.concatenate(res[:,0], axis=1)
error = np.concatenate(res[:,2], axis=1)

print(maximas[0])

# Get the 2-D Histogram and calculate the average over the full timescale
w = np.arange(0,3456)
b = np.ones(maximas.shape)
x = np.transpose(w * b.T)


xedges = np.arange(0,3456,1)
yedges = np.arange(0,300,1)

H, xedges, yedges = np.histogram2d(x.flatten(), maximas.flatten(), bins=(xedges, yedges))

cen = np.zeros(H.shape[0])
wid = np.zeros(H.shape[0])

x = yedges[:-1]
for idx, y in enumerate(H):
    print("{}/{}".format(idx, xedges[-1]))
    maxarg = np.max(y)
    if maxarg < 100:
        cen[idx] = np.inf
        wid[idx] = np.inf
    else:
        mod = GaussianModel()
        pars = mod.guess(y, x=x)
        result = mod.fit(y, pars, x=x)

        if result.params['center'] < 0 or result.params['sigma'] > 20:
            cen[idx] = np.inf
            wid[idx] = np.inf
        else:
            cen[idx] = result.params['center']
            wid[idx] = result.params['sigma']

np.savez('./out/time-histo/time-mean.npz', cen=cen, wid=wid)