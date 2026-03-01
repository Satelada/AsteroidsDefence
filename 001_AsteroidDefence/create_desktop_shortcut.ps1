$WshShell = New-Object -ComObject WScript.Shell
$Desktop = [Environment]::GetFolderPath("Desktop")
$Shortcut = $WshShell.CreateShortcut((Join-Path $Desktop "Falling Asteroids.lnk"))
$Shortcut.TargetPath = Join-Path $PSScriptRoot "Start_Falling_Asteroids.bat"
$Shortcut.WorkingDirectory = $PSScriptRoot
$Shortcut.Description = "Falling Asteroids"
$Shortcut.Save()
Write-Host "Desktop-Verknuepfung erstellt: $($Shortcut.FullName)"
