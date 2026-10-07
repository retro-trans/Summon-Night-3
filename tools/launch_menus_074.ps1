param([switch]$Execute,[string]$Iso='work/scratch/menus074-candidate1/Summon_Night_3_EN_0.1.74.iso',[int]$Port=19425,[string]$Case='menus074-candidate',[string]$State='',[string]$SaveRoot='work/scratch/release055-runtime/memstick/PSP/SAVEDATA')
$ErrorActionPreference='Stop'
$taskRoot=Split-Path -Parent $PSScriptRoot
$qaRoot=Join-Path $taskRoot ('work/scratch/'+$Case)
$vendorRoot=Join-Path $PSScriptRoot 'vendor/ppsspp-1.20.4'
$game=[IO.Path]::GetFullPath((Join-Path $taskRoot $Iso))
if(-not $game.StartsWith($taskRoot+[IO.Path]::DirectorySeparatorChar) -or $Case -notmatch '^menus074-[a-z0-9-]+$'){throw 'Outside scoped menu QA'}
$exe=Join-Path $qaRoot 'PPSSPPWindows64.exe'
$cfg=Join-Path $qaRoot 'strict.ini'
$launchArgs=@('--windowed','--graphics=software',('--config="'+$cfg+'"'),('--log="'+(Join-Path $qaRoot 'runtime.log')+'"'),('"'+$game+'"'))
if($State){$stateFile=[IO.Path]::GetFullPath((Join-Path $taskRoot $State));if(-not $stateFile.StartsWith($taskRoot+[IO.Path]::DirectorySeparatorChar) -or -not(Test-Path -LiteralPath $stateFile)){throw 'Invalid private diagnostic state'};$launchArgs+=('--state="'+$stateFile+'"')}
[pscustomobject]@{Mode=$(if($Execute){'Launch'}else{'Preview'});Game=$game;IsolatedDirectory=$qaRoot;Port=$Port;Audio=$true;Arguments=$launchArgs}|ConvertTo-Json
if(-not $Execute){return}
if(Get-Process -Name '*PPSSPP*' -ErrorAction SilentlyContinue){throw 'An emulator is already running. Keep only one instance; close the owned QA instance before launching another.'}
if(Test-Path -LiteralPath $qaRoot){throw 'QA directory already exists'}
if(-not (Test-Path -LiteralPath $game)){throw 'Candidate missing'}
New-Item -ItemType Directory -Path (Join-Path $qaRoot 'memstick/PSP/SYSTEM') -Force|Out-Null
Copy-Item -LiteralPath (Join-Path $vendorRoot 'PPSSPPWindows64.exe') -Destination $exe
Copy-Item -LiteralPath (Join-Path $vendorRoot 'assets') -Destination $qaRoot -Recurse
$saveSource=[IO.Path]::GetFullPath((Join-Path $taskRoot $SaveRoot));if(-not $saveSource.StartsWith($taskRoot+[IO.Path]::DirectorySeparatorChar)){throw 'Invalid private save source'}
Copy-Item -LiteralPath $saveSource -Destination (Join-Path $qaRoot 'memstick/PSP') -Recurse
$config=(Get-Content -LiteralPath (Join-Path $taskRoot 'work/scratch/release055-runtime/strict.ini') -Raw).Replace('19392',[string]$Port).Replace('Enable=False','Enable=True')
$config|Set-Content -LiteralPath $cfg -Encoding utf8
$proc=Start-Process -FilePath $exe -ArgumentList $launchArgs -WorkingDirectory $qaRoot -WindowStyle Hidden -PassThru
[pscustomobject]@{pid=$proc.Id;iso=$game;fresh_boot=(-not $State);save_state_used=[bool]$State;audio_enabled=$true;port=$Port}|ConvertTo-Json|Set-Content -LiteralPath (Join-Path $qaRoot 'session.json') -Encoding utf8
$proc|Select-Object Id,Path|ConvertTo-Json
