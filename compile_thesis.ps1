# Parameters
$targetFile = "thesis_chapter_4_fa.tex"
$baseName = [System.IO.Path]::GetFileNameWithoutExtension($targetFile)
$cleanUp = $true # Set to $false if you want to keep auxiliary files

Write-Host "--- Starting LaTeX Compilation for $targetFile ---" -ForegroundColor Cyan

# Check if file exists
if (-not (Test-Path $targetFile)) {
    Write-Host "Error: $targetFile not found in current directory." -ForegroundColor Red
    exit 1
}

# 1. First Pass (Generates .aux and .toc)
Write-Host "[1/2] Running XeLaTeX (Pass 1)..." -ForegroundColor Yellow
xelatex -interaction=nonstopmode -halt-on-error $targetFile

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Compilation failed during the first pass. Check $baseName.log for details." -ForegroundColor Red
    exit $LASTEXITCODE
}

# 2. Second Pass (Resolves references and TOC)
Write-Host "[2/2] Running XeLaTeX (Pass 2)..." -ForegroundColor Yellow
xelatex -interaction=nonstopmode -halt-on-error $targetFile

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Compilation failed during the second pass." -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host "--- Compilation Successful! ---" -ForegroundColor Green
Write-Host "Generated: $baseName.pdf" -ForegroundColor White

# 3. Optional Cleanup
if ($cleanUp) {
    Write-Host "Cleaning up auxiliary files..." -ForegroundColor Gray
    $extensions = @(".aux", ".log", ".out", ".toc", ".synctex.gz", ".xdv")
    foreach ($ext in $extensions) {
        $file = "$baseName$ext"
        if (Test-Path $file) {
            Remove-Item $file -Force
        }
    }
}
