param([string]$Version = "1.2.0")
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$out = Join-Path $root "outputs"
$stage = Join-Path ([IO.Path]::GetTempPath()) ("mutube-portmaster-" + [guid]::NewGuid())
$port = Join-Path $stage "mutube"
New-Item -ItemType Directory -Force -Path $port, $out | Out-Null

# PortMaster ZIP root: launcher plus port directory. Metadata is inside it.
Copy-Item -LiteralPath (Join-Path $root "port\mutube\MuTube.sh") -Destination $stage
Copy-Item -LiteralPath (Join-Path $root "port\mutube\port.json") -Destination $port
Copy-Item -LiteralPath (Join-Path $root "port\mutube\README.md") -Destination $port
Copy-Item -LiteralPath (Join-Path $root "port\mutube\gameinfo.xml") -Destination $port
Copy-Item -LiteralPath (Join-Path $root "port\mutube\screenshot.png") -Destination $port
Copy-Item -LiteralPath (Join-Path $root "port\mutube\licenses") -Destination $port -Recurse

Get-ChildItem -LiteralPath $root -Force | Where-Object {
  $_.Name -notin @('.git','.gitignore','outputs','downloads','port','__pycache__','yt-dlp','ffmpeg','log.txt','mux_launch.sh','build_portmaster.ps1','build_portmaster.sh','build_muxapp.ps1','build_muxapp.sh','build_muxapp.bat')
} | Copy-Item -Destination $port -Recurse -Force
Get-ChildItem -LiteralPath $port -Recurse -Force | Where-Object {
  $_.Name -eq '__pycache__' -or $_.Extension -eq '.pyc' -or $_.Name -in @('yt-dlp','ffmpeg','log.txt','yt_settings.json')
} | Remove-Item -Recurse -Force

$zip = Join-Path $out ("MuTube-PortMaster-$Version.zip")
if (Test-Path $zip) { Remove-Item $zip -Force }
Add-Type -AssemblyName System.IO.Compression.FileSystem
[IO.Compression.ZipFile]::CreateFromDirectory($stage, $zip, [IO.Compression.CompressionLevel]::Optimal, $false)
Remove-Item $stage -Recurse -Force
Write-Host "Created $zip"
