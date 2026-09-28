param([switch]$Execute,[string]$GamePath='work/scratch/setup_candidate_0.1.6/Summon_Night_3_EN_0.1.6.iso',[string]$QaName='setup_qa_0.1.6')
$ErrorActionPreference='Stop'
$taskRoot=Split-Path -Parent $PSScriptRoot
if($QaName -notmatch '^setup_qa_[a-zA-Z0-9._-]+$'){throw 'Invalid QA directory name'}
$qaRoot=Join-Path $taskRoot ('work/scratch/'+$QaName)
$vendorRoot=Join-Path $PSScriptRoot 'vendor/ppsspp-1.20.4'
$gameFullPath=(Resolve-Path -LiteralPath (Join-Path $taskRoot $GamePath)).Path
$exe=Join-Path $qaRoot 'PPSSPPWindows64.exe'
$cfg=Join-Path $qaRoot 'setup.ini'
$launchArgs=@('--windowed','--graphics=software',('--config="'+$cfg+'"'),('"'+$gameFullPath+'"'))
[pscustomobject]@{Mode=$(if($Execute){'Launch'}else{'Dry run'});Game=$gameFullPath;IsolatedDirectory=$qaRoot;Port=19381;Arguments=$launchArgs}|ConvertTo-Json
if(-not $Execute){return}
if(Test-Path -LiteralPath $qaRoot){throw 'QA directory already exists'}
New-Item -ItemType Directory -Path (Join-Path $qaRoot 'memstick/PSP/SYSTEM') -Force|Out-Null
Copy-Item -LiteralPath (Join-Path $vendorRoot 'PPSSPPWindows64.exe') -Destination $exe
Copy-Item -LiteralPath (Join-Path $vendorRoot 'assets') -Destination $qaRoot -Recurse
@'
[General]
FirstRun=False
AutoRun=True
CheckForNewVersion=False
RemoteDebuggerOnStartup=True
RemoteDebuggerLocal=True
RemoteISOPort=19381
PauseOnLostFocus=False
PauseWhenMinimized=False
Language=en_US
[Graphics]
InternalResolution=1
[Sound]
Enable=False
'@ | Set-Content -LiteralPath $cfg -Encoding utf8
$proc=Start-Process -FilePath $exe -ArgumentList $launchArgs -WorkingDirectory $qaRoot -WindowStyle Hidden -PassThru
[pscustomobject]@{pid=$proc.Id;game=$gameFullPath;port=19381}|ConvertTo-Json|Set-Content -LiteralPath (Join-Path $qaRoot 'session.json') -Encoding utf8
$proc|Select-Object Id,Path|ConvertTo-Json
