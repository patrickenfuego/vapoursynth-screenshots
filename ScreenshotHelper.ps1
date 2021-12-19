<#
    .SYNOPSIS
        Wrapper script for screenshots.vpy
    .DESCRIPTION
        Vapoursynth doesn't support robust CLI libraries like argparse because
        all arguments are parsed from the global dictionary. This script is meant
        to make passing CLI args less painful
    .PARAMETER Source
        Path to the source (or primary) file
    .PARAMETER Encode
        Path to the encoded (or secondary) file
    .PARAMETER ScreenshotPath
        Optional path to screenshots directory. If not passed, the root of encode 
        will be used instead
    .PARAMETER frames
        Array of screenshot frames
    .PARAMETER Offset
        If comparing a test encode to the source, set the offset (in frames)
    .PARAMETER Title
        Optional title for encode screenshots. Default is "Encode"
    .NOTES
        Vapoursynth must be installed and vspipe available via PATH
#>

[CmdletBinding()]
param (
    [Parameter(Mandatory = $false, Position = 0)]
    [ValidateScript(
        {
            if (!(Test-Path $_)) {
                throw "Source input path does not exist"
            }
            else { $true }
        }
    )]
    [Alias("Src")]
    [string]$Source,

    [Parameter(Mandatory = $false, Position = 1)]
    [ValidateScript(
        {
            if (!(Test-Path $_)) {
                throw "Encode input path does not exist"
            }
            else { $true }
        }
    )]
    [Alias("Enc")]
    [string]$Encode,

    [Parameter(Mandatory = $true, Position = 2)]
    [Alias("F")]
    [int[]]$Frames,

    [Parameter(Mandatory = $false, Position = 3)]
    [Alias("Screenshots")]
    [string]$ScreenshotPath,

    [Parameter(Mandatory = $false, Position = 4)]
    [Alias("Tonemap")]
    [string]$TonemapType = "mobius",

    [Parameter(Mandatory = $false, Position = 5)]
    [Alias("T", "Name")]
    [string]$Title = "Encode",

    [Parameter(Mandatory = $false, Position = 6)]
    [Alias("E")]
    [double]$Exposure = 4.5,

    [Parameter(Mandatory = $false, Position = 7)]
    [Alias("O")]
    [int]$Offset
)

#Verify at least one file path was passed
if (!$PSBoundParameters['Source'] -and !$PSBoundParameters['Encode']) {
    throw "Must pass at least one input file to capture"
}

$script = Join-Path $PSScriptRoot -ChildPath "screenshots.vpy"
#$Frames = @(1,2,3,4)
[string]$Frames = "[$($Frames -join ",")]"
#$Frames.GetType()
$TonemapType = $TonemapType.ToLower()

#Make sure VS is installed
if (!(Get-Command "vspipe")) {
    throw "Could not find vspipe in PATH. Make sure Vapoursynth is installed"
}
#If no path is set, set encode root as path
if (!$PSBoundParameters['ScreenshotPath']) {
    $ScreenshotPath = Split-Path $Encode -Parent
}

#Set args for vspipe
$vsArgs = @(
    if ($PSBoundParameters['Source']) {
        '--arg'
        "source=$Source"
    }
    if ($PSBoundParameters['Encode']) {
        '--arg'
        "encode=$Encode"
    }
    '--arg'
    "screenshots=$ScreenshotPath"
    '--arg'
    "title=$Title"
    '--arg'
    "frames=$Frames"
    '--arg'
    "tonemap_type=$TonemapType"
    '--arg'
    "exposure=$Exposure"
    if ($PSBoundParameters['Offset']) {
        '--args'
        "offset=$Offset"
    }
)

vspipe $vsArgs $script -




