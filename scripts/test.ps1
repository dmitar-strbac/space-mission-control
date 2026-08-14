$ErrorActionPreference = "Stop"

$testTargets = @(
    "packages/orbital-mechanics",
    "services/mission-service",
    "services/vehicle-service",
    "services/trajectory-service",
    "services/flight-dynamics-service",
    "services/communication-service",
    "services/telemetry-safety-service"
)

$root = Resolve-Path (Join-Path $PSScriptRoot "..")
$originalPythonPath = $env:PYTHONPATH

try {
    foreach ($target in $testTargets) {
        Write-Host ""
        Write-Host "=== Testing $target ===" -ForegroundColor Cyan

        $targetPath = (Resolve-Path (Join-Path $root $target)).Path

        Push-Location $targetPath

        try {
            # Ensure that this project's local packages take precedence over
            # identically named packages installed by other workspace members.
            $env:PYTHONPATH = $targetPath

            uv run python -m pytest

            if ($LASTEXITCODE -ne 0) {
                Write-Host ""
                Write-Host "Tests failed for $target." -ForegroundColor Red
                exit $LASTEXITCODE
            }
        }
        finally {
            Pop-Location
        }
    }

    Write-Host ""
    Write-Host "All test suites passed." -ForegroundColor Green
}
finally {
    $env:PYTHONPATH = $originalPythonPath
}
