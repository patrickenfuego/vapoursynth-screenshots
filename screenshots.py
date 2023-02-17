#!/usr/bin/env python3

"""
Take wonderful screenshots using VapourSynth.

This script utilizes VapourSynth to generate comparison screenshots for encoding. The script will
overlay frame info (frame count, frame type, etc.) unless specified otherwise via the
`--no_frame_info` flag.

You can pass the script a series of specific frames, or generate random frames using the
`--random_frames` argument. When comparing test encodes to the source, use the `--offset`
argument to specify a frame offset from the source so screenshots are properly aligned. If the source
is HDR/DoVi/HDR10+, the screenshots are automatically tonemapped.

Each screenshot is tagged with an alphabet character to distinguish which video it corresponds to;
for example, source screens will be '1a.png', '2a.png', encode 1 screens will be '1b.png', '2b.png',
etc. When existing screenshots are detected, the alphabet characters are incremented to prevent
overwriting if the new ones are saved to an existing directory.

--- EXAMPLES ---

Generate screenshots for test encodes with an offset of 2000 frames::

    python screenshots.py 'C:\Path\src.mkv' --encodes 'C:\Path\t1.mkv' 'C:\Path\t2.mkv' --offset 2000

Generate 25 random screenshotS ranging from frame 100-25000::

    python screenshots.py 'C:\Path\src.mkv' --encodes 'C:\Path\t1.mkv' --random_frames 100 25000 25

Specify an input directory containing encode files::

    python screenshots.py '~/Ex Machina 2014/ex_machina_src.mkv' --input_directory '~/Ex Machina 2014'

Use `--help` for the full list of options.

"""

import vapoursynth as vs
import awsmfunc as awf

import argparse
import re
import random
from pathlib import Path
from pprint import pformat

from modules import (
    path_exists,
    verify_resize,
    load_clips,
    prepare_clips
)

core = vs.core


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            'CLI script for generating comparison screenshots using VapourSynth. '
            'The script can accept a variable amount of clips to process and will '
            'automatically generate frame info overlays unless instructed otherwise. '
            'Oh yeah, it automatically tonemaps HDR clips, too!'
        ),
        epilog='View module created by UniversalAI, awsmfunc created by OpusGang. All credit goes to them.'
    )

    parser.add_argument('source', nargs='?', metavar='SOURCE', type=path_exists,
                        help='Path to source file. Required')
    parser.add_argument('--frames', '-f', nargs='+', metavar='FRAMES', type=int,
                        help="Screenshot frames. If running tests, be sure to set '--offset'")
    parser.add_argument('--random_frames', '-r', nargs=3, metavar='RFRAMES', type=int,
                        help="Generate random frames in the form 'start stop count'. If running tests, be sure to set '--offset'")
    parser.add_argument('--offset', '-o', nargs='?', metavar='OFFSET', type=int, default=0,
                        help="Offset (in frames) from source. Useful for comparing test encodes")
    parser.add_argument('--crop', '-c', nargs='+', metavar='CROP', type=int,
                        help='Use custom crop dimensions instead of using the encode dimensions. All files must use the same values')
    parser.add_argument('--encodes', '-e', metavar='ENCODES', type=path_exists, nargs='+',
                        help='Paths to encoded file(s) you wish to compare')
    parser.add_argument('--titles', '-t', metavar='TITLES', type=str, nargs='+',
                        help='ScreenGen titles for files. Should match the order of --encodes')
    parser.add_argument('--input_directory', '-d', metavar='IN_FOLDER', type=path_exists, nargs=1,
                        help='Path to folder containing encoded file(s). Replaces --encodes')
    parser.add_argument('--output_directory', '-od', metavar='OUT_FOLDER', type=Path, nargs='?',
                        help='Path to folder containing encoded file(s). Replaces --encodes')
    parser.add_argument('--resize_kernel', '-k', metavar='KERNEL', type=str, nargs='?', default='spline36',
                        help='Specify kernel used for resizing (if applicable). Default is spline36')
    parser.add_argument('--load_filter', '-lf', type=str, choices=('lsmas', 'ffms2'), default='ffms2',
                        help="Filter used to load & index clips. Default is 'ffms2'")
    parser.add_argument('--no_frame_info', '-ni', action='store_false',
                        help="Don't add frame info overlay to clips. Default behavior is enabled")
    args = parser.parse_args()

    if not args.frames and not args.random_frames:
        raise NameError(
            "No frames were provided. Specify frames via the `--frames` argument or random "
            "frames via the `--random_frames` argument."
        )

    # Try to create output directory if passed. Else, use parent root
    if args.output_directory and not args.output_directory.exists():
        try:
            args.output_directory.mkdir(parents=True)
        except OSError as e:
            print(f"Failed to generate output folder: {e}. Using source root instead")
            args.output_directory = args.source.parent
    else:
        # don't overwrite
        screen_count = sum(1 for d in args.source.parent.iterdir() if d.is_dir() and 'screens' in d.stem)
        args.output_directory = args.source.parent / f'screens t{screen_count + 1}-offset_{args.offset}'
        args.output_directory.mkdir(parents=True, exist_ok=True)

    if not args.encodes and not args.input_directory:
        files = [args.source]
    else:
        files = [args.source, *args.encodes]

    # Making assumption - probably didn't add 'Source' as a title
    if args.titles and len(files) - len(args.titles) == 1:
        args.titles.insert(0, 'Source')
    # Only source passed, no title
    elif not args.titles and len(files) == 1:
        args.titles = ['Source']
    # Set titles to file names if not passed
    elif not args.titles and len(files) > 1:
        names = [str(f.stem) for f in files[1:]]
        args.titles = ['Source', *names]

    return (files,
            args.crop,
            args.titles,
            args.input_directory,
            args.output_directory,
            args.resize_kernel,
            args.no_frame_info,
            args.frames,
            args.random_frames,
            args.offset if args.offset else 0,
            args.load_filter[0] if type(args.load_filter) is list else args.load_filter)


