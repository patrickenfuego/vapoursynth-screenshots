import vapoursynth as vs
from vapoursynth import core
from rekt import rekt_fast

def rektaa(clip, left=0, top=0, right=0, bottom=0, aatype=3, aatypeu=None, aatypev=None, preaa=0, strength=0, cycle=0,
           mtype=None, mclip=None, mthr=None, mthr2=None, mlthresh=None, mpand=(1, 0), txtmask=0, txtfade=0, thin=0,
           dark=0.0, sharp=0, aarepair=0, postaa=None, src=None, stabilize=0, down8=True, showmask=0, opencl=False, 
           opencl_device=0):
    '''Anti-aliasing alias for fast_rekt with vsTAAmbk.'''
    import vsTAAmbk as taa
    return rekt_fast(clip, left=left, right=right, top=top, bottom=bottom, fun=lambda x: taa.TAAmbk(x, aatype=aatype, 
                                                  aatypeu=aatypeu, aatypev=aatypev, preaa=preaa,
                                                  strength=strength, cycle=cycle, mtype=mtype, mclip=mclip,
                                                  mthr=mthr, mthr2=mthr2, mlthresh=mlthresh, mpand=mpand,
                                                  txtmask=txtmask, txtfade=txtfade, thin=thin, dark=dark, sharp=sharp,
                                                  aarepair=aarepair, postaa=postaa, src=src, stabilize=stabilize,
                                                  down8=down8, showmask=showmask, opencl=opencl,
                                                  opencl_device=opencl_device))
