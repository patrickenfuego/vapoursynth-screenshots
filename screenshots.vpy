import vapoursynth as vs
from vapoursynth import core
import awsmfunc as awf

from pathlib import Path
from typing import Union
from termcolor import colored
import re
import math
import subprocess
import sys

PathLike = Union[str, Path]


"""
    ARGUMENT PARSING
    
    VS does not have robust argument parsing or direct support for things like argparse,
    so parsing is done manually with as much validation as possible. Everything is
    entered as a string and converted to the proper type at runtime.
    
    Example:
    
        vspipe --arg "source=c:\path\of\source.mkv" --arg "encode=c:\path\of\encode.mkv" --arg "test=True" -
    
    ---- VALID ARGS (Everything else will be ignored) ----
    
    source:         Path to the source file (or primary file)
    encode:         Path to the encode file (or secondary file)
    screenshots:    Optional path to screenshots. If one is not provided, the root of encode will be used
    frames:         A list of frame numbers for screenshots. Passed as a Python list, i.e. "[1,2,3,4]"
    offset:         Frame offset for test encodes
    title:          Title tag for frame info overlay. Applies to encodes
    tonemap_type:   Tonemap algorithm to use (hable, mobius, reinhard). Default is mobius
    exposure:       Gain to apply to source
     
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
    Validate and parse input from global dictionary
"""


def validate_input():
    args = dict()
    for key, value in dict(globals()).items():
        if key == "source":
            try:
                assert path_exists(value), "Source file path does not exist"
            except AssertionError as msg:
                print(msg)
                sys.exit(1)
            args["source"] = Path(value)

        elif key == "encode":
            try:
                assert path_exists(value), "Encode file path does not exist"
            except AssertionError as msg:
                print(msg)
                sys.exit(1)
            args["encode"] = Path(value)

        elif key == "screenshots":
            args["screenshots"] = Path(value)

        elif key == "frames":
            try:
                assert "[" in value and "]" in value, "Frames must be in list format: [1,2,3]"
                frame_convert = value.strip("][").split(",")
            except AssertionError as msg:
                print(msg)
                sys.exit(1)

            args["frames"] = [int(x) for x in frame_convert]

        elif key == "offset":
            try:
                assert isinstance(int(value), int), "offset (in frames) for test encodes must be integers"
                args["offset"] = int(value)
            except AssertionError as msg:
                print(msg)
                sys.exit(1)

        elif key == "title":
            args["title"] = value

        elif key == "tonemap_type":
            value.lower()
            if value in ("hable", "reinhard", "mobius"):
                args["tonemap"] = value.lower()
                print(f"Tonemap value: {value}")
            else:
                print(f"Unknown tonemapping algorithm: {value}. Mobius will be used")
                args["tonemap"] = "mobius"

        elif key == "exposure":
            try:
                assert isinstance(float(value), float), "Exposure must be a float. Setting default: 4.0"
                args["exposure"] = float(value)
            except AssertionError as msg:
                print(msg)
                args["exposure"] = 4.5

        else:
            pass

    return args


"""
   --------------- Utility functions ---------------
"""

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
    Determines the dimensions and returns them
    using ffprobe
    
    TODO: Verify ffprobe is available via PATH
"""


def get_resolution(path: PathLike, type: str) -> tuple:
    ffprobe = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=width,height",
        "-of",
        "csv=s=x:p=0",
    ]

    regex = re.compile("(\d+)x(\d+)")
    res_str = (
        subprocess.Popen([*ffprobe, path], stdout=subprocess.PIPE, universal_newlines=True).communicate()[0].strip()
    )

    print(f"ffprobe results {type}: {res_str}")
    match = regex.match(res_str)
    width, height = match.group(1, 2)

    return (int(width), int(height))


"""
   --------------- VapourSynth functions ---------------
"""

"""
    Crop the source encode (if needed) based on encode crop values
"""


def crop_src(src: tuple, enc: tuple, clip: vs.VideoNode) -> vs.VideoNode:
    # set reference dimensions
    if enc[0] > 3000:
        full_width, full_height = 3840, 2160
    elif enc[0] <= 1920 and enc[0] > 1280:
        full_width, full_height = 1920, 1080
    elif enc[0] <= 1280:
        full_width, full_height = 1280, 720
    else:
        raise InvalidArgumentException("Unsupported resolution")
    
    #resize if downscale
    if src[0] > full_width:
        clip = clip.resize.Spline36(width=full_width, height=full_height)
        
    # Calculate top, bottom, left, right crop values
    top = bottom = math.ceil((full_height - enc[1]) / 2)
    left = right = math.ceil((full_width - enc[0]) / 2)

    return core.std.Crop(clip, left, right, top, bottom)


"""
    Creates index and vs.VideoNode files using LWLibav
