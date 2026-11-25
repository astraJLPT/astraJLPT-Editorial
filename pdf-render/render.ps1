param(
    [string[]]$Unit = @(),
    [ValidateSet('regular','norubi','both')][string]$Variant = 'both',
    [switch]$NoCompile
)
$ErrorActionPreference = 'Stop'
$rendererArgs = @('-B', (Join-Path $PSScriptRoot 'render.py'), '--variant', $Variant)
if ($Unit.Count) {
    foreach ($paperUnit in $Unit) { $rendererArgs += @('--unit', $paperUnit) }
} else { $rendererArgs += '--all' }
if ($NoCompile) { $rendererArgs += '--no-compile' }
& python @rendererArgs
if ($LASTEXITCODE) { throw 'Renderer failed; inspect pdf-render/work logs.' }
