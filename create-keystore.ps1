<#
.SYNOPSIS
    Generates a release signing keystore for the Android build.

.DESCRIPTION
    Uses the Java keytool (bundled with the JDK / Android Studio) to create a
    new .jks keystore file. Run this once before doing a signed Android build.

.PARAMETER KeystoreFile
    Output path for the keystore. Default: .\robothri-release.jks

.PARAMETER Alias
    Key alias inside the keystore. Default: robothri

.PARAMETER ValidityDays
    Key validity in days. Default: 10000 (~27 years)

.EXAMPLE
    .\create-keystore.ps1
    .\create-keystore.ps1 -KeystoreFile .\my.jks -Alias mykey
#>

param(
    [string]$KeystoreFile = ".\robothri-release.jks",
    [string]$Alias        = "robothri",
    [int]   $ValidityDays = 10000
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Locate keytool
$keytool = Get-Command keytool -ErrorAction SilentlyContinue
if (-not $keytool) {
    # Try common JDK locations
    $candidates = @(
        "$env:JAVA_HOME\bin\keytool.exe",
        "$env:ANDROID_HOME\jdk\jdk-8.0.302.8-hotspot\bin\keytool.exe",
        "C:\Program Files\Android\Android Studio\jbr\bin\keytool.exe",
        "C:\Program Files\Microsoft\jdk-17*\bin\keytool.exe"
    )
    foreach ($c in $candidates) {
        $resolved = Resolve-Path $c -ErrorAction SilentlyContinue
        if ($resolved) { $keytool = $resolved; break }
    }
    if (-not $keytool) {
        Write-Error "keytool not found. Install the JDK or Android Studio and make sure JAVA_HOME is set."
        exit 1
    }
}

if (Test-Path $KeystoreFile) {
    Write-Warning "Keystore already exists at $KeystoreFile. Delete it first if you want to regenerate."
    exit 0
}

Write-Host "Creating keystore: $KeystoreFile  (alias: $Alias)" -ForegroundColor Cyan
Write-Host "You will be prompted for passwords and certificate details." -ForegroundColor DarkGray
Write-Host ""

& "$keytool" `
    -genkeypair `
    -v `
    -keystore "$KeystoreFile" `
    -alias "$Alias" `
    -keyalg RSA `
    -keysize 2048 `
    -validity $ValidityDays `
    -storetype JKS

if ($LASTEXITCODE -ne 0) {
    Write-Error "keytool failed."
    exit 1
}

Write-Host ""
Write-Host "✔ Keystore created: $((Resolve-Path $KeystoreFile).Path)" -ForegroundColor Green
Write-Host ""
Write-Host "Next: run a signed Android release with:" -ForegroundColor White
Write-Host "  .\release.ps1 -Platform Android -Signed ``" -ForegroundColor DarkGray
Write-Host "      -KeystorePath $KeystoreFile ``" -ForegroundColor DarkGray
Write-Host "      -KeystoreAlias $Alias" -ForegroundColor DarkGray
