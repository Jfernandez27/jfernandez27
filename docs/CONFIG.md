# 🛠️ Configuración Técnica

Esta documentación detalla la configuración técnica completa para el mantenimiento automatizado del README.

## 🧭 Arquitectura

```
main (fuentes)                          output (generado, 1 commit, se reescribe a diario)
├── README.md ──referencia raw URLs──▶  ├── badges/*.svg
├── scripts/build_badges.py             ├── README-activity.svg
├── scripts/activity_graph.py           └── README.md (aviso)
└── .github/workflows/update-profile.yml
```

Un solo workflow (`update-profile.yml`) corre a diario, genera los SVG con los dos scripts y los publica con un `push --force` a la rama huérfana `output`. `main` nunca recibe commits automáticos.

## 🔐 Configuración de Tokens y Secretos

### `PAT_TOKEN` (Personal Access Token)

Se usa solo para **leer** datos de la API GraphQL. Nunca escribe en el repositorio.

1. **Crear el token** en GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. **Scopes mínimos**:
    - `read:user` — contribuciones, followers y starred
    - `repo` — **opcional**. Solo hace falta si quieres que los repos privados cuenten en Repositories, Languages, Frameworks y en los totales de commits/PRs/issues. Sin él, las cifras reflejan únicamente lo público
    - `read:org` — opcional, para que cuenten contribuciones en repos privados de organizaciones
3. **Configurar el secreto**: repositorio → Settings → Secrets and variables → Actions → `PAT_TOKEN`
4. **Anotar la expiración**. GitHub no avisa cuando un token usado por Actions caduca; el workflow sí: su primer paso falla con un mensaje explícito. Anota aquí la fecha para rotarlo antes:

    | Token       | Creado | Expira |
    | ----------- | ------ | ------ |
    | `PAT_TOKEN` | _(completar)_ | _(completar)_ |

### `GITHUB_TOKEN` (automático)

Lo genera cada corrida. El workflow declara estos permisos:

```yaml
permissions:
    contents: write # push a la rama output
    actions: write  # keepalive (re-habilitar el propio workflow)
```

## 📋 Dependencias

Ninguna que instalar. Los runners `ubuntu-latest` traen `gh`, `git`, `curl` y Python 3. Los scripts usan solo la librería estándar.

Para desarrollo local: `gh` autenticado (`gh auth login`) y Python 3.9+.

## 🔍 API de GitHub GraphQL

### Consulta de perfil (`build_badges.py`):

```graphql
query ($login: String!) {
    user(login: $login) {
        followers { totalCount }
        starredRepositories { totalCount }
        contributionsCollection { contributionYears }
        repositories(ownerAffiliations: [OWNER], isFork: false, first: 100) {
            totalCount
            nodes {
                languages(first: 5, orderBy: { field: SIZE, direction: DESC }) {
                    edges { size node { name } }
                }
                repositoryTopics(first: 10) { nodes { topic { name } } }
            }
        }
    }
}
```

### Totales por año (`build_badges.py`):

`contributionsCollection` sin rango devuelve solo los últimos 12 meses. Para el total histórico el script itera `contributionYears` y suma una consulta por año:

```graphql
query ($login: String!, $from: DateTime!, $to: DateTime!) {
    user(login: $login) {
        contributionsCollection(from: $from, to: $to) {
            totalCommitContributions
            totalPullRequestContributions
            totalIssueContributions
        }
    }
}
```

### Último push por proyecto (`build_badges.py`):

```graphql
query ($owner: String!, $name: String!) {
    repository(owner: $owner, name: $name) { pushedAt }
}
```

Una consulta por entrada de `PROJECT_REPOS`. Colores del badge: verde (< 30 días), amarillo (< 180 días), gris (más antiguo).

### Rachas (`build_badges.py`):

Se reutiliza la consulta por año anterior añadiendo `contributionCalendar`. Con todos los días del historial se calcula la racha más larga y la actual. Si hoy aún no hay contribuciones, la racha actual se cuenta hasta ayer.

### Calendario de contribuciones (`activity_graph.py`):

```graphql
query ($login: String!, $from: DateTime!, $to: DateTime!) {
    user(login: $login) {
        contributionsCollection(from: $from, to: $to) {
            contributionCalendar {
                totalContributions
                weeks { contributionDays { date contributionCount } }
            }
        }
    }
}
```

### Límites de la API:

-   **GraphQL API**: 5.000 puntos/hora. Una corrida completa consume del orden de 20 puntos

## 🎨 Generación de Badges

`scripts/build_badges.py` descarga cada badge de Shields.io:

```
https://img.shields.io/badge/<label>-<message>-<color>?style=flat&labelColor=101010
```

