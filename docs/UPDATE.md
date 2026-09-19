# 📋 Guía de Actualización del README

Esta documentación explica cómo actualizar y mantener el README.md del perfil de GitHub de **Jesus Fernández Machín**.

## 🔄 Actualizaciones Automáticas

Un único workflow, `.github/workflows/update-profile.yml`, se ejecuta **diariamente a las 04:00 UTC** y regenera todos los elementos dinámicos del README:

### Badges de estadísticas (`scripts/build_badges.py`)

-   **Repositories**: Número total de repositorios propios (sin forks)
-   **Total Commits**: Commits sumados en todos los años de la cuenta
-   **PR Contributions**: Pull requests sumados en todos los años
-   **Issue Contributions**: Issues sumados en todos los años
-   **Followers**: Número de seguidores
-   **Starred Repositories**: Repositorios marcados con estrella
-   **Languages**: Top 3 lenguajes por tamaño de código (Linguist)
-   **Frameworks**: Top 3 frameworks según los topics configurados en tus repos (solo frameworks, no lenguajes)

### Gráfico de actividad (`scripts/activity_graph.py`)

-   **README-activity.svg**: Contribuciones por día de los últimos 30 días

### Dónde se guardan

Los archivos generados **no se commitean en `main`**. El workflow los publica en la rama huérfana `output`, que se reescribe entera cada día con un solo commit. El README los referencia por su URL raw:

```
https://raw.githubusercontent.com/Jfernandez27/jfernandez27/output/badges/<badge>.svg
https://raw.githubusercontent.com/Jfernandez27/jfernandez27/output/README-activity.svg
```

Así `main` solo contiene cambios hechos a mano y el historial se mantiene limpio.

## ⚙️ Ejecución Manual

```bash
gh workflow run "Update profile assets"
```

O desde la interfaz web: **Actions → Update profile assets → Run workflow**.

### Regenerar en local

Requiere `gh` autenticado (`gh auth login`) y Python 3.9+. No hay dependencias que instalar.

```bash
python3 scripts/build_badges.py --user Jfernandez27 --output-dir badges
python3 scripts/activity_graph.py --user Jfernandez27 --days 30 --output README-activity.svg
```

Los números pueden diferir de los del workflow si tu token local ve un conjunto distinto de repos privados que `PAT_TOKEN`.

## ✏️ Actualizaciones Manuales

Para actualizar la información personal, edita directamente `README.md`:

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
<a href="URL_DE_LA_TECNOLOGIA" target="_blank" rel="noopener noreferrer">
  <img src="https://img.shields.io/badge/NOMBRE-VERSION-COLOR?logo=LOGO&logoColor=white&labelColor=101010" alt="NOMBRE" />
</a>
```

**Parámetros importantes**:

-   `NOMBRE`: Nombre de la tecnología
-   `VERSION`: Versión utilizada
-   `COLOR`: Color hexadecimal del badge
-   `LOGO`: Nombre del logo en shields.io
-   `labelColor=101010`: Color de fondo uniforme

> GitHub elimina los atributos `style` de las etiquetas `img` y `a` al renderizar el README, así que no sirve de nada añadirlos.

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

## 🔧 Configuración del Workflow

Ver `docs/CONFIG.md` para el detalle de tokens, permisos y estructura. Resumen:

1. **`PAT_TOKEN`** configurado en los secretos del repositorio (ver scopes en CONFIG.md)
2. Nada más: `gh` y Python vienen preinstalados en los runners de Ubuntu

### Modificar el horario de ejecución:

En `.github/workflows/update-profile.yml`, ajusta el cron:

```yaml
schedule:
    - cron: '0 4 * * *' # Diario a las 04:00 UTC
```

**Formato cron**: `minuto hora día mes día_semana`

## 🐛 Solución de Problemas

### Los badges o el gráfico no se actualizan:

1. Ve a **Actions** y comprueba que el workflow "Update profile assets" esté habilitado y que la última corrida terminó en verde
2. Si el primer paso falla, `PAT_TOKEN` no existe o expiró: genera uno nuevo y actualiza el secreto
3. Si el workflow aparece deshabilitado por inactividad, reactívalo con `gh workflow enable "Update profile assets"`. El propio workflow se re-habilita en cada corrida como keepalive, así que esto solo debería pasar si llevaba mucho tiempo fallando
4. Ejecuta los scripts en local (ver arriba) para reproducir un error de generación

### Veo una versión vieja de una imagen:

El servidor raw de GitHub cachea 5 minutos y el navegador guarda su copia. Recarga con `Ctrl+Shift+R` o abre la URL en incógnito.

### Error en GraphQL API:

1. Verificar límites de rate de la API de GitHub (5.000 puntos/hora)
2. Confirmar sintaxis de las consultas en `scripts/*.py`
3. Revisar scopes del `PAT_TOKEN`

## 📚 Recursos Adicionales

-   [GitHub GraphQL API](https://docs.github.com/en/graphql)
-   [GitHub Actions Docs](https://docs.github.com/en/actions)
-   [Shields.io](https://shields.io/)

## 🔄 Changelog

-   **2025-01**: Implementación de badges automáticos
-   **2025-01**: Integración de gráfico de actividad
-   **2025-01**: Documentación de actualización
-   **2026-09**: Badge de Frameworks basado en topics; actualización de versiones de Actions y corrección de docs
-   **2026-09**: El gráfico de actividad se genera con `scripts/activity_graph.py` (el servicio externo de Vercel dejó de funcionar)
-   **2026-09**: Un solo workflow, assets publicados en la rama `output`, badges generados con `scripts/build_badges.py` (totales de todos los años), Dependabot para Actions

---

**Mantenedor**: Jesus Fernández Machín  
**Última actualización**: Septiembre 2026
