param(
    [string]$Version = "1.2.0"
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$output = Join-Path $root "outputs"
$stage = Join-Path ([System.IO.Path]::GetTempPath()) ("mutube-build-" + [guid]::NewGuid())
$app = Join-Path $stage "MuTube"
New-Item -ItemType Directory -Force -Path $app, $output | Out-Null

Get-ChildItem -LiteralPath $root -Force | Where-Object {
    $_.Name -notin @('.git', 'outputs', 'downloads', '__pycache__', 'yt-dlp', 'ffmpeg', 'log.txt')
} | Copy-Item -Destination $app -Recurse -Force

Get-ChildItem -LiteralPath $app -Recurse -Force | Where-Object {
    $_.Name -eq '__pycache__' -or $_.Extension -eq '.pyc' -or $_.Name -in @('yt-dlp', 'ffmpeg', 'log.txt', 'yt_settings.json')
} | Remove-Item -Recurse -Force

$archive = Join-Path $output ("MuTube-$Version.muxapp")
if (Test-Path -LiteralPath $archive) { Remove-Item -LiteralPath $archive -Force }
Add-Type -AssemblyName System.IO.Compression.FileSystem
[System.IO.Compression.ZipFile]::CreateFromDirectory($app, $archive, [System.IO.Compression.CompressionLevel]::Optimal, $true)
Remove-Item -LiteralPath $stage -Recurse -Force
Write-Host "Created $archive"
