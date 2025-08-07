# 🛠️ Configuración Técnica

Esta documentación detalla la configuración técnica completa para el mantenimiento automatizado del README.

## 🔐 Configuración de Tokens y Secretos

### Personal Access Token (PAT)

1. **Crear el token**:

    - Ve a GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
    - Genera un nuevo token con los siguientes permisos:
        - `repo` (acceso completo a repositorios)
        - `read:user` (leer información del usuario)
        - `read:org` (leer información de organizaciones)

2. **Configurar el secreto**:
    - En el repositorio → Settings → Secrets and variables → Actions
    - Crear nuevo secreto: `PAT_TOKEN`
    - Pegar el token generado

### GitHub Token (automático)

El `GITHUB_TOKEN` se genera automáticamente y tiene permisos limitados para:

-   Hacer commits
-   Push de cambios
-   Leer repositorio

## 📋 Dependencias del Sistema

### En Ubuntu/GitHub Actions:

```bash
# GitHub CLI
sudo apt-get update
sudo apt-get install -y gh
```

### En desarrollo local:

```bash
# macOS
brew install gh

# Ubuntu/Debian
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh
```

## 🔍 API de GitHub GraphQL

### Consulta de métricas de usuario:

```graphql
query ($login: String!) {
    user(login: $login) {
        repositories(ownerAffiliations: [OWNER], isFork: false) {
            totalCount
        }
        contributionsCollection {
            totalCommitContributions
            totalPullRequestContributions
            totalIssueContributions
        }
        followers {
            totalCount
        }
        starredRepositories {
            totalCount
        }
    }
}
```

### Consulta de lenguajes por repositorio:

```graphql
query ($owner: String!, $name: String!) {
    repository(owner: $owner, name: $name) {
        languages {
            totalCount
        }
    }
}
```

### Límites de la API:

-   **REST API**: 5,000 requests/hora
-   **GraphQL API**: 5,000 points/hora
-   **Authenticated requests**: Límites más altos

## 🎨 Generación de Badges

### Generación de Badges con Shields.io

Los badges se generan usando la API de Shields.io y `curl`. Ejemplo:

```bash
curl -s -o badges/public-repos.svg "https://img.shields.io/badge/Repositories-123-0EA5E9?style=flat&labelColor=101010"
```

Puedes personalizar el texto, color y estilo directamente en la URL.

### Colores utilizados:

```bash
# Repositorios: Azul cielo      0EA5E9
# Commits: Verde esmeralda      10B981
# PRs: Verde lima               22C55E
# Issues: Rojo                  DC2626
# Followers: Amarillo           FACC15
# Starred: Naranja              F97316
# Languages: Magenta            D946EF
```

## 📊 Gráfico de Actividad

### Servicio utilizado:

**GitHub Readme Activity Graph**: https://github-readme-activity-graph.vercel.app/

### URL de generación:

```
https://github-readme-activity-graph.vercel.app/graph?username=USERNAME&theme=THEME&days=DAYS
```

### Parámetros:

-   `username`: Nombre de usuario de GitHub
-   `theme`: Tema visual
    -   `react-dark` (actual)
    -   `github`
    -   `xcode`
    -   `rogue`
    -   `merko`
    -   `gruvbox`
-   `days`: Número de días (30 por defecto)

### Temas disponibles:

-   `react-dark`: Fondo oscuro con colores modernos
-   `github`: Tema similar a GitHub
-   `xcode`: Estilo Xcode
-   `rogue`: Colores oscuros y contrastantes
-   `merko`: Verde y negro
-   `gruvbox`: Paleta retro

## 🔄 Flujo de Trabajo Automatizado

### Workflow de Badges (`user-global-badges.yml`):

1. **Checkout del repositorio**
2. **Instalación de dependencias** (gh CLI + make-issue-badge)
3. **Autenticación con PAT**
4. **Consulta a GraphQL API** para obtener métricas
5. **Generación de badges SVG**
6. **Commit y push automático**

### Workflow de Activity Graph (`activity-graph.yml`):

1. **Checkout del repositorio**
2. **Descarga del SVG** desde el servicio externo
3. **Commit y push automático**

## 📝 Estructura de Archivos

```
.
├── README.md                 # README principal
├── README-activity.svg       # Gráfico de actividad (auto-generado)
├── badges/                   # Carpeta de badges (auto-generada)
│   ├── public-repos.svg      # Badge de repositorios
│   ├── total-commits.svg     # Badge de commits
│   ├── pr-contrib.svg        # Badge de PRs
│   ├── issue-contrib.svg     # Badge de issues
│   ├── followers.svg         # Badge de followers
│   ├── starred.svg           # Badge de starred repos
│   └── languages.svg         # Badge de lenguajes
├── .github/
│   └── workflows/
│       ├── user-global-badges.yml  # Workflow de badges
│       └── activity-graph.yml      # Workflow de gráfico
└── docs/                     # Documentación
    ├── ACTUALIZACIÓN.md      # Guía de actualización
    └── CONFIGURACIÓN.md      # Este archivo
```

## 🐛 Debug y Logs

### Ver logs de workflows:

1. Ve a la pestaña **Actions** del repositorio
2. Selecciona el workflow que falló
3. Haz clic en el job específico
4. Expande los steps para ver detalles

### Comandos útiles para debug local:

```bash
# Probar autenticación GitHub CLI
gh auth status

# Probar consulta GraphQL
gh api graphql -f query='query { viewer { login } }'

# Generar badge de prueba con Shields.io
curl -s -o test.svg "https://img.shields.io/badge/Test-42-00FF00?style=flat&labelColor=101010"

# Verificar curl para activity graph
curl "https://github-readme-activity-graph.vercel.app/graph?username=Jfernandez27&theme=react-dark&days=30" -o test-activity.svg
```

### Errores comunes:

1. **Token expirado**: Renovar PAT en GitHub Settings
2. **Permisos insuficientes**: Verificar scopes del token
3. **Rate limit**: Esperar reset o usar token con mayor límite
4. **Servicio externo no disponible**: Verificar status del servicio

## 🔒 Seguridad

### Buenas prácticas:

-   ✅ Usar PAT con permisos mínimos necesarios
-   ✅ Rotar tokens periódicamente
-   ✅ No hardcodear tokens en código
-   ✅ Usar secretos de GitHub Actions
-   ✅ Verificar logs por información sensible

### Permisos mínimos requeridos:

```
PAT_TOKEN:
├── repo (full control)
├── read:user (read user profile)
└── read:org (read org membership)

GITHUB_TOKEN (automático):
├── contents: write (commit files)
└── metadata: read (read repository)
```

---

**Nota**: Esta configuración está optimizada para el repositorio personal de **Jfernandez27**. Para otros usuarios, ajustar nombres de usuario y configuraciones específicas.
