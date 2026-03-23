<#
.SYNOPSIS
    Builds and publishes AIko - Robot HRI for Android and/or Windows.

.DESCRIPTION
    Produces release artifacts in the ./artifacts/ directory.
    For a signed Android build, supply the keystore parameters or create
    a keystore first with .\create-keystore.ps1.

.PARAMETER Platform
    Which platform to build: Android, Windows, or All (default: All)

.PARAMETER AndroidFormat
    Android output format: apk, aab, or both (default: apk)

.PARAMETER Signed
    Sign the Android APK/AAB with a release keystore (requires keystore params).

.PARAMETER KeystorePath
    Path to the .jks / .keystore file.

.PARAMETER KeystoreAlias
    The key alias inside the keystore.

.PARAMETER KeystorePass
    Keystore password (will prompt if -Signed and not supplied).

.PARAMETER KeyPass
    Key password (will prompt if -Signed and not supplied).

.PARAMETER DisplayVersion
    Override the app display version (e.g. "1.1"). Updates csproj automatically.

.PARAMETER BuildNumber
    Override the integer build number. Updates csproj automatically.

.EXAMPLE
    # Quick unsigned release for both platforms
    .\release.ps1

.EXAMPLE
    # Signed Android APK only, version 2.0
    .\release.ps1 -Platform Android -Signed -KeystorePath .\robothri.jks `
        -KeystoreAlias robothri -DisplayVersion "2.0" -BuildNumber 2

.EXAMPLE
    # Windows only
    .\release.ps1 -Platform Windows
#>

[CmdletBinding()]
param(
    [ValidateSet("Android","Windows","All")]
    [string]$Platform = "All",

    [ValidateSet("apk","aab","both")]
    [string]$AndroidFormat = "apk",

    [switch]$Signed,
    [string]$KeystorePath  = "",
    [string]$KeystoreAlias = "",
    [string]$KeystorePass  = "",
    [string]$KeyPass       = "",

    [string]$DisplayVersion = "",
    [int]$BuildNumber = 0
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# ── Paths ────────────────────────────────────────────────────────────────────
$root         = $PSScriptRoot
$projectDir   = Join-Path $root "RobotHri"
$csproj       = Join-Path $projectDir "RobotHri.csproj"
$artifactsDir = Join-Path $root "artifacts"

# ── Helpers ──────────────────────────────────────────────────────────────────
function Write-Header([string]$msg) {
    Write-Host ""
    Write-Host "----------------------------------------------------" -ForegroundColor Cyan
    Write-Host "  $msg" -ForegroundColor Cyan
    Write-Host "----------------------------------------------------" -ForegroundColor Cyan
}

function Write-Step([string]$msg) {
    Write-Host "  >> $msg" -ForegroundColor Yellow
}

function Write-Done([string]$msg) {
    Write-Host "  OK $msg" -ForegroundColor Green
}

function Write-Fail([string]$msg) {
    Write-Host "  FAIL $msg" -ForegroundColor Red
}

# ── Verify dotnet ─────────────────────────────────────────────────────────────
if (-not (Get-Command dotnet -ErrorAction SilentlyContinue)) {
    Write-Fail "dotnet CLI not found. Install the .NET 9 SDK from https://dot.net"
    exit 1
}

$sdkVer = & dotnet --version
Write-Host "Using .NET SDK $sdkVer" -ForegroundColor DarkGray

# ── Optional: bump version in csproj ─────────────────────────────────────────
if (($DisplayVersion -ne "") -or ($BuildNumber -gt 0)) {
    Write-Header "Updating Version"
    [xml]$proj = Get-Content $csproj -Encoding UTF8

    if ($DisplayVersion -ne "") {
        $node = $proj.SelectSingleNode("//ApplicationDisplayVersion")
        if ($node) { $node.InnerText = $DisplayVersion }
        Write-Step "ApplicationDisplayVersion => $DisplayVersion"
    }

    if ($BuildNumber -gt 0) {
        $node = $proj.SelectSingleNode("//ApplicationVersion")
        if ($node) { $node.InnerText = "$BuildNumber" }
        Write-Step "ApplicationVersion        => $BuildNumber"
    }

    $proj.Save($csproj)
    Write-Done "csproj updated."
}

# Read current version for labelling artifacts
[xml]$projRead = Get-Content $csproj -Encoding UTF8
$verNode = $projRead.SelectSingleNode("//ApplicationDisplayVersion")
$bldNode = $projRead.SelectSingleNode("//ApplicationVersion")
$ver = if ($verNode) { $verNode.InnerText } else { "1.0" }
$bld = if ($bldNode) { $bldNode.InnerText } else { "1" }
Write-Host "  Version: $ver  (build $bld)" -ForegroundColor DarkGray

# ── Prepare artifacts dir ────────────────────────────────────────────────────
$stamp      = Get-Date -Format "yyyyMMdd-HHmmss"
$releaseDir = Join-Path $artifactsDir "$ver+$bld-$stamp"
New-Item -ItemType Directory -Force -Path $releaseDir | Out-Null

# ── Android Build ─────────────────────────────────────────────────────────────
function Build-Android {
    param([string]$format)

    Write-Header "Building Android ($format)"

    $outDir = Join-Path $releaseDir "android-$format"
    New-Item -ItemType Directory -Force -Path $outDir | Out-Null

    $publishArgs = @(
        "publish"
        "-f", "net9.0-android"
        "-c", "Release"
        "-p:AndroidPackageFormats=$format"
        "--output", $outDir
    )

    if ($Signed) {
        if ($KeystorePath -eq "") {
            Write-Fail "-KeystorePath is required when using -Signed"
            exit 1
        }
        if (-not (Test-Path $KeystorePath)) {
            Write-Fail "Keystore file not found: $KeystorePath"
            exit 1
        }
        if ($KeystoreAlias -eq "") {
            Write-Fail "-KeystoreAlias is required when using -Signed"
            exit 1
        }

        $ksPass = $KeystorePass
        if ($ksPass -eq "") {
            $secPass = Read-Host "Keystore password" -AsSecureString
            $bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secPass)
            $ksPass = [Runtime.InteropServices.Marshal]::PtrToStringAuto($bstr)
        }

        $kp = $KeyPass
        if ($kp -eq "") {
            $secKP = Read-Host "Key password (press Enter to reuse keystore password)" -AsSecureString
            $bstrKP = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secKP)
            $kpRaw  = [Runtime.InteropServices.Marshal]::PtrToStringAuto($bstrKP)
            if ($kpRaw -ne "") {
                $kp = $kpRaw
            }
            else {
                $kp = $ksPass
            }
        }

        $absKs = (Resolve-Path $KeystorePath).Path
        $publishArgs += "-p:AndroidKeyStore=true"
        $publishArgs += "-p:AndroidSigningKeyStore=$absKs"
        $publishArgs += "-p:AndroidSigningKeyAlias=$KeystoreAlias"
        $publishArgs += "-p:AndroidSigningStorePass=$ksPass"
        $publishArgs += "-p:AndroidSigningKeyPass=$kp"
        Write-Step "Signing with keystore: $absKs  (alias: $KeystoreAlias)"
    }
    else {
        Write-Step "Unsigned build (debug-signed -- suitable for sideloading and testing)"
    }

    Write-Step "Running: dotnet $($publishArgs -join ' ')"
    Push-Location $projectDir
    try {
        & dotnet @publishArgs
        if ($LASTEXITCODE -ne 0) {
            throw "dotnet publish failed with exit code $LASTEXITCODE"
        }
    }
    finally {
        Pop-Location
    }

    # Collect artifacts
    $found = Get-ChildItem $outDir -Recurse -Filter "*.$format" -ErrorAction SilentlyContinue
    if (-not $found) {
        # MAUI may put the artifact in bin/Release/net9.0-android
        $fallback = Join-Path $projectDir "bin\Release\net9.0-android"
        $found = Get-ChildItem $fallback -Recurse -Filter "*.$format" -ErrorAction SilentlyContinue |
                 Sort-Object LastWriteTime -Descending | Select-Object -First 3
        foreach ($f in $found) {
            Copy-Item $f.FullName -Destination $outDir -Force
        }
        $found = Get-ChildItem $outDir -Recurse -Filter "*.$format" -ErrorAction SilentlyContinue
    }

    if ($found) {
        foreach ($f in $found) { Write-Done "Artifact: $($f.FullName)" }
    }
    else {
        Write-Host "  WARNING: No .$format file found -- check the build log above." -ForegroundColor DarkYellow
    }
}

# ── Windows Build ─────────────────────────────────────────────────────────────
function Build-Windows {
    Write-Header "Building Windows (unpackaged EXE)"

    $outDir = Join-Path $releaseDir "windows"
    New-Item -ItemType Directory -Force -Path $outDir | Out-Null

    $publishArgs = @(
        "publish"
        "-f", "net9.0-windows10.0.19041.0"
        "-c", "Release"
        "--output", $outDir
    )

    Write-Step "Running: dotnet $($publishArgs -join ' ')"
    Push-Location $projectDir
    try {
        & dotnet @publishArgs
        if ($LASTEXITCODE -ne 0) {
            throw "dotnet publish failed with exit code $LASTEXITCODE"
        }
    }
    finally {
        Pop-Location
    }

    $exe = Get-ChildItem $outDir -Filter "*.exe" |
           Where-Object { $_.Name -notmatch 'createdump' } |
           Sort-Object LastWriteTime -Descending |
           Select-Object -First 1
    if ($exe) {
        Write-Done "Artifact: $($exe.FullName)"
    }
    else {
        Write-Host "  WARNING: No .exe found in output -- check the build log above." -ForegroundColor DarkYellow
    }
}

# ── Dispatch ──────────────────────────────────────────────────────────────────
if ($Platform -eq "Android") {
    if ($AndroidFormat -eq "both") {
        Build-Android -format "apk"
        Build-Android -format "aab"
    }
    else {
        Build-Android -format $AndroidFormat
    }
}
elseif ($Platform -eq "Windows") {
    Build-Windows
}
else {
    # All
    if ($AndroidFormat -eq "both") {
        Build-Android -format "apk"
        Build-Android -format "aab"
    }
    else {
        Build-Android -format $AndroidFormat
    }
    Build-Windows
}

# ── Summary ───────────────────────────────────────────────────────────────────
Write-Header "Release Complete"
Write-Host "  Output folder: $releaseDir" -ForegroundColor White
$allFiles = Get-ChildItem $releaseDir -Recurse -File -ErrorAction SilentlyContinue
foreach ($f in $allFiles) {
    $rel = $f.FullName.Replace($releaseDir, "").TrimStart("\")
    Write-Host "    $rel" -ForegroundColor DarkGray
}
Write-Host ""
