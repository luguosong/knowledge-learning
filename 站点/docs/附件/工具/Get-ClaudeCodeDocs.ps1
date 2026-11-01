[CmdletBinding()]
param(
    [string]$Language = 'all',
    [string]$OutDir = (Join-Path $PSScriptRoot ('claude-code-docs-' + $Language)),
    [switch]$ListOnly
)

$ErrorActionPreference = 'Stop'
$baseUrl = 'https://code.claude.com/docs/'

function Get-DocumentationResponse([string]$Url) {
    for ($attempt = 1; $attempt -le 3; $attempt++) {
        try {
            $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 60
            if ([string]$response.Headers['Content-Type'] -match 'text/html') {
                throw "Expected documentation text but received HTML: $Url"
            }
            return $response
        }
        catch {
            if ($attempt -eq 3) { throw }
            Start-Sleep -Seconds ($attempt * 2)
        }
    }
}

# Follow every generated index, including nested /_llms/ indexes.
$pending = [System.Collections.Generic.Queue[string]]::new()
$visited = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::Ordinal)
$pages = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::Ordinal)
$pending.Enqueue($baseUrl + 'llms.txt')
while ($pending.Count -gt 0) {
    $indexUrl = $pending.Dequeue()
    if (-not $visited.Add($indexUrl)) { continue }
    $indexText = [string](Get-DocumentationResponse $indexUrl).Content
    foreach ($link in [regex]::Matches($indexText, 'https://code\.claude\.com/docs/[^\s)<>]+')) {
        $url = $link.Value
        if ($url -match '/_llms/.*\.(txt|md)$') {
            $pending.Enqueue($url)
        }
        elseif ($url -match '\.md$') {
            [void]$pages.Add($url)
        }
    }
}

$selected = @($pages | Where-Object {
    $pageLanguage = ([uri]$_).AbsolutePath.Split('/')[2]
    $Language -eq 'all' -or $pageLanguage -eq $Language
} | Sort-Object)
if ($selected.Count -eq 0) { throw "No indexed pages match language '$Language'." }
Write-Host "Discovered $($pages.Count) pages; selected $($selected.Count) pages."
if ($ListOnly) { $selected; return }

$outputRoot = [System.IO.Path]::GetFullPath($OutDir)
[void][System.IO.Directory]::CreateDirectory($outputRoot)
$utf8 = [System.Text.UTF8Encoding]::new($false)
$results = [System.Collections.Generic.List[object]]::new()
foreach ($url in $selected) {
    $relativePath = ([uri]$url).AbsolutePath.Substring('/docs/'.Length)
    $destination = [System.IO.Path]::GetFullPath((Join-Path $outputRoot $relativePath))
    if (-not $destination.StartsWith($outputRoot.TrimEnd('\', '/') + [System.IO.Path]::DirectorySeparatorChar,
            [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Destination is outside output directory: $destination"
    }
    try {
        $response = Get-DocumentationResponse $url
        [void][System.IO.Directory]::CreateDirectory([System.IO.Path]::GetDirectoryName($destination))
        [System.IO.File]::WriteAllText($destination, [string]$response.Content, $utf8)
        $results.Add([pscustomobject]@{Url=$url; File=$relativePath; Status='ok'; Error=''})
        Write-Host "Saved $relativePath"
    }
    catch {
        $results.Add([pscustomobject]@{Url=$url; File=$relativePath; Status='failed'; Error=$_.Exception.Message})
        Write-Warning "Failed: $url - $($_.Exception.Message)"
    }
    Start-Sleep -Milliseconds 300
}
$manifestPath = Join-Path $outputRoot 'manifest.csv'
$results | Export-Csv -LiteralPath $manifestPath -NoTypeInformation -Encoding UTF8
$failed = @($results | Where-Object Status -eq 'failed')
Write-Host "Saved $($selected.Count - $failed.Count) / $($selected.Count) pages to $outputRoot"
Write-Host "Manifest: $manifestPath"
if ($failed.Count -gt 0) { throw "$($failed.Count) downloads failed. See manifest.csv; rerun to retry." }
