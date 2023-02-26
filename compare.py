#!/usr/bin/env python3

"""
CLI script for comparing media files.

This script allows you to compare source and encoded files without using VSEdit or VSPipe.
For comparison, it uses view (written by UniversalAI) to compare files using an intuitive
PythonQT view window. Repo for view can be found here: https://github.com/UniversalAl/view.
Since view is not available via pip, I've added it to this repo for convenience.

Example usage::

    PS > python compare.py 'C:\path\source.mkv' --encodes 'C:\path\enc1.mkv', 'C:\path\enc2.mkv'

You can also pass the script a folder containing files you want to compare::

    ~$ python compare.py '/path/source.mkv' --folder '/path/folder/with/encodes'

Run help to view all available options::

    ~$ python compare.py --help

"""

import vapoursynth as vs

import argparse
import argcomplete
from pprint import pformat

from modules import (
    Preview,
    path_exists,
    prepare_clips,
    verify_resize,
    get_dimensions,
    load_clips
)

core = vs.core


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "CLI script for comparing media files using VapourSynth. This allows you "
            "to view files in a preview (similar to VS Interleave function) without the "
            "need to use vspipe or the VS Editor, which is very convenient! You can simply "
            "run it like a normal python script. Requires dependencies, make sure to install "
            "'opencv-contrib-python'."
        ),
        epilog='view module created by UniversalAI. All credit goes to them.'
    )
    argcomplete.autocomplete(parser)

    parser.add_argument('source', nargs='?', metavar='SOURCE', type=path_exists,
                        help='Path to source file. Required')
    parser.add_argument('--frames', '-f', nargs=2, metavar='FRAMES', type=int,
                        help="Frame range to evaluate, in the form 'START END'. Useful for comparing test encodes")
    parser.add_argument('--crop', '-c', nargs=2, metavar='CROP', type=int,
                        help='Crop dimensions for files in the form WIDTH HEIGHT. All files should use the same values')
    parser.add_argument('--encodes', '-e', metavar='ENCODES', type=path_exists, nargs='+',
                        help='Paths to encoded file(s) you wish to compare')
    parser.add_argument('--titles', '-t', metavar='TITLES', type=str, nargs='+',
                        help='ScreenGen titles for files. Should match the order of --encodes')
    parser.add_argument('--input_directory', '-d', metavar='IN_FOLDER', type=path_exists, nargs='?',
                        help='Path to folder containing encoded file(s). Replaces --encodes')
    parser.add_argument('--resize_kernel', '-k', metavar='KERNEL', type=str, nargs='?', default='spline36',
                        help="Specify kernel used for resizing (if encodes are upscaled/downscaled). Default is 'spline36'")
    parser.add_argument('--preview_resolution', '-p', metavar='RESOLUTION', type=str, nargs='?',
                        default='1080p', choices=('720p', '1080p', '1440p', '2160p'),
                        help='Preview window resolution, which can be different from source. Default is 1080p (1920x1080)')
    parser.add_argument('--load_filter', '-lf', type=str, choices=('lsmas', 'ffms2'), default='ffms2',
                        help="Filter used to load & index clips. Default is 'ffms2'")
    parser.add_argument('--no_frame_info', '-ni', action='store_false',
                        help="Don't add frame info overlay to clips. This flag negates the default behavior")

    args = parser.parse_args()

    if not args.encodes and not args.input_directory:
        raise FileNotFoundError(
            "No comparison files provided. Specify encodes via '--encodes' or a folder containing encodes "
            "via '--input_directory'."
        )

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
            args.preview_resolution if isinstance(args.preview_resolution, str) else args.preview_resolution[0],
            args.resize_kernel,
            args.no_frame_info,
            args.frames,
            args.load_filter[0] if type(args.load_filter) is list else args.load_filter)


def main():
    (files,
     crop,
     titles,
     folder,
     res,
     kernel,
     overlay,
     frames,
     load_filter) = parse_args()

    print("Source: ", files[0])
    print("Encodes: ", pformat(files[1:]))

    # Probably didn't add 'Source' as a title
    if titles and len(files) - len(titles) == 1:
        titles.insert(0, 'Source')

    # Load clips
    if folder:
        clips = load_clips(folder=folder, load_filter=load_filter)
    else:
        clips = load_clips(files=files, load_filter=load_filter)

    # If frame range was specified
    if frames and frames[0] < frames[1]:
        clips[0] = clips[0][frames[0]:frames[1]+1]
    elif frames and frames[0] >= frames[1]:
        raise ValueError("Invalid frame range. Start of range must be less than end")

    # If crop not passed, use encode1 dimensions
    if not crop:
        crop = [clips[1].width, clips[1].height]
    # Check if source requires resizing and resize if needed
    clips[0] = verify_resize(clips, kernel=kernel)

    # Crop, Tonemap (if applicable), and Frame Info (if applicable)
    kwargs = {
        'clips': clips,
        'crop_dimensions': crop,
        'clip_titles': titles if titles else None,
        'add_frame_info': overlay
    }
    clips = prepare_clips(**kwargs)

    # Set view dimensions. Use encode clip as reference for better scaling
    view_width, view_height = get_dimensions(res, clip=clips[1])
    print(f"View dimensions: {view_width}x{view_height}\n")

    # Display clips using view
    Preview(clips, preview_width=view_width, preview_height=view_height)


if __name__ == '__main__':
    main()
