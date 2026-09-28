param(
    [switch]$Execute,
    [switch]$Software,
    [string]$GamePath = 'work/source/original.iso'
)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$emulatorPath = Join-Path $PSScriptRoot 'vendor/ppsspp-1.20.4/PPSSPPWindows64.exe'
$configPath = Join-Path $PSScriptRoot 'ppsspp_baseline.ini'
$gameFullPath = (Resolve-Path -LiteralPath (Join-Path $projectRoot $GamePath)).Path
$graphicsOption = $(if ($Software) { '--graphics=software' } else { '--graphics=directx11' })
$launchArguments = @('--windowed', $graphicsOption, ('--config="' + $configPath + '"'), ('"' + $gameFullPath + '"'))
[pscustomobject]@{
    Mode = $(if ($Execute) { 'Launch' } else { 'Dry run' })
    Emulator = $emulatorPath
    Game = $gameFullPath
    Configuration = $configPath
    Debugger = 'ws://127.0.0.1:19380/debugger'
    SoftwareRendering = [bool]$Software
    Arguments = $launchArguments
} | ConvertTo-Json
if (-not $Execute) { return }
$existing = Get-Process -Name PPSSPPWindows64 -ErrorAction SilentlyContinue | Where-Object Path -EQ $emulatorPath
if ($existing) {
    $existing | Select-Object Id,ProcessName,Path | ConvertTo-Json
    return
}
$emulatorProcess = Start-Process -FilePath $emulatorPath -ArgumentList $launchArguments -WorkingDirectory (Split-Path -Parent $emulatorPath) -WindowStyle Hidden -PassThru
$sessionDirectory = Join-Path $projectRoot 'work/scratch'
New-Item -ItemType Directory -Path $sessionDirectory -Force | Out-Null
[pscustomobject]@{ pid = $emulatorProcess.Id; game = $gameFullPath; graphics_option = $graphicsOption; started_utc = [DateTime]::UtcNow.ToString('o'); websocket = 'ws://127.0.0.1:19380/debugger' } | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $sessionDirectory 'ppsspp_session.json') -Encoding utf8
$emulatorProcess | Select-Object Id,ProcessName | ConvertTo-Json
