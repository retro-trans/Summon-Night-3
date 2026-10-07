param([switch]$Execute,[switch]$State,[string]$Build='0.1.70',[int]$Port=19408,[string]$Case='pot071-normal')
$ErrorActionPreference='Stop'
$taskRoot=Split-Path -Parent $PSScriptRoot
$qaRoot=Join-Path $taskRoot ('work/scratch/'+$Case)
$vendorRoot=Join-Path $PSScriptRoot 'vendor/ppsspp-1.20.4'
$game=Join-Path $taskRoot ('work/output/'+$Build+'/Summon_Night_3_EN_'+$Build+'.iso')
$exe=Join-Path $qaRoot 'PPSSPPWindows64.exe'
$cfg=Join-Path $qaRoot 'strict.ini'
$launchArgs=@('--windowed','--graphics=software',('--config="'+$cfg+'"'),('--log="'+(Join-Path $qaRoot 'runtime.log')+'"'),('"'+$game+'"'))
if($State){$launchArgs+=('--state="'+(Join-Path $qaRoot 'memstick/PSP/PPSSPP_STATE/NPJH50380_2.00_0.ppst')+'"')}
[pscustomobject]@{Mode=$(if($Execute){'Launch'}else{'Preview'});Game=$game;IsolatedDirectory=$qaRoot;Port=$Port;Audio=$true;Arguments=$launchArgs}|ConvertTo-Json
if(-not $Execute){return}
if(Test-Path -LiteralPath $qaRoot){throw 'QA directory already exists'}
if(-not (Test-Path -LiteralPath $game)){throw 'Build missing'}
New-Item -ItemType Directory -Path (Join-Path $qaRoot 'memstick/PSP/SYSTEM') -Force|Out-Null
Copy-Item -LiteralPath (Join-Path $vendorRoot 'PPSSPPWindows64.exe') -Destination $exe
Copy-Item -LiteralPath (Join-Path $vendorRoot 'assets') -Destination $qaRoot -Recurse
$saveRoot=Join-Path $qaRoot 'memstick/PSP/SAVEDATA'
New-Item -ItemType Directory -Path $saveRoot -Force|Out-Null
Expand-Archive -LiteralPath (Join-Path $taskRoot 'work/incoming/sn3 save.zip') -DestinationPath $saveRoot
$stateRoot=Join-Path $qaRoot 'memstick/PSP/PPSSPP_STATE'
New-Item -ItemType Directory -Path $stateRoot -Force|Out-Null
Expand-Archive -LiteralPath (Join-Path $taskRoot 'work/incoming/sn3 crash savestate.zip') -DestinationPath $stateRoot
$config=(Get-Content -LiteralPath (Join-Path $taskRoot 'work/scratch/release055-runtime/strict.ini') -Raw).Replace('19392',[string]$Port).Replace('Enable=False','Enable=True')
$config|Set-Content -LiteralPath $cfg -Encoding utf8
$proc=Start-Process -FilePath $exe -ArgumentList $launchArgs -WorkingDirectory $qaRoot -WindowStyle Hidden -PassThru
[pscustomobject]@{pid=$proc.Id;iso=$game;fresh_boot=(-not $State);save_state_used=[bool]$State;audio_enabled=$true;port=$Port}|ConvertTo-Json|Set-Content -LiteralPath (Join-Path $qaRoot 'session.json') -Encoding utf8
$proc|Select-Object Id,Path|ConvertTo-Json
