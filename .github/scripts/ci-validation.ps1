<#
.SYNOPSIS
    Script de validation CI pour Scientific English Agents.
.DESCRIPTION
    Vérifie l'architecture des dossiers, la sécurité (fuite de clés) 
    et la validité syntaxique des scripts Python.
#>

$ErrorActionPreference = "Stop"
$exitCode = 0

Write-Host "[INFO] Demarrage de la validation CI..." -ForegroundColor Cyan

# 1. Vérification de la structure de base
$requiredPaths = @(
    "src/agents",
    "src/shared",
    "providers/anthropic/CLAUDE.md.template",
    "providers/mistral/MISTRAL.md.template"
)

Write-Host "`n[TEST] Verification de l'arborescence"
foreach ($path in $requiredPaths) {
    if (-Not (Test-Path $path)) {
        Write-Host "  [FAIL] Manquant : $path" -ForegroundColor Red
        $exitCode = 1
    } else {
        Write-Host "  [PASS] Trouve : $path"
    }
}

# 2. Audit de sécurité (Fuite de clés API)
Write-Host "`n[TEST] Scan de securite (.env et cles en dur)"
$envFiles = Get-ChildItem -Path . -Filter ".env" -Recurse -ErrorAction SilentlyContinue
if ($envFiles.Count -gt 0) {
    Write-Host "  [FAIL] Fichier(s) .env detecte(s) :" -ForegroundColor Red
    foreach ($file in $envFiles) {
        Write-Host "         -> $($file.FullName)" -ForegroundColor Yellow
    }
    $exitCode = 1
} else {
    Write-Host "  [PASS] Aucun fichier .env detecte."
}

# Recherche de clés Mistral/Anthropic avec Regex pour éviter les faux positifs dans la documentation
$suspiciousRegex = @(
    "sk-ant-api03-[a-zA-Z0-9\-_]{40,}",
    "MISTRAL_API_KEY=[a-zA-Z0-9]{25,}"
)

$filesToScan = Get-ChildItem -Path . -File -Recurse -Exclude "*.ps1", "*.yml", ".git*" -ErrorAction SilentlyContinue
$leakDetected = $false

foreach ($regex in $suspiciousRegex) {
    $leaks = $filesToScan | Select-String -Pattern $regex -ErrorAction SilentlyContinue
    if ($leaks) {
        Write-Host "  [FAIL] Vraie cle d'API potentielle detectee :" -ForegroundColor Red
        $leaks | ForEach-Object { Write-Host "         -> $($_.Filename) ligne $($_.LineNumber)" -ForegroundColor Yellow }
        $exitCode = 1
        $leakDetected = $true
    }
}

if (-Not $leakDetected) {
    Write-Host "  [PASS] Aucune vraie cle API en dur detectee."
}

# 3. Validation syntaxique Python
Write-Host "`n[TEST] Validation de la syntaxe Python"
$pythonScripts = Get-ChildItem -Path "providers/" -Filter "*.py" -Recurse -ErrorAction SilentlyContinue
if ($pythonScripts.Count -eq 0) {
    Write-Host "  [INFO] Aucun script Python trouve dans providers/."
} else {
    foreach ($script in $pythonScripts) {
        $pyCheck = python -m py_compile $script.FullName 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Host "  [FAIL] Erreur de syntaxe : $($script.Name)" -ForegroundColor Red
            Write-Host $pyCheck -ForegroundColor Yellow
            $exitCode = 1
        } else {
            Write-Host "  [PASS] Syntaxe OK : $($script.Name)"
        }
    }
}

Write-Host "`n[RESULTAT FINALE]" -ForegroundColor Cyan
if ($exitCode -ne 0) {
    Write-Host "ECHEC : Des erreurs bloquantes ont ete detectees." -ForegroundColor Red
    exit $exitCode
} else {
    Write-Host "SUCCES : Le projet est conforme." -ForegroundColor Green
}