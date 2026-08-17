# Optional: clear runtime test clutter (uploads, job reports, job history)
# Safe to run before viva — demo accounts are re-seeded on backend restart.

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$ArchiveRoot = Split-Path -Parent $ProjectRoot | Join-Path -ChildPath "_archive\integration-test-artifacts"

$uploadArchive = Join-Path $ArchiveRoot "uploads"
$jobArchive = Join-Path $ArchiveRoot "job-results"
New-Item -ItemType Directory -Force -Path $uploadArchive, $jobArchive | Out-Null

$movedUploads = 0
Get-ChildItem (Join-Path $ProjectRoot "uploads") -File -ErrorAction SilentlyContinue | ForEach-Object {
    Move-Item $_.FullName $uploadArchive -Force
    $movedUploads++
}

$movedJobs = 0
Get-ChildItem (Join-Path $ProjectRoot "results\jobs") -Directory -ErrorAction SilentlyContinue | ForEach-Object {
    Move-Item $_.FullName $jobArchive -Force
    $movedJobs++
}

Set-Content -Path (Join-Path $ProjectRoot "uploads\.gitkeep") -Value "" -Encoding utf8
Set-Content -Path (Join-Path $ProjectRoot "jobs.json") -Value "[]" -Encoding utf8

Write-Host "Archived $movedUploads upload(s) and $movedJobs job result folder(s) to:"
Write-Host "  $ArchiveRoot"
Write-Host "jobs.json reset to []. Restart backend to re-seed demo users if needed."
