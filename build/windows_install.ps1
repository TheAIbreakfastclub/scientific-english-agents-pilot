# Go to project root
Set-Location -Path "$PSScriptRoot\.."

Clear-Host
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host "  Scientific English Agents (v3.0.0) Setup           " -ForegroundColor Cyan
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Select AI Provider:" -ForegroundColor Yellow
Write-Host "A: Claude Code (Recommended for Mac/Win, needs Node.js)"
Write-Host "B: Mistral (EU-hosted, needs Python 3.8 - 3.12)"
$choice = Read-Host "Choice (A/B)"

if ($choice -match "^[Aa]$") {
    Write-Host "`n[+] Setting up Claude Code..." -ForegroundColor Cyan
    npm install -g @anthropic-ai/claude-code
    Copy-Item -Path "providers\anthropic\CLAUDE.md.template" -Destination "CLAUDE.md" -Force

    $apiKey = Read-Host "Enter Anthropic API key (sk-ant-...)"
    $envContent = "ANTHROPIC_API_KEY=$apiKey`nPROVIDER=anthropic"
    Set-Content -Path ".env" -Value $envContent

    Write-Host "`nDone! ✅ Configure CLAUDE.md and run 'claude'." -ForegroundColor Green

} elseif ($choice -match "^[Bb]$") {
    Write-Host "`n[+] Checking Python version..." -ForegroundColor Cyan

    $pyVersionStr = python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>$null

    if ($pyVersionStr) {
        $pyParts = $pyVersionStr.Split('.')
        $major = [int]$pyParts[0]
        $minor = [int]$pyParts[1]

        if ($major -ne 3 -or $minor -lt 8 -or $minor -gt 12) {
            Write-Host "WARNING: Python version must be between 3.8 and 3.12. You have $pyVersionStr." -ForegroundColor Red
            Write-Host "Dependencies (like opentelemetry) may fail on Python 3.13+." -ForegroundColor Yellow
            $cont = Read-Host "Continue anyway? (Y/N)"
            if ($cont -notmatch "^[Yy]$") {
                Write-Host "Exiting."
                exit
            }
        } else {
            Write-Host "Python $pyVersionStr detected. Perfect!" -ForegroundColor Green
        }
    } else {
        Write-Host "WARNING: Python command not found. Please install Python and add it to PATH." -ForegroundColor Red
        exit
    }

    Write-Host "`n[+] Setting up Mistral..." -ForegroundColor Cyan
    pip install mistralai python-dotenv
    Copy-Item -Path "providers\mistral\MISTRAL.md.template" -Destination "MISTRAL.md" -Force

    $apiKey = Read-Host "Enter Mistral API key"
    $envContent = "MISTRAL_API_KEY=$apiKey`nMISTRAL_MODEL=mistral-large-latest`nPROVIDER=mistral"
    Set-Content -Path ".env" -Value $envContent

    Write-Host "`nDone! ✅ Configure MISTRAL.md and run 'python providers\mistral\session.py'." -ForegroundColor Green

} else {
    Write-Host "Invalid choice. Exiting." -ForegroundColor Red
}

Write-Host "`nPress Enter to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
