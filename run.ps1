# 가상환경 경로 설정
$venvPath = ""
if (Test-Path ".\.venv\Scripts\Activate.ps1") {
    $venvPath = ".\.venv\Scripts\Activate.ps1"
}
elseif (Test-Path ".\venv\Scripts\Activate.ps1") {
    $venvPath = ".\venv\Scripts\Activate.ps1"
} 

# 바로가기 생성
$shortcutPath = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\run_motion_records.lnk"
if (-Not (Test-Path $shortcutPath)) {
    $WScriptShell = New-Object -ComObject WScript.Shell
    $Shortcut = $WScriptShell.CreateShortcut($shortcutPath)
    if (Get-Command pwsh -ErrorAction SilentlyContinue) {
        $Shortcut.TargetPath = "pwsh"
    } else {
        $Shortcut.TargetPath = "powershell"
    }
    $Shortcut.Arguments = "-File `"$PSScriptRoot\run.ps1`""
    $Shortcut.Save()
}

# Install requirements
& pip install -r requirements.txt

# Activate virtual environment
& $venvPath

# main.py 실행
& python main.py

