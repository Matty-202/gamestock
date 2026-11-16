# 🎮 GameStock — Inventario seguro de videojuegos

Proyecto académico de Desarrollo Seguro desarrollado con **Django**, **Python**, **SQLite** y **Docker**. Administra videojuegos, registra compras y ventas, controla stock y consulta movimientos.

## Requisitos
- Docker Desktop con WSL 2 (Windows) **o** Python 3.12 y pip.
- Git para publicar en GitHub.

## Opción A: Docker (recomendada)
1. Copia `.env.example` a `.env` (PowerShell: `Copy-Item .env.example .env`).
2. Sustituye `DJANGO_SECRET_KEY` por una clave larga y aleatoria (puedes generar una con `python -c "import secrets; print(secrets.token_urlsafe(50))"`).
3. Inicia Docker Desktop.
4. Ejecuta:

```powershell
docker compose build
docker compose run --rm web python manage.py migrate
docker compose run --rm web python manage.py createsuperuser
docker compose up -d
```

5. Abre **http://localhost:8000** e inicia sesión. El administrador está en `/admin/`.

Para detener: `docker compose down` (no elimina el volumen). **No uses** `docker compose down -v` si deseas conservar datos.

## Opción B: Sin Docker (Windows PowerShell)
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
**Nota:** sin Docker, Django no lee `.env` automáticamente. Para desarrollo local se utiliza la clave insegura predeterminada; antes de cualquier despliegue real, configura `DJANGO_SECRET_KEY` como variable de entorno y ejecuta con `DEBUG=0`.

## Permisos
El superusuario tiene acceso completo. Para otros usuarios, asigna permisos de `Videojuego` (agregar/cambiar/eliminar) y `Movimiento` (agregar) desde `/admin/`. Los usuarios autenticados pueden consultar inventario e historial. El historial no se puede editar ni borrar desde el administrador.

## Funcionalidades
- CRUD de videojuegos: título, plataforma, género, precio de compra, precio de venta y stock.
- Compra: aumenta stock; venta: descuenta stock solo si hay existencias suficientes.
- Historial de operaciones con usuario, fecha y totales.
- Búsqueda y filtro, panel de indicadores.
- Login, permisos, protección CSRF, ORM, validaciones y control de stock transaccional.
- Dockerfile con usuario no privilegiado, `.dockerignore`, puerto restringido a localhost y volumen persistente.

## Pruebas
```powershell
docker compose run --rm web python manage.py test
# O sin Docker: python manage.py test
```

## GitHub
```powershell
git init
git add .
git commit -m "Proyecto GameStock Django Docker"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/gamestock.git
git push -u origin main
```
Crea primero el repositorio **vacío** en GitHub. Nunca publiques `.env`, bases de datos reales ni contraseñas.

## Relación con el material Fundamento Docker.pdf
- Arquitectura cliente-servidor, imágenes y contenedores: partes II y III.
- Dockerfile y `.dockerignore`: secciones 9 y 10.
- Puertos y volúmenes: secciones 22 y 23.
- Django, Git y GitHub: secciones 24 y 25.
- Seguridad y buenas prácticas: sección 26.

## Límites y mejoras futuras
Este proyecto está diseñado para **demostración local académica**, no para producción pública. Antes de desplegarlo: usar PostgreSQL, HTTPS con proxy inverso, gestión real de secretos, backups, auditoría, monitoreo y pruebas de carga. El panel presenta totales de compras y ventas, no beneficio neto contable. La edición manual de stock está destinada al administrador y no genera movimientos históricos; para trazabilidad estricta se debe añadir un módulo de ajustes. SQLite admite concurrencia limitada.
