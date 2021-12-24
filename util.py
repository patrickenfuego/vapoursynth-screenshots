from pathlib import Path
#from typing import Union

import vapoursynth as vs
from vapoursynth import core
import awsmfunc as awf

"""
    UTILITY FUNCTIONS
    Functions common to all files
"""


"""
    Utility function to verify input paths exist
"""

def path_exists(x: PathLike) -> bool:
    if not Path(x).exists():
        raise FileNotFoundError(f"{x} does not exist")
    else:
        return x


"""
    Replaces input extensions with the .lwi suffix for cache files
"""

def replace_extension(files: list) -> tuple:
    cache_files = tuple()
    for f in files:
        extensions = "".join(Path(f).suffixes)
        cache_files = (*cache_files, Path(str(f).replace(extensions, ".lwi")))
    else:
        return cache_files
 
   
"""
    Creates index and vs.VideoNode files using LWLibav
"""


def load_VS_files(lwi_files: tuple, in_files: list):
    clips = tuple()
    for i in range(len(in_files)):
        clip = core.lsmas.LWLibavSource(source=in_files[i], cachefile=lwi_files[i])
        clips = (*clips, clip)
    
    return clips

"""
    Add frame info to screenshots
"""


def frame_info(clips: tuple, titles: Union[str, tuple]) -> list:
    ret_clips = list()
    for c in range(len(clips)):
        clip = awf.FrameInfo(clips[i], titles[i])
        ret_clips.append(clip)
    
    return ret_clips
