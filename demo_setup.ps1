cd C:\Users\neuro\OneDrive\Desktop\hackathon
Start-Job -ScriptBlock {
    cd C:\Users\neuro\OneDrive\Desktop\hackathon
    python -m uvicorn backend.main:app --host 127.0.0.1 --port 8080
} | Out-Null
Start-Sleep -Seconds 5
Invoke-RestMethod -Uri http://localhost:8080/demo/generate