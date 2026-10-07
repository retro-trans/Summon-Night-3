param([switch]$Execute)
$ErrorActionPreference='Stop'
$taskRoot=Split-Path -Parent $PSScriptRoot
$qaRoot=Join-Path $taskRoot 'work/scratch/categories069-runtime'
$vendorRoot=Join-Path $PSScriptRoot 'vendor/ppsspp-1.20.4'
$game=Join-Path $taskRoot 'work/output/0.1.69/Summon_Night_3_EN_0.1.69.iso'
$exe=Join-Path $qaRoot 'PPSSPPWindows64.exe'
$cfg=Join-Path $qaRoot 'strict.ini'
$launchArgs=@('--windowed','--graphics=software',('--config="'+$cfg+'"'),('--log="'+(Join-Path $qaRoot 'runtime.log')+'"'),('"'+$game+'"'))
[pscustomobject]@{Mode=$(if($Execute){'Launch'}else{'Preview'});Game=$game;IsolatedDirectory=$qaRoot;Port=19406;Arguments=$launchArgs}|ConvertTo-Json
if(-not $Execute){return}
if(Test-Path -LiteralPath $qaRoot){throw 'QA directory already exists'}
if(-not (Test-Path -LiteralPath $game)){throw 'Candidate not built'}
New-Item -ItemType Directory -Path (Join-Path $qaRoot 'memstick/PSP/SYSTEM') -Force|Out-Null
Copy-Item -LiteralPath (Join-Path $vendorRoot 'PPSSPPWindows64.exe') -Destination $exe
Copy-Item -LiteralPath (Join-Path $vendorRoot 'assets') -Destination $qaRoot -Recurse
Copy-Item -LiteralPath (Join-Path $taskRoot 'work/scratch/release055-runtime/memstick/PSP/SAVEDATA') -Destination (Join-Path $qaRoot 'memstick/PSP') -Recurse
$config=(Get-Content -LiteralPath (Join-Path $taskRoot 'work/scratch/release055-runtime/strict.ini') -Raw).Replace('19392','19406')
$config|Set-Content -LiteralPath $cfg -Encoding utf8
$proc=Start-Process -FilePath $exe -ArgumentList $launchArgs -WorkingDirectory $qaRoot -WindowStyle Hidden -PassThru
[pscustomobject]@{pid=$proc.Id;iso=$game;fresh_boot=$true;save_state_used=$false;port=19406}|ConvertTo-Json|Set-Content -LiteralPath (Join-Path $qaRoot 'session.json') -Encoding utf8
$proc|Select-Object Id,Path|ConvertTo-Json
