import vapoursynth as vs
from vapoursynth import core
from rekt import rekt_fast


def rektlvl(c, num, adj_val, type='row', prot_val=[16, 235], min=16, max=235):
    '''
    A rekt_fast version of havsfunc's FixBrightnessProtect2/FixBrightness.
    :param c: Clip to be processed.
    :param num: Row or column number.
    :param adj_val: Adjustment value; negative numbers darken, while positive numbers brighten. Between -100 and 100.
    :param type: Whether a row or a column is to be processed
    :param prot_val: If None, this will work like FixBrightness. If an int, values above 255 - prot_val will not be
                     processed. If list, first int is value below which no processing takes place, second int is same as
                     no list.
    :return: Clip with first plane's values adjusted by adj_val.
    '''
    from vsutil import get_y, plane, scale_value
    core = vs.core
    if (adj_val > 100 or adj_val < -100) and prot_val:
        raise ValueError("adj_val must be between -100 and 100!")
    if c.format.color_family == vs.RGB:
        raise TypeError("RGB color family is not supported by rektlvls.")
    bits = c.format.bits_per_sample

    if c.format.color_family != vs.GRAY:
        c_orig = c
        c = get_y(c)
    else:
        c_orig = None
    if prot_val or prot_val == 0:
        if adj_val > 0:
            expr = f'x {scale_value(16, 8, bits)} - 0 <= {scale_value(16, 8, bits)} {scale_value(235, 8, bits)} {scale_value(adj_val * 2.19, 8, bits)} - {scale_value(16, 8, bits)} - 0 <= 0.01 {scale_value(235, 8, bits)} {scale_value(adj_val * 2.19, 8, bits)} - {scale_value(16, 8, bits)} - ? / {scale_value(219, 8, bits)} * x {scale_value(16, 8, bits)} - {scale_value(235, 8, bits)} {scale_value(adj_val * 2.19, 8, bits)} - {scale_value(16, 8, bits)} - 0 <= 0.01 {scale_value(235, 8, bits)} {scale_value(adj_val * 2.19, 8, bits)} - {scale_value(16, 8, bits)} - ? / {scale_value(219, 8, bits)} * {scale_value(16, 8, bits)} + ?'
        elif adj_val < 0:
            expr = f'x {scale_value(16, 8, bits)} - 0 <= {scale_value(16, 8, bits)} {scale_value(219, 8, bits)} / {scale_value(235, 8, bits)} {scale_value(adj_val * 2.19, 8, bits)} + {scale_value(16, 8, bits)} - * x {scale_value(16, 8, bits)} - {scale_value(219, 8, bits)} / {scale_value(235, 8, bits)} {scale_value(adj_val * 2.19, 8, bits)} + {scale_value(16, 8, bits)} - * {scale_value(16, 8, bits)} + ?'
        else:
            return c_orig
        if isinstance(prot_val, int):
            expr = expr + f' x {scale_value(255 - prot_val, 8, bits)} - -{scale_value(10, 8, bits)} / 0 max 1 min * x x {scale_value(245 - prot_val, 8, bits)} - {scale_value(10, 8, bits)} / 0 max 1 min * +'
        else:
            expr = expr + f' x {scale_value(prot_val[1], 8, bits)} - -{scale_value(10, 8, bits)} / 0 max 1 min * x x {scale_value(prot_val[1], 8, bits)} {scale_value(10, 8, bits)} - - {scale_value(10, 8, bits)} / 0 max 1 min * + {scale_value(prot_val[0], 8, bits)} x - -{scale_value(10, 8, bits)} / 0 max 1 min * x {scale_value(prot_val[0], 8, bits)} {scale_value(10, 8, bits)} + x - {scale_value(10, 8, bits)} / 0 max 1 min * +'
        last = lambda x: core.std.Expr(x, expr=expr)
    else:
        if adj_val < 0:
            last = lambda x: core.std.Levels(x, min_in=scale_value(min, 8, bits), max_in=scale_value(max, 8, bits),
                                             min_out=scale_value(min, 8, bits), max_out=scale_value(max + adj_val, 8, bits))
        elif adj_val > 0:
            last = lambda x: core.std.Levels(x, min_in=scale_value(min, 8, bits), max_in=scale_value(max - adj_val, 8, bits),
                                             min_out=scale_value(min, 8, bits), max_out=scale_value(max, 8, bits))
        else:
            last = lambda x: x
    if type is 'row':
        last = rekt_fast(c, last, bottom=c.height - num - 1, top=num)
    elif type is 'column':
        last = rekt_fast(c, last, right=c.width - num - 1, left=num)
    else:
        raise ValueError("Type must be 'row' or 'column'.")

    if c_orig is not None:
        last = core.std.ShufflePlanes([last, c_orig], planes=[0, 1, 2], colorfamily=c_orig.format.color_family)

    return last


def rektlvls(clip, rownum=None, rowval=None, colnum=None, colval=None, prot_val=[16, 235], min=16, max=235):
    '''
    Wrapper around rektlvl: a rekt_fast version of havsfunc's FixBrightnessProtect2.
    :param clip: Clip to be processed.
    :param rownum: Row(s) to be processed.
    :param rowval: Row adjustment value. Negatives darken, positives brighten. Values can be between -100 and 100.
    :param colnum: Column(s) to be processed.
    :param colval: Column adjustment value. Negatives darken, positives brighten. Values can be between -100 and 100.
    :param prot_val: If None, this will work like FixBrightness. If an int, values above 255 - prot_val will not be
                     processed. If list, first int is value below which no processing takes place, second int is same as
                     no list.
    :return: Clip with first plane's values adjusted by adj_val.
    '''
    if rownum is not None:
        if isinstance(rownum, int):
            rownum = [rownum]
        if isinstance(rowval, int):
            rowval = [rowval]
        for _ in range(len(rownum)):
            clip = rektlvl(clip, rownum[_], rowval[_], type='row', prot_val=prot_val, min=min, max=max)
    if colnum is not None:
        if isinstance(colnum, int):
            colnum = [colnum]
        if isinstance(colval, int):
            colval = [colval]
        for _ in range(len(colnum)):
            clip = rektlvl(clip, colnum[_], colval[_], type='column', prot_val=prot_val, min=min, max=max)
    return clip
