$ErrorActionPreference = "Stop"

$distros = @(& wsl.exe -l -q) | ForEach-Object { $_.Trim() } | Where-Object { $_ }
if (-not $distros -or $distros.Count -eq 0) { throw "No WSL distribution is registered." }

$distro = $distros | Where-Object { $_ -eq "Ubuntu" } | Select-Object -First 1
if (-not $distro) { $distro = $distros | Where-Object { $_ -like "Ubuntu*" } | Select-Object -First 1 }
if (-not $distro) { $distro = $distros | Select-Object -First 1 }

$startup = [Environment]::GetFolderPath("Startup")
if (-not $startup) { throw "Could not resolve the current user's Startup folder." }

$launcher = Join-Path $startup "AMX-BLACK-WSL.cmd"
$body = @"
@echo off
start "" /min wsl.exe -d "$distro" --exec /bin/true
"@
Set-Content -LiteralPath $launcher -Value $body -Encoding ASCII

# Start/verify now as well. The enabled Linux systemd unit remains the worker supervisor.
& wsl.exe -d $distro --exec /bin/sh -lc "systemctl start amx-black.service >/dev/null 2>&1 || true"
$enabled = (& wsl.exe -d $distro --exec systemctl is-enabled amx-black.service 2>$null | Out-String).Trim()
$active  = (& wsl.exe -d $distro --exec systemctl is-active  amx-black.service 2>$null | Out-String).Trim()

[ordered]@{
  state = "WINDOWS_WSL_AUTOSTART_INSTALLED"
  distro = $distro
  launcher = $launcher
  linux_service_enabled = $enabled
  linux_service_active = $active
} | ConvertTo-Json -Compress
