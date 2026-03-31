# DoItForMe API

FastAPI backend foundation for the DoItForMe platform.

## 🛠️ Requisitos Previos

- **Python 3.13+**
- **uv** (Gestor de paquetes extremadamente rápido): [Instalación](https://github.com/astral-sh/uv)
- **Docker** (Opcional, para la base de datos local)

## 🚀 Instalación y Ejecución

1. **Instalar dependencias:**
   ```bash
   uv sync
   ```

2. **Configurar el entorno:**
   Copia el archivo de ejemplo y rellena los valores (DB_URL, JWT_SECRET, etc.):
   ```bash
   cp .env.example .env
   ```

3. **Ejecutar Base de Datos (vía Docker):**
   ```bash
   docker compose up -d
   ```

4. **Ejecutar Migraciones:**
   ```bash
   uv run alembic upgrade head
   ```

5. **Lanzar el servidor:**
   ```bash
   uv run uvicorn app.main:app --reload
   ```

## 🧪 Pruebas y Verificación

### Ejecutar Suite de Tests
Para pasar todos los tests automáticos y asegurar que no hay regresiones:
```bash
uv run pytest
```

### Verificación Manual (Swagger UI)
Una vez el servidor esté corriendo, abre en tu navegador:
- **Documentación Interactiva:** `http://localhost:8000/docs`
- **Documentación Redoc:** `http://localhost:8000/redoc`

## 📂 Estructura del Proyecto

- `app/api`: Definición de endpoints y rutas.
- `app/services`: Lógica de negocio principal.
- `app/repositories`: Consultas a la base de datos.
- `app/models`: Modelos de SQLAlchemy.
- `app/schemas`: Esquemas de validación Pydantic.
- `tests`: Tests de integración y unitarios.
