# React + TypeScript + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## Expanding the ESLint configuration

If you are developing a production application, we recommend updating the configuration to enable type-aware lint rules:

```js
export default tseslint.config([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...

      // Remove tseslint.configs.recommended and replace with this
      ...tseslint.configs.recommendedTypeChecked,
      // Alternatively, use this for stricter rules
      ...tseslint.configs.strictTypeChecked,
      // Optionally, add this for stylistic rules
      ...tseslint.configs.stylisticTypeChecked,

      // Other configs...
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```

You can also install [eslint-plugin-react-x](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-x) and [eslint-plugin-react-dom](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-dom) for React-specific lint rules:

```js
// eslint.config.js
import reactX from 'eslint-plugin-react-x'
import reactDom from 'eslint-plugin-react-dom'

export default tseslint.config([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...
      // Enable lint rules for React
      reactX.configs['recommended-typescript'],
      // Enable lint rules for React DOM
      reactDom.configs.recommended,
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```



$out = "all_code.txt"
Remove-Item $out -ErrorAction SilentlyContinue

# все ts, tsx, scss внутри src
$files = Get-ChildItem -Path .\src -Recurse -Include *.ts,*.tsx,*.scss -File

# отдельно файлы в корне
$core = @(
  "vite.config.ts","index.html","nginx.conf","Dockerfile",
  "package.json","tsconfig.json","tsconfig.app.json","tsconfig.node.json",
  "eslint.config.js","README.md",".env.development.local"
) | ForEach-Object { Get-Item -ErrorAction SilentlyContinue $_ }

$files += $core

$files = $files |
  Where-Object { $_.FullName -notmatch '\\node_modules\\|\\dist\\|\\.git\\' -and $_.Name -ne 'package-lock.json' } |
  Sort-Object FullName

foreach ($f in $files) {
  Add-Content -Path $out -Value "`r`n`r`n/* ===== $($f.FullName) ===== */`r`n" -Encoding utf8
  (Get-Content $f.FullName -Raw) | Add-Content -Path $out -Encoding utf8
}

"$($files.Count) файлов объединено -> $(Resolve-Path $out)"
