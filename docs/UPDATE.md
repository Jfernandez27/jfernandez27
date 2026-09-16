# 📋 Guía de Actualización del README

Esta documentación explica cómo actualizar y mantener el README.md del perfil de GitHub de **Jesus Fernández Machín**.

## 🔄 Actualizaciones Automáticas

El README incluye elementos que se actualizan automáticamente mediante GitHub Actions:

### 1. Badges de Estadísticas GitHub (`.github/workflows/user-global-badges.yml`)

Se ejecuta **diariamente a las 4:00 AM** y actualiza los siguientes badges usando Shields.io y curl:

-   **Repositorios**: Número total de repositorios públicos
-   **Commits Totales**: Total de commits realizados
-   **PR Contributions**: Contribuciones de Pull Requests
-   **Issue Contributions**: Contribuciones de Issues
-   **Followers**: Número de seguidores
-   **Starred Repos**: Repositorios marcados con estrella
-   **Languages**: Tecnologías principales
-   **Frameworks**: Top 3 frameworks/tecnologías según los topics configurados en tus repos de GitHub

**Archivos generados**: `badges/*.svg`

### 2. Gráfico de Actividad (`.github/workflows/activity-graph.yml`)

Se ejecuta **diariamente a la 1:00 AM** y actualiza:

-   **README-activity.svg**: Gráfico de actividad de los últimos 30 días

## ⚙️ Ejecución Manual

### Forzar actualización de badges:

```bash
gh workflow run "Build extended user & repo badges"
```

### Forzar actualización del gráfico de actividad:

```bash
gh workflow run "Update Activity Graph"
```

O desde la interfaz web de GitHub:

1. Ve a **Actions** en el repositorio
2. Selecciona el workflow deseado
3. Haz clic en **"Run workflow"**

## ✏️ Actualizaciones Manuales

### Información Personal

Para actualizar la información personal, edita directamente `README.md`:

#### Secciones que requieren actualización manual:

1. **Proyectos en desarrollo** (sección "🚀 What I'm Working On")

    - Agregar/quitar proyectos
    - Actualizar URLs y estados

2. **Stack tecnológico** (sección "🛠️ Tech Stack")

    - Agregar nuevas tecnologías
    - Actualizar versiones

3. **Certificaciones** (sección "🎓 Certifications")

    - Marcar como completadas
    - Agregar nuevas certificaciones

4. **Objetivos** (sección "🎯 Goals")

    - Actualizar metas actuales

5. **Badges de tecnologías** (sección "💻 I Code With")

    - Agregar nuevas tecnologías
    - Actualizar versiones

6. **Información de contacto** (sección "📫 How to Reach Me")
    - Actualizar enlaces
    - Agregar nuevas redes sociales

### Estructura de los Badges de Tecnología

Los badges siguen este formato:

```markdown
<a href="URL_DE_LA_TECNOLOGIA">
  <img src="https://img.shields.io/badge/NOMBRE-VERSION-COLOR?logo=LOGO&logoColor=white&labelColor=101010" alt="NOMBRE" />
</a>
```

**Parámetros importantes**:

-   `NOMBRE`: Nombre de la tecnología
-   `VERSION`: Versión utilizada
-   `COLOR`: Color hexadecimal del badge
-   `LOGO`: Nombre del logo en shields.io
-   `labelColor=101010`: Color de fondo uniforme

## 🎨 Personalización de Badges

### Colores recomendados por tecnología:

-   **PHP**: `3B82F6` (azul)
-   **Laravel**: `F97316` (naranja)
-   **Node.js**: `22C55E` (verde)
-   **Python**: `3776AB` (azul oscuro)
-   **MySQL**: `4479A1` (azul MySQL)
-   **PostgreSQL**: `336791` (azul PostgreSQL)
-   **Docker**: `2496ED` (azul Docker)
-   **Vue.js**: `4FC08D` (verde Vue)
-   **Tailwind**: `38B2AC` (teal)

### Herramientas útiles:

-   [Shields.io](https://shields.io/) - Generador de badges (usado en el workflow)
-   [Simple Icons](https://simpleicons.org/) - Iconos disponibles
-   [Color Picker](https://htmlcolorcodes.com/) - Selección de colores

## 🔧 Configuración de Workflows

### Requisitos:

1. **Personal Access Token (PAT)**:

    - Configurado como `PAT_TOKEN` en los secretos del repositorio
    - Permisos: `repo`, `read:user`, `read:org`

2. **Dependencias**:
    - GitHub CLI (`gh`)
    - curl

### Modificar horarios de ejecución:

En los archivos `.github/workflows/*.yml`, ajusta el cron:

```yaml
schedule:
    - cron: '0 4 * * *' # Diario a las 4:00 AM UTC
```

**Formato cron**: `minuto hora día mes día_semana`

## 🐛 Solución de Problemas

### Los badges no se actualizan:

1. Verificar que el token PAT tenga permisos correctos
2. Revisar los logs en la pestaña **Actions**
3. Confirmar que la carpeta `badges/` existe
4. Verificar que la URL de Shields.io sea válida y que curl esté instalado

### El gráfico de actividad no aparece:

1. Verificar que el archivo `README-activity.svg` se genera correctamente
2. Comprobar la URL del servicio de gráficos
3. Revisar que el nombre de usuario sea correcto

### Error en GraphQL API:

1. Verificar límites de rate de la API de GitHub
2. Confirmar sintaxis de las consultas GraphQL
3. Revisar permisos del token PAT

## 📚 Recursos Adicionales

-   [GitHub GraphQL API](https://docs.github.com/en/graphql)
-   [GitHub Actions Docs](https://docs.github.com/en/actions)
-   [Make Issue Badge](https://www.npmjs.com/package/make-issue-badge)
-   [GitHub Readme Activity Graph](https://github.com/Ashutosh00710/github-readme-activity-graph)

## 🔄 Changelog

### Últimas actualizaciones:

-   **2025-01**: Implementación de badges automáticos
-   **2025-01**: Integración de gráfico de actividad
-   **2025-01**: Documentación de actualización

---

**Mantenedor**: Jesus Fernández Machín  
**Última actualización**: Agosto 2025
