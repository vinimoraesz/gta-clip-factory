$python = 'C:\Users\DESKTOP\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
$app = Join-Path $PSScriptRoot 'app.py'
Start-Process -WindowStyle Hidden -FilePath $python -ArgumentList $app -WorkingDirectory $PSScriptRoot
Start-Sleep -Milliseconds 500
Start-Process 'http://127.0.0.1:8765'

