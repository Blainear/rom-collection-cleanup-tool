#!/usr/bin/env pwsh

# Disable git pager
$env:GIT_PAGER = ""

# Stage all changes
Write-Host "Staging changes..."
git add .

# Commit with detailed message
Write-Host "Committing changes..."
git commit -m @"
Implement IGDB API integration for enhanced cross-language game matching

- Add intelligent game name matching using IGDB alternative names
- Sync CLI and GUI logic for consistent results  
- Add platform filtering for more accurate API queries
- Maintain graceful fallback when API unavailable
- Clean up debug code and test artifacts
- Remove hardcoded credentials for production readiness
"@

Write-Host "Commit completed! Ready to push to main branch."
Write-Host "To push: git push origin main"