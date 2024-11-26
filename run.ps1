# Activate virtual environment
& ".\.venv\Scripts\Activate.ps1"

# main.py 실행
$process = Start-Process -FilePath "python" -ArgumentList "main.py" -PassThru

Write-Host "main.py is running. Press 'q' to quit."

# 'q' 키 입력 대기
while ($true) {
    if ($Host.UI.RawUI.KeyAvailable) {
        $key = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        if ($key.Character -eq 'q') {
            break
        }
    }
    Start-Sleep -Milliseconds 100
}

# 프로세스 종료
$process.Kill()
Write-Host "main.py has been terminated."