def generate_screenshots(clips: list[vs.VideoNode],
                         folder: Path,
                         frames: list,
                         offset: int = None) -> None:

    """
    Generate screenshots using ScreenGen.
    :param clips: Source and encode clips to process
    :param folder: Output folder for screenshots
    :param frames: Screenshot frames
    :param offset: Frame offset from source. Used for generating test encodes
    :return: Void
    """

    chars = []
    clip_len = len(clips)

    if offset:
        src_frames = [x + offset for x in frames]
    else:
        src_frames = frames

    # Generate tags. Increment chars to prevent overwriting
    for file in folder.iterdir():
        if file.suffix in ('.jpg', '.jpeg', '.png'):
            char = ord(re.search("[A-Za-z]", file.name)[0])
            if char and char not in chars:
                chars.append(char)
    if len(chars) == 0:
        tags = [chr(ord('a') + c) for c in range(0, clip_len)]
    else:
        tags = [chr(c + clip_len) for c in chars]
        if len(tags) < clip_len:
            difference = clip_len - len(tags)
            for i in range(1, difference + 1):
                last = tags[-1]
                tags.append(chr(ord(last) + 1))

    # screenshots for source. Pop src tag to prevent conflict
    awf.ScreenGen(clips[0], folder, tags[0], frame_numbers=src_frames)
    tags.pop(0)
    for i, clip in enumerate(clips[1:]):
        awf.ScreenGen(clip, folder, tags[i], frame_numbers=frames)


def generate_random_frames(clips: list[vs.VideoNode],
                           frame_range: list[int]) -> list[int]:
    """
    Generate random frames for screenshots.

    This function takes input in the form [start, stop, count] to generate sequential
    frames randomly.

    :param clips: Encoded clips. Used to get frame counts where the smallest value is used for stop
    :param frame_range: Frame range and count in the form [start, stop, count]
    :return: A list of random, sequential frames
    """

    # Get the smallest number of frames for all clips
    frame_count = min([c.num_frames for c in clips])
    if frame_range[0] > frame_count:
        raise ValueError("random_frames: Start frame is greater than the smallest clip's end frame.")

    # Handle out-of-bounds errors if stop is greater than frame count
    stop = frame_range[1] if frame_range[1] < frame_count - 5 else frame_count - 5
    rand_frames = random.sample(range(frame_range[0], stop), frame_range[2])
    rand_frames.sort()

    return rand_frames


def main():
    (files,
     crop,
     titles,
     in_folder,
     out_folder,
     kernel,
     overlay,
     frames,
     rand_frames,
     offset,
     load_filter) = parse_args()

    print("Source: ", files[0])
    print("Encodes: ", pformat(files[1:]))

    # Load from dir or load files
    if in_folder:
        clips = load_clips(folder=in_folder, load_filter=load_filter)
    else:
        clips = load_clips(files=files, load_filter=load_filter)

    if len(clips) == 1:
        if not crop:
            print("WARNING: No crop values were provided. The source will be uncropped.")
            crop = [clips[0].width, clips[0].height]
        if rand_frames:
            frames = generate_random_frames(clips, rand_frames)
    elif len(clips) > 1:
        if rand_frames:
            frames = generate_random_frames(clips[1:], rand_frames)
        # If no crop passed, use encode 1 dimensions
        if not crop:
            crop = [clips[1].width, clips[1].height]
        # Check if source requires resizing
        clips[0] = verify_resize(clips, kernel=kernel)
    else:
        raise ValueError("The number of clips could not be determined, or an unexpected value was received")

    # Crop, Tonemap (if applicable), and Frame Info (if applicable)
    kwargs = {
        'clips': clips,
        'crop_dimensions': crop,
        'clip_titles': titles if titles else None,
        'add_frame_info': overlay
    }
    clips = prepare_clips(**kwargs)

    generate_screenshots(clips, out_folder, frames, offset)


if __name__ == '__main__':
    main()

