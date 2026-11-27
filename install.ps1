# Installer 1-langkah babydocs untuk Windows (PowerShell).
# - Auto-install Python 3.12 via winget jika belum ada
# - Otomatis menambahkan folder bin\ ke User PATH
# - Otomatis menghubungkan skill ke coding agent yang terdeteksi
$ErrorActionPreference = "Stop"
$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
$BinDir = Join-Path $Here "bin"

Write-Host ""
Write-Host "  babydocs - Pemasangan Otomatis (Windows)" -ForegroundColor Magenta
Write-Host ""

function Test-Python {
  foreach ($cmd in @("py", "python")) {
    if (Get-Command $cmd -ErrorAction SilentlyContinue) {
      $argsList = if ($cmd -eq "py") { @("-3", "-c", "import sys; sys.exit(0 if sys.version_info >= (3,8) else 1)") } `
                  else { @("-c", "import sys; sys.exit(0 if sys.version_info >= (3,8) else 1)") }
      & $cmd @argsList 2>$null
      if ($LASTEXITCODE -eq 0) { return $cmd }
    }
  }
  return $null
}

$py = Test-Python
if (-not $py) {
  Write-Host "Kebutuhan sistem (Python) belum terpasang. Memasang otomatis..." -ForegroundColor Yellow
  if (Get-Command winget -ErrorAction SilentlyContinue) {
    winget install -e --id Python.Python.3.12 --scope user --accept-source-agreements --accept-package-agreements
    $env:Path = [Environment]::GetEnvironmentVariable("Path", "User") + ";" + [Environment]::GetEnvironmentVariable("Path", "Machine")
    $py = Test-Python
  }
  if (-not $py) {
    Write-Host "Gagal memasang Python otomatis. Unduh dari https://www.python.org/downloads/ (centang 'Add Python to PATH') lalu jalankan ulang." -ForegroundColor Red
    exit 1
  }
}
Write-Host "[OK] Sistem siap ($py)" -ForegroundColor Green

# Tambahkan bin\ ke User PATH
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
if (-not $userPath) { $userPath = "" }
$parts = $userPath -split ";" | Where-Object { $_ -ne "" }
if ($parts -notcontains $BinDir) {
  $newPath = ($parts + $BinDir) -join ";"
  [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
  $env:Path = "$BinDir;$env:Path"
  Write-Host "[OK] Perintah 'babydocs' ditambahkan ke PATH" -ForegroundColor Green
} else {
  Write-Host "[OK] Perintah 'babydocs' sudah ada di PATH" -ForegroundColor Green
}

# Hubungkan skill ke coding agent yang terdeteksi
foreach ($rel in @(".gemini\antigravity", ".claude", ".gemini", ".codex", ".agents", ".cursor")) {
  $base = Join-Path $HOME $rel
  if (Test-Path $base) {
    $skillsDir = Join-Path $base "skills"
    New-Item -ItemType Directory -Force -Path $skillsDir | Out-Null
    $target = Join-Path $skillsDir "babydocs"
    if (-not (Test-Path $target)) {
      try {
        New-Item -ItemType Junction -Path $target -Target $Here | Out-Null
      } catch {
        Copy-Item -Recurse -Force $Here $target
      }
      Write-Host "[OK] Skill terhubung ke $target" -ForegroundColor Green
    }
  }
}

Write-Host ""
Write-Host "Selesai! Tutup lalu buka ulang terminal, kemudian coba:" -ForegroundColor Cyan
Write-Host "  babydocs --help"
Write-Host "  babydocs serve --open"
Write-Host ""
