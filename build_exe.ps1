# Jump Loop World - EXE 打包脚本
# 使用方法: 在 PowerShell 中运行 .\build_exe.ps1

$ErrorActionPreference = "Stop"

# 切换到脚本所在目录
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  Jump Loop World - EXE 打包工具" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# 检查 Python 是否可用
Write-Host "[1/5] 检查 Python 环境..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "      Python 版本: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "错误: 未找到 Python，请确保 Python 已安装并添加到 PATH" -ForegroundColor Red
    exit 1
}

# 安装/更新依赖
Write-Host ""
Write-Host "[2/5] 安装依赖..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet
python -m pip install -r requirements.txt --quiet
python -m pip install pyinstaller --quiet
Write-Host "      依赖安装完成" -ForegroundColor Green

# 生成精灵图（如果需要）
Write-Host ""
Write-Host "[3/5] 检查并生成精灵图..." -ForegroundColor Yellow
if (-not (Test-Path "assets\sprites\player\red_idle.png")) {
    Write-Host "      正在生成精灵图..." -ForegroundColor Yellow
    python generate_sprites.py
    Write-Host "      精灵图生成完成" -ForegroundColor Green
} else {
    Write-Host "      精灵图已存在，跳过生成" -ForegroundColor Green
}

# 清理旧的构建文件
Write-Host ""
Write-Host "[4/5] 清理旧的构建文件..." -ForegroundColor Yellow
if (Test-Path "build") {
    Remove-Item -Recurse -Force "build"
}
if (Test-Path "dist") {
    Remove-Item -Recurse -Force "dist"
}
Write-Host "      清理完成" -ForegroundColor Green

# 使用 spec 文件构建 EXE
Write-Host ""
Write-Host "[5/5] 构建 EXE 文件..." -ForegroundColor Yellow
Write-Host "      这可能需要几分钟时间，请耐心等待..." -ForegroundColor Gray

pyinstaller JumpLoopWorld.spec --noconfirm

# 检查构建结果
Write-Host ""
if (Test-Path "dist\JumpLoopWorld.exe") {
    $exeSize = (Get-Item "dist\JumpLoopWorld.exe").Length / 1MB
    $exeSizeStr = "{0:N2}" -f $exeSize
    
    Write-Host "======================================" -ForegroundColor Green
    Write-Host "  构建成功!" -ForegroundColor Green
    Write-Host "======================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "  输出文件: dist\JumpLoopWorld.exe" -ForegroundColor White
    Write-Host "  文件大小: $exeSizeStr MB" -ForegroundColor White
    Write-Host ""
    Write-Host "  你可以直接运行 dist\JumpLoopWorld.exe 来启动游戏" -ForegroundColor Cyan
    Write-Host "  或将该文件复制到任意位置分发给其他人" -ForegroundColor Cyan
    Write-Host ""
    
    # 询问是否立即运行
    $runNow = Read-Host "是否立即运行游戏? (Y/N)"
    if ($runNow -eq "Y" -or $runNow -eq "y") {
        Start-Process "dist\JumpLoopWorld.exe"
    }
} else {
    Write-Host "======================================" -ForegroundColor Red
    Write-Host "  构建失败!" -ForegroundColor Red
    Write-Host "======================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "  请检查上方的错误信息" -ForegroundColor Yellow
    Write-Host "  常见问题:" -ForegroundColor Yellow
    Write-Host "    - 确保所有依赖已正确安装" -ForegroundColor White
    Write-Host "    - 确保 assets 目录包含所有必要资源" -ForegroundColor White
    Write-Host "    - 尝试以管理员身份运行此脚本" -ForegroundColor White
    exit 1
}