Los guiones y guiones bajos del texto se escapan (`--`, `__`) porque son separadores en la sintaxis de Shields.

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
# Current Streak: Naranja       F97316
# Longest Streak: Rojo          EF4444
# Last push: verde/amarillo/gris según antigüedad
```

### Badge de Languages

Excluye los "lenguajes" de marcado, estilos y configuración que Linguist reporta (`CSS`, `SCSS`, `HTML`, `Blade`, `Dockerfile`, etc.; lista `NON_CODE_LANGUAGES` en el script) para que el top 3 refleje código real.

### Badge de Frameworks (basado en GitHub Topics)

El badge de "Frameworks" no viene de un dato nativo de la API de GitHub (a diferencia de "Languages", que usa el detector de Linguist). Se calcula agregando los **repository topics** que hayas configurado manualmente en cada repo (Settings → General → Topics), filtrados contra la lista `FRAMEWORK_TOPICS` de `scripts/build_badges.py` (`laravel`, `livewire`, `react`, `nextjs`, `vue`, `django`, `fastapi`, `tailwindcss`, etc.). Los lenguajes (`php`, `python`, `typescript`) quedan fuera a propósito, porque ya los cubre el badge de Languages.

-   Si un repo no tiene topics configurados, no aporta nada al cálculo.
-   Si ningún repo tiene topics relevantes, el badge muestra "Add topics on GitHub" como aviso.
-   Para que un repo cuente, agrégale topics en GitHub que coincidan con la lista.

## 📊 Gráfico de Actividad

### Generación propia (sin servicios externos)

Hasta diciembre de 2025 el gráfico se descargaba de `github-readme-activity-graph.vercel.app`. Ese deployment de terceros fue deshabilitado (responde `402 DEPLOYMENT_DISABLED`), así que ahora el SVG se genera en el propio workflow con `scripts/activity_graph.py`.

El script:

1. Consulta `contributionCalendar` en la API GraphQL usando el `gh` CLI
2. Toma los últimos N días (30 por defecto) y rellena con 0 los días sin contribuciones
3. Renderiza un gráfico de línea como SVG estático (1200×420) con estilo oscuro: fondo `0a0f0b`, línea `F97316`, puntos `abd200`

### Personalización:

Los colores, tamaño y fuente están definidos como constantes al inicio de `scripts/activity_graph.py`. El número de días se cambia con `--days` en el workflow.

## 🔄 Flujo de Trabajo Automatizado (`update-profile.yml`)

1. **Checkout** de `main`
2. **Verificar `PAT_TOKEN`**: falla rápido con un mensaje claro si falta o expiró
3. **Generar** badges y gráfico en `dist/` con los dos scripts
4. **Publicar**: `git init` en `dist/`, un commit, `push --force` a la rama `output`. La rama siempre tiene un único commit
5. **Keepalive**: llama a la API `enable` del propio workflow, lo que reinicia el contador de 60 días de inactividad con el que GitHub deshabilita los crons

`concurrency` evita que una ejecución manual y la programada se pisen.

### Rama `output`

-   Es huérfana: no comparte historia con `main`
-   Se reescribe entera cada día; no edites nada ahí a mano
-   Si la borras, la siguiente corrida la vuelve a crear

## 🤖 Dependabot

`.github/dependabot.yml` revisa mensualmente las versiones de las GitHub Actions usadas y abre un PR cuando hay una nueva.

## 📝 Estructura de Archivos

```
.
├── README.md                       # README principal (rama main)
├── scripts/
│   ├── build_badges.py             # Genera badges/*.svg
│   └── activity_graph.py           # Genera README-activity.svg
├── .github/
│   ├── dependabot.yml              # Bumps automáticos de Actions
│   └── workflows/
│       └── update-profile.yml      # Workflow único
└── docs/
    ├── UPDATE.md                   # Guía de actualización
    └── CONFIG.md                   # Este archivo

output (rama aparte, generada)
├── README.md
├── README-activity.svg
└── badges/*.svg
```

## 🐛 Debug y Logs

### Ver logs de workflows:

```bash
gh run list --workflow=update-profile.yml --limit 5
gh run view <run-id> --log
```

O en la pestaña **Actions** del repositorio.

### Comandos útiles para debug local:

```bash
# Probar autenticación GitHub CLI
gh auth status

# Probar consulta GraphQL
gh api graphql -f query='query { viewer { login } }'

# Generar todo en local
python3 scripts/build_badges.py --user Jfernandez27 --output-dir /tmp/badges
python3 scripts/activity_graph.py --user Jfernandez27 --days 30 --output /tmp/activity.svg

# Ver qué hay publicado en la rama output
gh api "repos/Jfernandez27/jfernandez27/git/trees/output?recursive=1" --jq '.tree[].path'
```

### Errores comunes:

1. **Token expirado o ausente**: el paso "Verificar PAT_TOKEN" lo indica. Renovar el PAT y actualizar el secreto
2. **Workflow deshabilitado por inactividad**: `gh workflow enable "Update profile assets"`
3. **Rate limit**: esperar el reset
4. **Shields.io caído**: `build_badges.py` falla si la respuesta no es un SVG; la rama `output` conserva la versión anterior

## 🔒 Seguridad

-   ✅ `PAT_TOKEN` solo lee; el push lo hace `GITHUB_TOKEN` con permisos declarados explícitamente
-   ✅ Usar los scopes mínimos (ver arriba) y rotar el token antes de que caduque
-   ✅ Dependabot mantiene las Actions al día
-   ✅ Los scripts no tienen dependencias de terceros

---

**Nota**: Esta configuración está optimizada para el repositorio personal de **Jfernandez27**. Para otros usuarios, ajustar `GH_USER` en el workflow y las URLs raw del README.
