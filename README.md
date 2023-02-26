# Vapoursynth-Screenshots

A collection of scripts for previewing clips and generating screenshots with Vapoursynth. Previewing clips does not require `vspipe` or `vsedit`.

- [Vapoursynth-Screenshots](#vapoursynth-screenshots)
  - [About](#about)
  - [Dependencies](#dependencies)
    - [Python](#python)
    - [VapourSynth](#vapoursynth)
    - [Python Packages](#python-packages)
    - [VapourSynth Plugins](#vapoursynth-plugins)
  - [Other Features](#other-features)
    - [Previewing Clips](#previewing-clips)
    - [Tonemapping](#tonemapping)
  - [Arguments](#arguments)
    - [Screenshot Notes](#screenshot-notes)
    - [Shared Arguments](#shared-arguments)
    - [Screenshots Only](#screenshots-only)
    - [Compare Only](#compare-only)
  - [Examples](#examples)
    - [Compare](#compare)
    - [Screenshots](#screenshots)
  - [Troubleshooting](#troubleshooting)
    - [Python Can't Find VapourSynth](#python-cant-find-vapoursynth)
    - [Feature x Does Not Work](#feature-x-does-not-work)
    - [Python Can't Load Module 'utils.py'](#python-cant-load-module-utilspy)
    - [Error `Tonemap: Function does not take argument(s) named tone_mapping_function_s`](#error-tonemap-function-does-not-take-arguments-named-tone_mapping_function_s)
  - [Acknowledgements](#acknowledgements)

---

## About

I'm lazy, and hate changing variables for each batch of screenshots I create. This script accepts an arbitrary number of video files and other options from the command line and generates screenshots using `ScreenGen` from the `awsmfunc` module. Screenshots are created with a frame info overlay including title, frame number, and picture type unless specified otherwise.

By default, screenshots are generated with character "tags", or letters, that distinguish them and make them easy to sort; for example, source screens will be named '1a.png', '2a.png', encode 1 screens will be '1b.png', '2b.png', etc. The script will check for existing tags and increment the characters so other screenshots in the same directory are not overwritten (unless you generate *a lot* of them, as there are only 26 characters in the English alphabet).

When capturing screenshots for multiple encodes, I highly recommend using the same crop values. When cropping the source, the first encode passed is used to get the dimensions. If you only want screenshots of the source and wish to crop it, use the `--crop` argument (see below).

---

## Dependencies

For installing dependencies on Windows, I *highly* recommend using the [VSRepo GUI](https://github.com/theChaosCoder/VSRepoGUI) so you don't have to hunt down all of the various GitHub repos and keep them updated. However, I list the various dependencies below if you wish to manage them manually.

### Python

At the time of writing, VapourSynth R61's API is only compatible with Python [Python 3.10](https://www.python.org/downloads/release/python-31010/). 3.11 might work, I haven't tried.

### VapourSynth

Download the [VapourSynth](https://github.com/vapoursynth/vapoursynth/releases) installer and run it. Make sure you follow the instructions regarding the type of Python installation you have. I recommend doing a full install as I've had far less issues with it vs. the portable install.

### Python Packages

- [Vapoursynth](https://www.vapoursynth.com/)
- [Awsmfunc](https://github.com/OpusGang/awsmfunc)
  - [rekt](https://pypi.org/project/rekt/) (only required if you manually install dependencies)
  - This module includes support for several other optional plugins and scripts not included with this repo. See their docs for more details
- [opencv-contrib-python](https://pypi.org/project/opencv-contrib-python/) (only required if you want to use the `compare.py` functionality)
  - Previewing clips before generating screenshots is accomplished via the [view](https://github.com/UniversalAl/view) module, which is not included in PyPI so I have added it to the repo under `modules`. This is the core dependency needed for this feature
- [argcomplete](https://kislyuk.github.io/argcomplete/#) (optional argument completer for Linux shells)

To make life easy, use the `requirements.txt` file included as it will install all of the additional dependencies needed by the packages above:

```python
# From the projects's root level directory
pip install -r requirements.txt
```

### VapourSynth Plugins

- [vs-placebo](https://github.com/Lypheo/vs-placebo) (tonemapping only)
- [dovi](https://github.com/quietvoid/dovi_tool/tree/main/dolby_vision) (tonemapping only)

For loading clips, either `lsmas` or `ffms2` are required. `ffms2` is preferred as it supports DoVi tonemapping. The scripting allows you to specify which one you want to use:

- [lsmas](https://github.com/HomeOfAviSynthPlusEvolution/L-SMASH-Works)
- [ffms2](https://github.com/FFMS/ffms2/releases)

Plugins must be placed inside the `plugins64` directory inside of the VapourSynth installation directory. For users of VSRepo, plugins are installed at `C:\Users\<Username>\AppData\Roaming\VaporSynth\plugins64`.

I've included some compiled plugins for both Windows and Linux users under the `bin` directory, although I might not keep them up to date. Copy them into your `plugins64` directory (see above).

---

## Other Features

### Previewing Clips

If you wish to preview clips before generating screenshots, use the `compare.py` file. This functionality utilizes the `view` module, and unlike most other methods, does not require `vspipe` or `vsedit` which is incredibly convenient as you can run it like a normal Python file. The OpenCV Python module is required - see [Dependencies](#dependencies) above.

If you wish to compare test encode(s) vs. the source, specify the frame range using the `--frames`/`-f` argument. This will slice the source to ensure frames match during comparison. Depending on where the video is sliced, slight adjustments might be required to ensure all video files are aligned.

You can also take screenshots in the preview window using keybindings, although they will be missing some features included with the `screenshots.py` module.

### Tonemapping

> NOTE: Tonemapping has changed significantly since the last release of this project

For any HDR/DoVi/HDR10+ sources, the script automatically tonemaps the screenshots for you using the `DynamicTonemap` function from `awsmfunc`. I think this tonemaps screenshots better than the older tonemap plugin, which was used previously.

For properly tonemapping DoVi, additional plugins are required. See [Dependencies](#dependencies) for more information.

---

## Arguments

### Screenshot Notes

One or more of the following arguments are required:

- `--source`/`-s`
- `--encodes` / `-e`
- `--input_directory`/`-d`

If no source is passed and `--input_directory` is used, the script will attempt guess the source based on file size and exclude it (assuming all files are saved in the same directory). If the source is located in a different directory, it is recommended to pass the source via argument so indexing is performed correctly.

### Shared Arguments

> A \* denotes that an argument is required only if a similar argument isn't already passed (i.e., `--frames` vs `--random_frames`)

| Full Argument Name | Alias | Description                                                                                                                                                        | Mandatory: `screenshots` / `compare` |
| ------------------ | ----- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------ |
| `source`           | `-s`  | Path to the source file                                                                                                                                            | <b>*</b>True / True                  |
| `encodes`          | `-e`  | Space delimited list of encode files                                                                                                                               | <b>\*</b>True / <b>*</b>True          |
| `frames`           | `-f`  | Space delimited list of screenshot frame numbers. For `compare`, this accepts a range in the form 'START STOP'                                                     | <b>*</b>True / False                 |
| `titles`           | `-t`  | Space delimited list of titles for the encodes. Must match the number of encodes passed                                                                            | False / False                        |
| `input_directory`  | `-d`  | Path to an input directory containing encodes to screenshot                                                                                                        | <b>\*</b>True / <b>*</b>True          |
| `resize_kernel`    | `-k`  | Specify a resizing kernel to use for source on upscaled/downscaled encodes (make sure screenshots match)                                                           | False / False                        |
| `no_frame_info`    | `-ni` | Don't add frame overlay with name, frame number, picture type, etc. This flag negates the default behavior                                                         | False / False                        |
| `crop`             | `-c`  | Optional custom crop dimensions to use. Default uses the dimensions of the first encode passed. Set this if only passing `source` or wish to use a different value | False / False                        |
| `load_filter`      | `-lf` | Filter used to load & index clips. Default is `ffms2`                                                                                                              | False / False                        |

### Screenshots Only

| Full Argument Name | Alias | Description                                                                                                                  | Mandatory    |
| ------------------ | ----- | ---------------------------------------------------------------------------------------------------------------------------- | ------------ |
| `output_directory` | `-od` | Output directory path for saved screenshots. Default behavior uses the root folder for `source`                              | False        |
| `offset`           | `-o`  | Optional frame offset from source. Used for aligning test encodes                                                            | False        |
| `random_frames`    | `-r`  | Generate `count` random, sequential frames between `start` & `stop`. Input is space delimited in the form `start stop count` | <b>*</b>True |

### Compare Only

The preview resolution is used to scale dimensions for your viewing monitor, and is unrelated to the dimensions of the video files. Once a resolution is specified, it is then scaled based on the crop values to eliminate stretching.

Options for `preview_resolution`:

- 720p
- 1080p
- 1440p
- 2160p

| Full Argument Name   | Alias | Description                                                               | Mandatory |
| -------------------- | ----- | ------------------------------------------------------------------------- | --------- |
| `preview_resolution` | `-p`  | Preview window resolution to better match the monitor. Default is '1080p' | False     |

---

## Examples

### Compare

```bash
# Compare a source vs. an encode
~$ python3 compare.py "$HOME/Videos/MySource/Source.mkv" --encodes "$HOME/Videos/MySource/Encode1.mkv"
```

```bash
# Set view resolution to 1440p. Note this doesn't have to match the source resolution
~$ python3 compare.py "$HOME/Videos/MySource/Source.mkv" --encodes "$HOME/Videos/MySource/Encode1.mkv" \
    --preview_resolution '1440p'
```

```PowerShell
# View frames between 1000-5000. Useful for comparing source against test encodes
PS > python compare.py "$HOME\Videos\MySource\Source.mkv" --encodes "$HOME\Videos\MySource\Encode1.mkv" `
     "$HOME\Videos\MySource\Encode2.mkv" "$HOME\Videos\MySource\Encode3.mkv" --frames 1000 5000
```

### Screenshots

```PowerShell
# Generate screenshots for source and 3 encodes
PS > python screenshots.py "$HOME\Videos\MySource\Source.mkv" --encodes "$HOME\Videos\MySource\Encode1.mkv" `
     "$HOME\Videos\MySource\Encode2.mkv" "$HOME\Videos\MySource\Encode3.mkv" --frames 2000 4000 6000
```

```PowerShell
# Generate screenshots for source and 3 encodes with random frames starting at frame 1000, ending at 5000,
# with a count of 25
PS > python screenshots.py "$HOME\Videos\MySource\Source.mkv" --encodes "$HOME\Videos\MySource\Encode1.mkv" `
     "$HOME\Videos\MySource\Encode2.mkv" "$HOME\Videos\MySource\Encode3.mkv" --random_frames 1000 5000 25
```

```bash
# Specify an offset of 10000 frames to align test encodes with source
~$ python3 screenshots.py "$HOME/Videos/MySource/Source.mkv" --encodes "$HOME/Videos/MySource/Encode1.mkv" \
    --offset 10000 --frames 2000 4000 6000
```

```bash
# Specify a folder containing all encodes you want screenshots for
~$ python3 screenshots.py "$HOME/Videos/MySource/Source.mkv" --input_directory "$HOME/Videos/MySource" \
    --frames 2000 4000 6000
```

```bash
# Specify an output folder for screenshots. Default is saved in the root of source file
~$ python3 screenshots.py "$HOME/Videos/MySource/Source.mkv" --input_directory "$HOME/Videos/MySource" \
    --output_directory "$HOME/Desktop/screens-t1" --frames 2000 4000 6000
```

## Troubleshooting

### Python Can't Find VapourSynth

If Python can't detect VapourSynth after installation, navigate to the VapourSynth installation directory and **copy** (not cut) the dynamic libraries `vapoursynth.dll`/`vapoursynth.so` and `vsscript.dll`/`vsscript.so` and paste them into either the root directory of your Python installation directory or one of the `site-packages` directories.

### Feature x Does Not Work

This is more than likely a plugin or a PATH issue. Make sure you have the latest plugins installed in the `plugins64` directory, and both VapourSynth and Python are available via system PATH.

### Python Can't Load Module 'utils.py'

This is most likely a Python path issue. To solve, set (or append to) the environment variable `PYTHONPATH` with the path of the `modules` directory inside this project.

### Error `Tonemap: Function does not take argument(s) named tone_mapping_function_s`

This is due to an incompatibility between `vs-placebo` and `awsmfunc`. If you're running into this, use `awsmfunc` version 1.3.3 as 1.3.4 (currently the latest) requires a custom compiled version of the `libvs_placebo` plugin.

Linux users should be ok as I compiled the plugin recently. I plan to compile it manually for Windows and add it under `/bin` in the project sometime soon.

## Acknowledgements

This project utilizes several plugins and scripts written by other people within the community. All credit goes to them.

- OpusGang - `Awsmfunc`
- UniversalAI - `view`
- Lypheo - `vs-placebo` plugin
- quietvoid - `dovi` plugin
- theChaosCoder - VSRepo GUI
