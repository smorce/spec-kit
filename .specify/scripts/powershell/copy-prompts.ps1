# Copy .codex/prompts/ to C:\Users\kbpsh\.codex\prompts

# Source directory (relative path)
$sourceDir = ".codex\prompts"

# Target directory (absolute path)
$targetDir = "C:\Users\kbpsh\.codex\prompts"

# Get current directory
$currentDir = Get-Location

# Build absolute path for source directory
$sourcePath = Join-Path $currentDir $sourceDir

Write-Host "Source: $sourcePath" -ForegroundColor Green
Write-Host "Target: $targetDir" -ForegroundColor Green

# Check if source directory exists
if (-not (Test-Path $sourcePath)) {
    Write-Error "Source directory not found: $sourcePath"
    exit 1
}

# Create target directory if it doesn't exist
if (-not (Test-Path $targetDir)) {
    Write-Host "Creating target directory: $targetDir" -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
}

# Execute copy operation
Write-Host "Copying files..." -ForegroundColor Cyan
try {
    # Copy all files and subdirectories, overwriting existing files
    Copy-Item -Path "$sourcePath\*" -Destination $targetDir -Recurse -Force
    
    Write-Host "Copy completed!" -ForegroundColor Green
    
    # Display list of copied files
    $copiedFiles = Get-ChildItem -Path $targetDir -Recurse -File
    Write-Host "`nCopied files:" -ForegroundColor Cyan
    foreach ($file in $copiedFiles) {
        Write-Host "  - $($file.Name)" -ForegroundColor White
    }
    
} catch {
    Write-Error "Error occurred during copy: $($_.Exception.Message)"
    exit 1
}
