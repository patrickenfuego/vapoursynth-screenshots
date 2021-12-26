<#
    .SYNOPSIS
        Wrapper script for screenshots.vpy
    .DESCRIPTION
        Vapoursynth doesn't support robust CLI libraries like argparse because
        all arguments are parsed from the global dictionary. This script is meant
        to make passing CLI args less painful
    .PARAMETER Source
        Path to the source file
    .PARAMETER Encode
        Path to an encoded file
    .PARAMETER Encode2
        Path to a second encoded file
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
    [Parameter(Mandatory = $false)]
    [ValidateScript(
        {
            if (!(Test-Path $_)) {
                throw "Source input path does not exist"
            }
            else { $true }
        }
    )]
    [Alias("Src")]
    [string[]]$Sources,

    [Parameter(Mandatory = $false)]
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

    [Parameter(Mandatory = $false)]
    [ValidateScript(
        {
            if (!(Test-Path $_)) {
                throw "Encode2 input path does not exist"
            }
            else { $true }
        }
    )]
    [Alias("Enc2")]
    [string]$Encode2,

    [Parameter(Mandatory = $true)]
    [Alias("F")]
    [int[]]$Frames,

    [Parameter(Mandatory = $false)]
    [Alias("Screenshots")]
    [string]$ScreenshotPath,

    [Parameter(Mandatory = $false)]
    [Alias("Tonemap")]
    [string]$TonemapType = "mobius",

    [Parameter(Mandatory = $false)]
    [Alias("T", "Name")]
    [string]$Title = "Encode",

    [Parameter(Mandatory = $false)]
    [Alias("T2", "Name2")]
    [string]$Title2 = "Encode 2",

    [Parameter(Mandatory = $false)]
    [Alias("E")]
    [double]$Exposure = 4.5,

    [Parameter(Mandatory = $false)]
    [Alias("O")]
    [int]$Offset
)

#Verify at least one file path was passed
if (!$PSBoundParameters['Source'] -and 
    !$PSBoundParameters['Encode'] -and 
    !$PSBoundParameters['Encode2']) {
        
    throw "Must pass at least one input file to capture"
}

$script = Join-Path $PSScriptRoot -ChildPath "screenshots.vpy"
[string]$Frames = "[$($Frames -join ",")]"
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
    if ($PSBoundParameters['Encode2']) {
        '--arg'
        "encode2=$Encode2"
    }
    if ($PSBoundParameters['ScreenshotPath']) {
        '--arg'
        "screenshots=$ScreenshotPath"
    }
    if ($PSBoundParameters['Offset']) {
        '--arg'
        "offset=$Offset"
    }
    '--arg'
    "title=$Title"
    '--arg'
    "title2=$Title2"
    '--arg'
    "frames=$Frames"
    '--arg'
    "tonemap_type=$TonemapType"
    '--arg'
    "exposure=$Exposure"
)

vspipe $vsArgs $script -