"""


def load_VS_files(lwi_files: tuple, in_files: list, format: str) -> tuple:
    src = core.lsmas.LWLibavSource(source=in_files[0], format=format, cachefile=lwi_files[0])
    enc = core.lsmas.LWLibavSource(source=in_files[1], format=format, cachefile=lwi_files[1])

    return (src, enc)


"""
    Tonemap screenshots based on input and exposure
    Default algorithm: mobius
    Default exposure: 4.5
"""


def tonemap(clips: tuple, res: tuple, tonemap: str, exposure=4.5) -> tuple:
    tm_clips = tuple()
    for clip in clips:
        clip = core.resize.Spline36(
            clip=clip,
            format=vs.RGBS,
            width=res[0],
            height=res[1],
            matrix_in_s="2020ncl",
            range_in_s="limited",
            transfer_in_s="st2084",
            transfer_s="linear",
            nominal_luminance=1000,
        )

        if tonemap == "hable":
            clip = core.tonemap.Hable(clip=clip, exposure=exposure)
        elif tonemap == "reinhard":
            clip = core.tonemap.Reinhard(clip=clip, exposure=exposure)
        else:
            clip = core.tonemap.Mobius(clip=clip, exposure=exposure)

        clip = core.resize.Spline36(
            clip=clip,
            format=vs.YUV420P10,
            primaries_in_s="2020",
            transfer_in_s="linear",
            transfer_s="709",
            matrix_s="709",
            primaries_s="709",
        )

        tm_clips = (*tm_clips, clip)

    return tm_clips


"""
    Add frame info to screenshots
"""


def frame_info(clips: tuple, title: str) -> tuple:
    src = awf.FrameInfo(clips[0], "Source")
    enc = awf.FrameInfo(clips[1], title)

    return (src, enc)


"""
    Call ScreenGen to generate the screenshots
"""


def take_screenshots(clips: tuple, folder: PathLike, offset: int, frames: list):
    src, enc = clips
    # Set offset for test encodes (if passed)
    if offset != 0:
        oframes = [x + offset for x in frames]
    else:
        oframes = frames
    # Set tags for sorting
    pattern = re.compile("[A-Za-z]")
    chars = list()
    # loop through dir and ensure files are not overwritten
    for f in folder.iterdir():
        if f.suffix in (".jpg", ".jpeg", ".png"):
            char = ord(re.search(pattern, f.name)[0])
        else:
            char = None
        if char is not None and char not in chars:
            chars.append(char)

    if len(chars) > 0:
        chars.sort()
        # Convert back to char and increment to avoid overwriting
        tags = (chr(chars[-2] + 2), chr(chars[-1] + 2))
    else:
        tags = ("a", "b")

    awf.ScreenGen(src, folder, tags[0], frame_numbers=oframes)
    awf.ScreenGen(enc, folder, tags[1], frame_numbers=frames)


"""
   Main Script Logic
"""

args = validate_input()
print(args)

# Get resolution of source and encode.
src_res = get_resolution(args["source"], type="Source")
enc_res = get_resolution(args["encode"], type="Encode")

# Create LWI filepaths
lwi_paths = replace_extension([args["source"], args["encode"]])
# Set screenshot path. If no path is specified, use root of encode
screenshots = Path(args["encode"]).parent / "screens" if "screenshots" not in args else Path(args["screenshots"])
print(f"Screenshots directory: '{screenshots}'")

# Get bit depth based on source resolution
format = "YUV420P10" if src_res[0] > 3000 else "YUV420P8"
print(f"Pixel format: {format}")

# Load clip files
src, enc = load_VS_files(lwi_paths, [args["source"], args["encode"]], format)
# Crop source & resize if downscale
src = crop_src(src_res, enc_res, src)
# tonemap if UHD
if format == "YUV420P10":
    tonemap_algo = args["tonemap"].lower() if "tonemap" in args else "mobius"
    exposure = args["exposure"] if "exposure" in args else 4.5
    src, enc = tonemap(clips=(src, enc), res=enc_res, tonemap=tonemap_algo, exposure=exposure)

# Generate frame info
title = "Encode" if "title" not in args else args["title"]
src, enc = frame_info(clips=(src, enc), title=title)

# Finally...screenshots
offset = 0 if "offset" not in args else args["offset"]
take_screenshots(clips=(src, enc), folder=screenshots, offset=offset, frames=args["frames"])
