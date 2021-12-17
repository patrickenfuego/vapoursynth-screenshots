# Vapoursynth-Screenshots

A simple script for generating screenshots with Vapoursynth.

---

## About

I'm lazy, and hate changing variables for each batch of screenshots I create. This script accepts input from the command line and generates screenshots using `ScreenGen` from the `awsmfunc` Vapoursynth script.

Included is a PowerShell wrapper script (all platforms) to make entering CLI arguments easier. Vapoursynth parses arguments from the global dictionary (so no `argparse`), which is pretty tedious to type. The PowerShell script gives you tab complete functionality and more input validation. It's optional - `screenshots.vpy` works just fine on it's own.

By default, screenshots are generated with character "tags", or letters that distinguish them and make them easy to sort. The script will check for existing tags and increment the characters so the other screenshots are not overwritten.

---

## Dependencies

- [Vapoursynth](https://www.vapoursynth.com/)
- [tonemap plugin](https://github.com/ifb/vapoursynth-tonemap)
- [awsmfunc](https://git.concertos.live/AHD/awsmfunc)

---

## Tonemapping

If the input files are UHD, the script can tonemap them automatically using the tonemap plugin. Tonemapping algorithms:

- Hable
- Mobius
- Reinhard

The default value is Mobius, but you can specify which one you want using the `tonemap_type` parameter. You can also specify the exposure (gain) for the screenshots using the `exposure` parameter.

---

## Parameters

> NOTE: PowerShell parameters are case insensitive, whereas Python's are not. Python parameters must be **lowercase**

| Parameter Name      | Description                                                                           |
| ------------------- | ------------------------------------------------------------------------------------- |
| **[-]source**       | Path to the source file (or primary file)                                             |
| **[-]encode**       | Path to the encode file (or secondary file)                                           |
| **[-]screenshots**  | Optional path to screenshots. If one is not provided, the root of encode will be used |
| **[-]frames**       | A list of frame numbers for screenshots. Passed as a Python list, i.e. "[1,2,3,4]"    |
| **[-]offset**       | Optional frame offset for test encodes                                                |
| **[-]title**        | Title tag for frame info overlay. Applies to encodes. Default is "Encode"             |
| **[-]tonemap_type** | Tonemap algorithm to use (hable, mobius, reinhard). Default is mobius                 |
| **[-]exposure**     | Gain to apply to image. Default is 4.5                                                |

---

## Examples

### PowerShell

> All PowerShell parameters can be used positionally. See `Get-Help .\Wrapper.ps1` or read the comments to see them all.

```PowerShell
#Named parameters
PS > .\Wrapper.ps1 -Encode "C:\Path\file.mkv" -Encode "C:\Path\file2.mkv" -Frames 100,200,300 -Title "My Encode" -TonemapType hable
#Positional parameters
PS > .\Wrapper.ps1 "C:\Path\file.mkv" "C:\Path\file2.mkv" 100,200,300 "C:\Path\Screenshots" hable "My Encode"
```

### VSPipe

```shell
#Pass parameters using --arg
vspipe --arg "source=C:\Path\file1.mkv" --arg "encode=C:\Path\file2.mkv" --arg "frames=[100,200,300]" --arg "tonemap_type=hable" .\screenshots.vpy -
```
