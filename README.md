# Vapoursynth-Screenshots

A simple script for generating screenshots with Vapoursynth.

---

## About

I'm lazy, and hate changing variables for each batch of screenshots I create. This script accepts input from the command line and generates screenshots using `ScreenGen` from the `awsmfunc` Vapoursynth script.

Included is a PowerShell wrapper script (all platforms with Pwsh 6/7) to make entering CLI arguments easier. Vapoursynth parses arguments from the global dictionary (so no `argparse`), which is pretty tedious to type. The PowerShell script gives you tab complete functionality and more input validation. It's optional - `screenshots.vpy` works just fine on it's own.

By default, screenshots are generated with character "tags", or letters that distinguish them and make them easy to sort. The script will check for existing tags and increment the characters so other screenshots in the same directory are not overwritten.

---

## Dependencies

- [Vapoursynth](https://www.vapoursynth.com/)
- [tonemap plugin](https://github.com/ifb/vapoursynth-tonemap)
- [awsmfunc](https://git.concertos.live/AHD/awsmfunc)
- [ffprobe](https://ffmpeg.org/ffprobe.html)

---

## Tonemapping

If the input files are YUV420P10 (YUV 4:2:0 10-Bit), the script will tonemap them automatically using the tonemap plugin. Tonemapping algorithms:

- Hable
- Mobius
- Reinhard

The default is Mobius, but you can specify which one you want using the `tonemap_type` (or `-TonemapType` with PowerShell) parameter. You can also specify the exposure (gain) for the screenshots using the `exposure` parameter; default is 4.5.

---

## Parameters

> NOTE: PowerShell parameters are case insensitive, whereas Python's are not. Python parameters must be **lowercase**

| Parameter Name      | Description                                                                            | Mandatory     |
| ------------------- | -------------------------------------------------------------------------------------- | ------------- |
| **[-]source**       | Path to the source file                                                                | <b>*</b>False |
| **[-]encode**       | Path to the encode file                                                                | <b>*</b>False |
| **[-]encode2**      | Path to a second encode file                                                           | <b>*</b>False |
| **[-]screenshots**  | Optional path to screenshots. If one is not provided, the root of encode will be used  | False         |
| **[-]frames**       | A list of frame numbers for screenshots. Passed as a Python list, i.e. "[1,2,3,4]"     | True          |
| **[-]offset**       | Optional frame offset for test encodes                                                 | False         |
| **[-]title**        | Title tag for frame info overlay. Applies to the encode parameter. Default is "Encode" | False         |
| **[-]title2**       | Title tag for frame info overlay. Applies to encode2 parameter. Default is "Encode 2"  | False         |
| **[-]tonemap_type** | Tonemap algorithm to use. Equivalent Pwsh parameter is `TonemapType`                   | False         |
| **[-]exposure**     | Gain to apply to image. Default is 4.5                                                 | False         |

Input file parameters are marked with an asterisk because one of them must be present or an error is thrown (seems sensible, right?).

---

## Examples

### PowerShell

```PowerShell
#Named parameters
PS > .\ScreenshotHelper.ps1 -Encode "C:\Path\file.mkv" -Encode "C:\Path\file2.mkv" `
                            -Frames 100,200,300 -TonemapType hable -Title "My Encode"
```

### VSPipe

```shell
#Pass parameters using --arg
~$ vspipe --arg "source=~/videos/source.mkv" --arg "encode=~/videos/encode.mkv" \
              --arg "frames=[100,200,300]" --arg "tonemap_type=hable" screenshots.vpy -
```
