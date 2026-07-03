$ErrorActionPreference = "Stop"
$url = "http://localhost:8501"

function Wait-DemoUrl {
    param(
        [string]$TargetUrl,
        [int]$TimeoutSeconds = 45
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        try {
            $response = Invoke-WebRequest -Uri $TargetUrl -UseBasicParsing -TimeoutSec 3
            if ($response.StatusCode -lt 500) {
                return $true
            }
        } catch {
            Start-Sleep -Seconds 1
        }
    }
    return $false
}

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
}

$dockerOk = $false
try {
    docker compose config *> $null
    $dockerOk = ($LASTEXITCODE -eq 0)
} catch {
    $dockerOk = $false
}

if ($dockerOk) {
    docker compose up --build -d
} else {
    python -m pip install -r requirements.txt
    python scripts/prepare_demo_data.py
    Start-Process -WindowStyle Hidden -FilePath "python" -ArgumentList "-m", "streamlit", "run", "app.py", "--server.port", "8501"
}

if (Wait-DemoUrl -TargetUrl $url) {
    Start-Process $url
    Write-Host "Demo URL: $url"
} else {
    Write-Host "Demo is starting, open manually: $url"
}
