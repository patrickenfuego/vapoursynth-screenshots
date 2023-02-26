<#
    .SYNOPSIS
        Powershell wrapper for screenshots.py
    .DESCRIPTION
        A wrapper that provides readline and autocomplete functionality for screenshots.py.
        Linux users have access to argcomplete, which is less straightforward to implement
        on Windows. This script attempts to fill that gap
    .NOTES
        This script does minimal input validation and mostly relies on the python script.

        For help, please use the -Help parameter which calls the python script.
#>

[CmdletBinding(DefaultParameterSetName = 'Frames')]
param (
    [Parameter(Mandatory = $false, Position = 0, ParameterSetName = 'Frames')]
    [Parameter(Mandatory = $false, Position = 0, ParameterSetName = 'RandomFrames')]
    [ValidateScript(
        {
            if (!(Test-Path $_)) {
                throw "Source input path does not exist"
            }
            else { $true }
        }
    )]
    [Alias('S')]
    [string]$Source,

    [Parameter(Mandatory = $false, ParameterSetName = 'Frames')]
    [Parameter(Mandatory = $false, ParameterSetName = 'RandomFrames')]
    [ValidateScript(
        {
            $res = $_.ForEach({ Test-Path $_ })
            if ($res -contains $false) { throw "One ore more file paths do not exist" }
            else { $true }
        }
    )]
    [Alias('E')]
    [string[]]$Encodes,

    [Parameter(Mandatory = $true, ParameterSetName = 'Frames')]
    [Alias('F')]
    [int[]]$Frames,

    [Parameter(Mandatory = $true, ParameterSetName = 'RandomFrames')]
    [ValidateCount(3, 3)]
    [Alias('RF')]
    [int[]]$RandomFrames,

    [Parameter(Mandatory = $false, ParameterSetName = 'Frames')]
    [Parameter(Mandatory = $false, ParameterSetName = 'RandomFrames')]
    [Alias('O')]
    [int]$Offset,

    [Parameter(Mandatory = $false, ParameterSetName = 'Frames')]
    [Parameter(Mandatory = $false, ParameterSetName = 'RandomFrames')]
    [ValidateCount(2, 2)]
    [Alias('C')]
    [int[]]$Crop,

    [Parameter(Mandatory = $false, ParameterSetName = 'Frames')]
    [Parameter(Mandatory = $false, ParameterSetName = 'RandomFrames')]
    [Alias('T')]
    [string[]]$Titles,

    [Parameter(Mandatory = $false, ParameterSetName = 'Frames')]
    [Parameter(Mandatory = $false, ParameterSetName = 'RandomFrames')]
    [ValidateScript(
        {
            if (!(Test-Path $_)) {
                throw "Input directory does not exist"
            }
            else { $true }
        }
    )]
    [Alias('D')]
    [string]$InputDirectory,

    [Parameter(Mandatory = $false, ParameterSetName = 'Frames')]
    [Parameter(Mandatory = $false, ParameterSetName = 'RandomFrames')]
    [Alias('OD')]
    [string]$OutputDirectory,

    [Parameter(Mandatory = $false, ParameterSetName = 'Frames')]
    [Parameter(Mandatory = $false, ParameterSetName = 'RandomFrames')]
    [ValidateSet('bilinear', 'bicubic', 'point', 'lanczos', 'spline16', 'spline36', 'spline64')]
    [Alias('K')]
    [string]$ResizeKernel,

    [Parameter(Mandatory = $false, ParameterSetName = 'Frames')]
    [Parameter(Mandatory = $false, ParameterSetName = 'RandomFrames')]
    [ValidateSet('lsmas', 'ffms2')]
    [Alias('LF')]
    [string]$LoadFilter,

    [Parameter(Mandatory = $false, ParameterSetName = 'Frames')]
    [Parameter(Mandatory = $false, ParameterSetName = 'RandomFrames')]
    [Alias('NI')]
    [switch]$NoFrameInfo,

    [Parameter(Mandatory = $true, ParameterSetName = 'Help')]
    [Alias('H')]
    [switch]$Help
)

if (!$PSBoundParameters['Source'] -and !$PSBoundParameters['Encodes'] -and !$PSBoundParameters['InputDirectory']) {
    Write-Error "No input files or directories were provided" -ErrorAction Stop
}

if (!(Get-Command 'python')) {
    Write-Error "Python could not be resolved in system PATH" -ErrorAction Stop
}

$scriptPath = Join-Path $PSScriptRoot -ChildPath 'screenshots.py'
if (!(Test-Path $scriptPath)) {
    Write-Error "Could not locate 'screenshots.py'. Are you running the wrapper from the same directory?" -ErrorAction Stop
}

if ($Help) {
    & python $scriptPath -h
    exit 0
}

$pyArgs = @(
    $scriptPath
    if ($PSBoundParameters['Source']) {
        '-s'
        $Source
    }
    if ($PSBoundParameters['Encodes']) {
        '-e'
        $Encodes
    }
    if ($PSBoundParameters['Titles']) {
        '-t'
        $Titles
    }
    if ($PSBoundParameters['Crop']) {
        '-c'
        $Crop
    }
    if ($PSBoundParameters['Frames']) {
        '-f'
        $Frames
    }
    if ($PSBoundParameters['RandomFrames']) {
        '-rf'
        $RandomFrames
    }
    if ($PSBoundParameters['Offset']) {
        '-o'
        $Offset
    }
    if ($PSBoundParameters['InputDirectory']) {
        '-d'
        $InputDirectory
    }
    if ($PSBoundParameters['OutputDirectory']) {
        '-od'
        $OutputDirectory
    }
    if ($PSBoundParameters['ResizeKernel']) {
        '-k'
        $ResizeKernel
    }
    if ($PSBoundParameters['LoadFilter']) {
        '-lf'
        $LoadFilter
    }
    if ($NoFrameInfo) {
        '-ni'
    }
)

# Execute python screenshots script with params
& python $pyArgs