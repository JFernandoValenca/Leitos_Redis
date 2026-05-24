Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Medi CLOUD - Iniciando sistema...   " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/4] Verificando Docker..." -ForegroundColor Yellow
$dockerStatus = docker info 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "      ERRO: Docker nao esta rodando!" -ForegroundColor Red
    Write-Host "      Abra o Docker Desktop e tente novamente." -ForegroundColor Red
    Read-Host "Pressione ENTER para sair"
    exit 1
}
Write-Host "      Docker OK" -ForegroundColor Green

Write-Host ""
Write-Host "[2/4] Iniciando Redis..." -ForegroundColor Yellow
$redisStatus = docker start redis 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "      Redis iniciado com sucesso" -ForegroundColor Green
} else {
    Write-Host "      Criando container Redis..." -ForegroundColor Yellow
    docker run -d --name redis -p 6379:6379 -v redis-data:/data redis:latest 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "      Container Redis criado!" -ForegroundColor Green
    } else {
        Write-Host "      ERRO ao iniciar o Redis!" -ForegroundColor Red
        Read-Host "Pressione ENTER para sair"
        exit 1
    }
}

Write-Host ""
Write-Host "[3/4] Aguardando Redis ficar pronto..." -ForegroundColor Yellow
$tentativas = 0
$redisOk = $false
while ($tentativas -lt 10) {
    Start-Sleep -Seconds 1
    $ping = docker exec redis redis-cli ping 2>&1
    if ($ping -eq "PONG") {
        $redisOk = $true
        Write-Host "      Redis pronto!" -ForegroundColor Green
        break
    }
    $tentativas++
    Write-Host "      Aguardando... ($tentativas/10)" -ForegroundColor DarkYellow
}

Write-Host ""
Write-Host "[4/4] Iniciando FastAPI..." -ForegroundColor Yellow
$venvPath = ".venv311\Scripts\Activate.ps1"
if (Test-Path $venvPath) {
    & $venvPath
    Write-Host "      Ambiente virtual ativado" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Acesse: http://127.0.0.1:8000       " -ForegroundColor Cyan
Write-Host "   CTRL+C para encerrar                " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

uvicorn main:app --reload
