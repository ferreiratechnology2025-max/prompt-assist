@echo off
echo === QualiPrompt - Ollama Setup ===
echo.

REM Verificar se Ollama esta instalado
where ollama >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERRO] Ollama nao encontrado. Instale de https://ollama.com/download/windows
    exit /b 1
)

echo [OK] Ollama encontrado.

REM Verificar se o modelo base existe
ollama list | findstr "qwen2.5:14b" >nul
if %errorlevel% neq 0 (
    echo [INFO] Baixando qwen2.5:14b (pode levar varios minutos)...
    ollama pull qwen2.5:14b
)

REM Criar Modelfile customizado
echo [INFO] Criando Modelfile customizado...
copy NUL Modelfile.qualiprompt >nul

REM Escrever Modelfile
(
echo FROM qwen2.5:14b
echo.
echo PARAMETER temperature 0.2
echo PARAMETER top_p 0.9
echo PARAMETER top_k 40
echo PARAMETER repeat_penalty 1.1
echo PARAMETER num_ctx 8192
echo.
echo SYSTEM """Voce e um engenheiro de prompts especialista. Sua funcao e criar prompts estruturados, precisos e otimizados seguindo rigorosamente as melhores praticas. Voce prioriza clareza, especificidade e acionabilidade. Nunca usa termos ambigueos. Sempre inclui formato de saida estruturado. Sempre adiciona instrucoes negativas."""
) > Modelfile.qualiprompt

echo [INFO] Criando modelo customizado qualiprompt-engine...
ollama create qualiprompt-engine -f Modelfile.qualiprompt

echo.
echo === VERIFICACAO ===
ollama list | findstr "qualiprompt-engine" >nul
if %errorlevel% equ 0 (
    echo [OK] Modelo qualiprompt-engine instalado
) else (
    echo [ERRO] Modelo nao encontrado
)

echo.
echo === Setup concluido ===
echo Execute: ollama run qualiprompt-engine
