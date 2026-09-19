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
# Frameworks: Violeta           8B5CF6
```

### Badge de Frameworks (basado en GitHub Topics)

El badge de "Frameworks" no viene de un dato nativo de la API de GitHub (a diferencia de "Languages", que usa el detector de Linguist). Se calcula agregando los **repository topics** que hayas configurado manualmente en cada repo (Settings → General → Topics), filtrados contra una lista fija de topics de frameworks en el workflow (`laravel`, `livewire`, `react`, `nextjs`, `vue`, `django`, `fastapi`, `tailwindcss`, etc.). Los lenguajes (`php`, `python`, `typescript`) quedan fuera a propósito, porque ya los cubre el badge de Languages.

- Si un repo no tiene topics configurados, no aporta nada al cálculo.
- Si ningún repo tiene topics relevantes, el badge muestra "Add topics on GitHub" como aviso.
- Para que un repo cuente, agrégale topics en GitHub que coincidan con la lista `frameworks` definida en `.github/workflows/user-global-badges.yml`.

## 📊 Gráfico de Actividad

### Generación propia (sin servicios externos)

Hasta diciembre de 2025 el gráfico se descargaba de `github-readme-activity-graph.vercel.app`. Ese deployment de terceros fue deshabilitado (responde `402 DEPLOYMENT_DISABLED`), así que ahora el SVG se genera en el propio workflow con `scripts/activity_graph.py`.

El script:

1. Consulta `contributionsCollection.contributionCalendar` en la API GraphQL usando el `gh` CLI (autenticado con `PAT_TOKEN`)
2. Toma los últimos N días (30 por defecto) y rellena con 0 los días sin contribuciones
3. Renderiza un gráfico de línea como SVG estático (1200×420) con estilo oscuro: fondo `0a0f0b`, línea `F97316`, puntos `abd200`

Solo usa la librería estándar de Python y `gh`; no hay dependencias que instalar.

### Uso:

```bash
python3 scripts/activity_graph.py --user Jfernandez27 --days 30 --output README-activity.svg
```

### Personalización:

Los colores, tamaño y fuente están definidos como constantes al inicio de `scripts/activity_graph.py`.

## 🔄 Flujo de Trabajo Automatizado

### Workflow de Badges (`user-global-badges.yml`):

1. **Checkout del repositorio**
2. **Instalación de dependencias** (gh CLI)
3. **Autenticación con PAT**
4. **Consulta a GraphQL API** para obtener métricas
5. **Generación de badges SVG**
6. **Commit y push automático**

### Workflow de Activity Graph (`activity-graph.yml`):

1. **Checkout del repositorio**
2. **Generación del SVG** con `scripts/activity_graph.py` (API GraphQL vía `gh`)
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
│   ├── languages.svg         # Badge de lenguajes
│   └── frameworks.svg        # Badge de frameworks (via GitHub Topics)
├── .github/
│   └── workflows/
│       ├── user-global-badges.yml  # Workflow de badges
│       └── activity-graph.yml      # Workflow de gráfico
├── scripts/
│   └── activity_graph.py     # Generador del gráfico de actividad
└── docs/                     # Documentación
    ├── UPDATE.md              # Guía de actualización
    └── CONFIG.md              # Este archivo
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

# Generar el gráfico de actividad en local
python3 scripts/activity_graph.py --user Jfernandez27 --days 30 --output test-activity.svg
```

### Errores comunes:

1. **Token expirado**: Renovar PAT en GitHub Settings
2. **Permisos insuficientes**: Verificar scopes del token
3. **Rate limit**: Esperar reset o usar token con mayor límite
4. **Workflow deshabilitado por inactividad**: Reactivar con `gh workflow enable <nombre>`

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
