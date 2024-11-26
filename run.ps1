# 가상환경 경로 설정
$venvPath = ""
if (Test-Path ".\.venv\Scripts\Activate.ps1") {
    $venvPath = ".\.venv\Scripts\Activate.ps1"
}
elseif (Test-Path ".\venv\Scripts\Activate.ps1") {
    $venvPath = ".\venv\Scripts\Activate.ps1"
} 

# Activate virtual environment
& $venvPath

# main.py 실행
& python main.py
