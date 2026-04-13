$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$distRoot = Join-Path $projectRoot "dist"
$buildRoot = Join-Path $projectRoot "build"
$appDir = Join-Path $distRoot "GeoEnvironmentalAnalyzer"

Write-Host "Building Geo Environmental Analyzer..."
python -m PyInstaller --noconfirm --clean (Join-Path $projectRoot "GeoEnvironmentalAnalyzer.spec")

Write-Host "Copying runtime files..."
Copy-Item (Join-Path $projectRoot "settings.toml") $appDir -Force

$dataTarget = Join-Path $appDir "data"
New-Item -ItemType Directory -Force -Path $dataTarget | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $dataTarget "input") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $dataTarget "output") | Out-Null

Copy-Item (Join-Path $projectRoot "data\waters") $dataTarget -Recurse -Force
Copy-Item (Join-Path $projectRoot "data\RDOS") $dataTarget -Recurse -Force

$instructions = @"
Geo Environmental Analyzer

1. Uruchom GeoEnvironmentalAnalyzer.exe
2. Wybierz plik TXT ze wspolrzednymi
3. Kliknij "Generuj raport"
4. Gotowy plik XLSX zostanie zapisany we wskazanej lokalizacji
"@

Set-Content -Path (Join-Path $appDir "URUCHOM.txt") -Value $instructions -Encoding UTF8

$rootExe = Join-Path $distRoot "GeoEnvironmentalAnalyzer.exe"
if (Test-Path $rootExe) {
    Remove-Item $rootExe -Force
}

$rootSettings = Join-Path $distRoot "settings.toml"
if (Test-Path $rootSettings) {
    Remove-Item $rootSettings -Force
}

Write-Host "Build complete: $appDir"
