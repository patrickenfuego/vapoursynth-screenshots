import vapoursynth as vs
from vapoursynth import core

def rekt_fast(src, fun=lambda x: x, left=0, top=0, right=0, bottom=0):
    '''Creates a rectangular "mask" in which a fix is applied to only the masked area.
    This vastly speeds up filters like anti-aliasing and scaling.
    This wrapper works with a lambda function called m, which is applied to the "m" clip later on:

    rekt_fast(src, fun=lambda m: taa.TAAmbk(m, aatype=3, preaa=-1, strength=-1, mtype=2), left=2, right=8, top=10, bottom=2)

    Results in the following function being applied to only the masked rectangle:

    def f(m):
        return taa.TAAmbk(m, aatype=3, preaa=-1, strength=-1, mtype=2)'''
    m = core.std.Crop(src, left=left, right=right)
    if left > 0 or right > 0:
        m = fun(m.std.Crop(top=top, bottom=bottom)).std.AddBorders(top=top, bottom=bottom)
        l = core.std.Crop(src, right=src.width - left) if left > 0 else 0
        r = core.std.Crop(src, left=src.width - right) if right > 0 else 0
        params = [x for x in [l, m, r] if x != 0]
        m = core.std.StackHorizontal(params)
    else:
        m = fun(m).std.AddBorders(right=right, left=left)
    if top > 0 or bottom > 0:
        t = core.std.Crop(src, bottom=src.height - top) if top > 0 else 0
        m = core.std.Crop(m, bottom=bottom, top=top)
        b = core.std.Crop(src, top=src.height - bottom) if bottom > 0 else 0
        params = [x for x in [t, m, b] if x != 0]
        m = core.std.StackVertical(params)
    return m
