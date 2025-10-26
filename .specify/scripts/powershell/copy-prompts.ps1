# Copy .codex/prompts/ to C:\Users\kbpsh\.codex\prompts

# Source directory (relative path)
$sourceDir = ".codex\prompts"

# Target directories (absolute paths)
$targetDirs = @(
    "C:\Users\kbpsh\.codex\prompts",
    "\\wsl.localhost\Ubuntu-24.04\home\smorce\.codex\prompts"
)

# Get current directory
$currentDir = Get-Location

# Build absolute path for source directory
$sourcePath = Join-Path $currentDir $sourceDir

Write-Host "Source: $sourcePath" -ForegroundColor Green

# Check if source directory exists
if (-not (Test-Path $sourcePath)) {
    Write-Error "Source directory not found: $sourcePath"
    exit 1
}

# Loop through each target directory
foreach ($targetDir in $targetDirs) {
    Write-Host "--------------------------------------------------" -ForegroundColor Magenta
    Write-Host "Processing Target: $targetDir" -ForegroundColor Green

    # Create target directory if it doesn't exist
    if (-not (Test-Path $targetDir)) {
        Write-Host "Creating target directory: $targetDir" -ForegroundColor Yellow
        try {
            New-Item -ItemType Directory -Path $targetDir -Force -ErrorAction Stop | Out-Null
        } catch {
            Write-Error "Failed to create target directory '$targetDir'. Error: $($_.Exception.Message)"
            continue # Skip to the next target
        }
    }

    # Execute copy operation
    Write-Host "Copying files..." -ForegroundColor Cyan
    try {
        # Copy all files and subdirectories, overwriting existing files
        Copy-Item -Path "$sourcePath\*" -Destination $targetDir -Recurse -Force -ErrorAction Stop
        
        Write-Host "Copy completed!" -ForegroundColor Green
        
        # Display list of copied files
        $copiedFiles = Get-ChildItem -Path $targetDir -Recurse -File
        Write-Host "`nCopied files in '$targetDir':" -ForegroundColor Cyan
        foreach ($file in $copiedFiles) {
            Write-Host "  - $($file.Name)" -ForegroundColor White
        }
        
    } catch {
        Write-Error "Error occurred during copy to '$targetDir': $($_.Exception.Message)"
    }
    Write-Host "--------------------------------------------------" -ForegroundColor Magenta
    Write-Host ""
}
