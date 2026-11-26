$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$python = 'C:\Users\DESKTOP\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
if (!(Test-Path $python)) { $python = (Get-Command python -ErrorAction SilentlyContinue).Source }
if (!$python) { throw 'Python não encontrado.' }

if (!(Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
  Write-Host 'FFmpeg não encontrado. Instale FFmpeg e adicione-o ao PATH; depois execute novamente.' -ForegroundColor Yellow
  exit 2
}

& $python -m pip install -r (Join-Path $root 'requirements.txt')
Start-Process -WindowStyle Hidden -FilePath $python -ArgumentList (Join-Path $root 'app.py') -WorkingDirectory $root
Start-Sleep -Seconds 1
Start-Process 'http://127.0.0.1:8765'
Write-Host 'Fábrica iniciada em http://127.0.0.1:8765'

