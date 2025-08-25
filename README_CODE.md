$out = "all_code.txt"
Remove-Item $out -ErrorAction SilentlyContinue

$files = Get-ChildItem -Path .\src -Recurse -Include *.ts,*.tsx,*.scss -File
$core = @(
  "vite.config.ts","index.html","nginx.conf","Dockerfile",
  "package.json","tsconfig.json","tsconfig.app.json","tsconfig.node.json",
  "eslint.config.js","README.md",".env.development.local"
) | ForEach-Object { Get-Item -ErrorAction SilentlyContinue $_ }

$files += $core
$files = $files | Where-Object { $_.FullName -notmatch '\\node_modules\\|\\dist\\|\\.git\\' -and $_.Name -ne 'package-lock.json' } | Sort-Object FullName

foreach ($f in $files) {
  Add-Content -Path $out -Value "`r`n`r`n/* ===== $($f.FullName) ===== */`r`n" -Encoding UTF8
  Get-Content -Path $f.FullName -Raw -Encoding UTF8 | Add-Content -Path $out -Encoding UTF8
}

"$($files.Count) файлов объединено -> $(Resolve-Path $out)"













$out = "backend_code.txt"
Remove-Item $out -ErrorAction SilentlyContinue

# какие файлы считаем "кодом"
$includes = @(
  "*.py","*.pyi","*.sql","*.j2","*.jinja2",
  "requirements*.txt","pyproject.toml","alembic.ini",
  "*.ini","*.toml","*.yaml","*.yml","*.cfg","*.json",
  "Dockerfile","docker-compose*.yml","docker-compose*.yaml","*.md","*.sh"
)

# что исключаем по пути
$excludeRe = '[\\/](__pycache__|\.pytest_cache|\.mypy_cache|\.ruff_cache|\.tox|\.git|\.svn|\.hg|\.idea|\.vscode|\.venv|venv|env|build|dist|site-packages)([\\/]|$)'

$files = Get-ChildItem -Recurse -File -Include $includes |
  Where-Object { $_.FullName -notmatch $excludeRe } |
  Sort-Object FullName

foreach ($f in $files) {
  Add-Content -Path $out -Value "`r`n`r`n/* ===== $($f.FullName) ===== */`r`n" -Encoding UTF8
  Get-Content -Path $f.FullName -Raw -Encoding UTF8 | Add-Content -Path $out -Encoding UTF8
}

"$($files.Count) файлов объединено -> $(Resolve-Path $out)"
