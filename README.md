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
  - [Parameters](#parameters)
  - [Examples](#examples)
  - [Troubleshooting](#troubleshooting)
    - [Python Can't Find VapourSynth](#python-cant-find-vapoursynth)
    - [Feature x Does Not Work](#feature-x-does-not-work)
    - [Python Can't Load Module 'utils.py'](#python-cant-load-module-utilspy)
  - [Acknowledgements](#acknowledgements)

---

## About

I'm lazy, and hate changing variables for each batch of screenshots I create. This script accepts an arbitrary number of video files and other options from the command line and generates screenshots using `ScreenGen` from the `awsmfunc` module. Screenshots are created with a frame info overlay including title, frame number, and picture type unless specified otherwise.

By default, screenshots are generated with character "tags", or letters, that distinguish them and make them easy to sort; for example, source screens will be named '1a.png', '2a.png', encode 1 screens will be '1b.png', '2b.png', etc. The script will check for existing tags and increment the characters so other screenshots in the same directory are not overwritten (unless you generate *a lot* of them, as there are only 26 characters in the English alphabet).

When capturing screenshots for multiple encodes, I highly recommend using the same crop values. When cropping the source, the first encode passed is used to get the dimensions. If you only want screenshots of the source and wish to crop it, use the `--crop` argument (see below).

---

## Dependencies

For installing dependencies, I *highly* recommend using the [VSRepo GUI](https://github.com/theChaosCoder/VSRepoGUI) so you don't have to hunt down all of the various GitHub repos and keep them updated. However, I list the various dependencies below if you wish to manage them manually.

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

I've included plugins for Windows users under the `bin` directory, although I might not keep them up to date.

---

## Other Features

### Previewing Clips

If you wish to preview clips before generating screenshots, use the `compare.py` file. This functionality utilizes the `view` module, and unlike most other methods, does not require `vspipe` or `vsedit` which is incredibly convenient as you can run it like a normal Python file. The OpenCV Python module is required - see [Dependencies](#dependencies) above.

### Tonemapping

> NOTE: Tonemapping has changed significantly since the last release of this project

For any HDR/DoVi/HDR10+ sources, the script automatically tonemaps the screenshots for you using the `DynamicTonemap` function from `awsmfunc`. I think this tonemaps screenshots better than the older tonemap plugin, which was used previously.

For properly tonemapping DoVi, additional plugins are required. See [Dependencies](#dependencies) for more information.

---

## Parameters

> A \* denotes that one or the other is required

| Parameter Name       | Alias | Description                                                                                                                       | Mandatory    |
| -------------------- | ----- | --------------------------------------------------------------------------------------------------------------------------------- | ------------ |
| `--source`           | None  | Path to the source file. Positional                                                                                               | True         |
| `--encodes`          | `-e`  | Space delimited list of encode files                                                                                              | False        |
| `--frames`           | `-f`  | Space delimited list of screenshot frame numbers                                                                                  | <b>*</b>True |
| `--random_frames`    | `-r`  | Generate random frames between `start` & `stop`. Input is space delimited in the form `start stop count`                          | <b>*</b>True |
| `--titles`           | `-t`  | Space delimited list of titles for the encodes. Must match the number of encodes passed                                           | False        |
| `--offset`           | `-o`  | Optional frame offset from source. Used for test encodes                                                                          | False        |
| `--input_directory`  | `-d`  | Path to an input directory containing encodes to screenshot                                                                       | False        |
| `--output_directory` | `-od` | Output directory path. Default uses the root folder for `--source`                                                                | False        |
| `--resize_kernel`    | `-k`  | Specify a resizing kernel to use for source on upscaled/downscaled encodes (make sure screenshots match)                          | False        |
| `--no_frame_info`    | `-ni` | Don't add frame overlay with name, frame number, picture type, etc. Default enabled                                               | False        |
| `--crop`             | `-c`  | Optional custom crop dimensions to use. Default uses the dimensions of the first encode passed. Set this if only passing `source` | False        |
| `--load_filter`      | `-lf` | Filter used to load & index clips. Default is `ffms2`                                                                             | False        |

---

## Examples

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
# Specify an offset of 10000 frames to align test encodes
~$ python3 screenshots.py "$HOME/Videos/MySource/Source.mkv" --input_directory "$HOME/Videos/MySource" \
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

If Python can't detect VapourSynth after installation, navigate to the VapourSynth installation directory and **copy** (not cut) the dynamic libraries `vapoursynth.dll`/`vapoursynth.so` and `vsscript.dll`/`vsscript.so` and paste them into the root directory of your Python installation directory.

### Feature x Does Not Work

This is more than likely a plugin or a PATH issue. Make sure you have the latest plugins installed in the `plugins64` directory, and both VapourSynth and Python are available via system PATH.

### Python Can't Load Module 'utils.py'

This is most likely a Python path issue. To solve, set (or append to) the environment variable `PYTHONPATH` with the path of the `modules` directory inside this project.

## Acknowledgements

This project utilizes several plugins and scripts written by other people within the community. All credit goes to them.

- OpusGang - `Awsmfunc`
- UniversalAI - `view`
- Lypheo - `vs-placebo` plugin
- quietvoid - `dovi` plugin
- theChaosCoder - VSRepo GUI
