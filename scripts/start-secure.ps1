param(
    [Parameter(Mandatory=$true)][string]$HostIp,
    [int]$Port = 8080
)

$ErrorActionPreference = "Stop"
$exe = $env:LAI_LLAMA_SERVER
$keyFile = $env:LAI_API_KEY_FILE_WINDOWS
$model = if ($env:LAI_MODEL) { $env:LAI_MODEL } else { "mistralai/Ministral-3-8B-Instruct-2512-GGUF:Q4_K_M" }
$chatTemplate = $env:LAI_CHAT_TEMPLATE
$logDir = if ($env:LAI_LOG_DIR) { $env:LAI_LOG_DIR } else { Join-Path $env:LOCALAPPDATA "lai-local-agent" }
$ctxSize = if ($env:LAI_CTX_SIZE) { $env:LAI_CTX_SIZE } else { "4096" }
$gpuLayers = if ($env:LAI_GPU_LAYERS) { $env:LAI_GPU_LAYERS } else { "0" }
$parallel = if ($env:LAI_PARALLEL) { $env:LAI_PARALLEL } else { "1" }

if (-not $exe -or -not (Test-Path $exe)) { throw "Set LAI_LLAMA_SERVER to llama-server.exe." }
if (-not $keyFile -or -not (Test-Path $keyFile)) { throw "Set LAI_API_KEY_FILE_WINDOWS to a key file." }

$helpText = (& $exe --help 2>&1 | Out-String)
$argsList = @()
if (Test-Path -LiteralPath $model -PathType Leaf) {
    $argsList += @("--model", $model)
} else {
    $argsList += @("-hf", $model, "--no-mmproj")
}
$argsList += @(
    "--host", $HostIp, "--port", "$Port",
    "--ctx-size", $ctxSize, "--gpu-layers", $gpuLayers, "--parallel", $parallel,
    "--flash-attn", "on", "--cache-type-k", "q8_0", "--cache-type-v", "q8_0",
    "--jinja", "--load-mode", "none"
)

if ($chatTemplate) {
    if (-not (Test-Path $chatTemplate)) { throw "LAI_CHAT_TEMPLATE does not exist." }
    $argsList += @("--chat-template-file", $chatTemplate)
}

if ($helpText -match "--api-key-file") {
    $argsList += @("--api-key-file", $keyFile)
} else {
    throw "This llama-server build does not support --api-key-file authentication."
}
if ($helpText -match "--no-webui") { $argsList += "--no-webui" }
if ($helpText -match "(?m)^\s*--metrics\b") { $argsList += "--metrics" }

New-Item -ItemType Directory -Force -Path $logDir | Out-Null
Start-Process -FilePath $exe -ArgumentList $argsList `
    -RedirectStandardOutput (Join-Path $logDir "server.out.log") `
    -RedirectStandardError (Join-Path $logDir "server.err.log") `
    -WindowStyle Hidden
Write-Output "LAI_LLAMA_SERVER_STARTED"
