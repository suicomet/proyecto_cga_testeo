# Guía de Despliegue - Sistema de Panadería

Esta guía explica cómo desplegar el sistema de panadería en producción usando:
- **Frontend**: Vercel (Angular)
- **Backend**: Railway (Django + PostgreSQL)
- **Base de datos**: PostgreSQL gestionada por Railway

## 📋 Prerrequisitos

1. Cuenta en [GitHub](https://github.com) (repositorio del proyecto)
2. Cuenta en [Vercel](https://vercel.com) (gratis)
3. Cuenta en [Railway](https://railway.app) (gratis con límites)

## 🚀 Despliegue del Backend (Railway)

### Paso 1: Preparar el repositorio
Asegúrate de que tu proyecto esté en GitHub con la siguiente estructura:
```
panaderia_proyecto/
├── backend/          # Django backend
│   ├── api/
│   ├── panaderia_backend/
│   ├── requirements.txt
│   ├── Procfile
│   ├── runtime.txt
│   ├── .env.example
│   └── manage.py
└── frontend/         # Angular frontend
    ├── src/
    ├── angular.json
    ├── vercel.json
    └── package.json
```

### Paso 2: Desplegar en Railway
1. Inicia sesión en [Railway](https://railway.app)
2. Haz clic en **"New Project"** → **"Deploy from GitHub repo"**
3. Conecta tu cuenta de GitHub y selecciona el repositorio
4. Selecciona el directorio `backend` como raíz del proyecto
5. Railway detectará automáticamente que es un proyecto Django

### Paso 3: Configurar base de datos
1. En el dashboard de Railway, haz clic en **"New"** → **"Database"**
2. Selecciona **PostgreSQL**
3. Railway creará automáticamente una base de datos y configurará las variables de entorno

### Paso 4: Configurar variables de entorno
En Railway, ve a **Settings** → **Variables** y configura:

```
DEBUG=False
DJANGO_SECRET_KEY=<genera-un-secreto-seguro>
ALLOWED_HOSTS=*.railway.app
CORS_ALLOWED_ORIGINS=https://tu-frontend.vercel.app
CSRF_TRUSTED_ORIGINS=https://*.railway.app
```

**Nota**: Railway proporciona automáticamente `DATABASE_URL`, no es necesario configurarla manualmente.
**Nota 2**: `CORS_ALLOWED_ORIGINS` se configurará después de desplegar el frontend.

### Paso 5: Ejecutar migraciones
1. En Railway, ve a la pestaña **"Deployments"**
2. Haz clic en los tres puntos del deployment más reciente → **"Open Shell"**
3. Ejecuta los siguientes comandos:

```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

### Paso 6: Obtener la URL del backend
1. En Railway, ve a **Settings** → **Domains**
2. Copia la URL generada (ej: `https://tu-proyecto.up.railway.app`)

## 🎨 Despliegue del Frontend (Vercel)

### Paso 1: Preparar configuración
1. Actualiza `frontend/vercel.json`:
   - Reemplaza `https://your-backend-service.railway.app` con tu URL real de Railway

2. Verifica `frontend/src/environments/environment.prod.ts`:
   ```typescript
   export const environment = {
     production: true,
     apiUrl: '/api',      // Usa proxy de Vercel
     authUrl: '/api/token'
   };
   ```

### Paso 2: Desplegar en Vercel
1. Inicia sesión en [Vercel](https://vercel.com)
2. Haz clic en **"Add New Project"** → **"Import Git Repository"**
3. Conecta tu cuenta de GitHub y selecciona el repositorio
4. Configura el proyecto:
   - **Framework Preset**: Angular
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist/panaderia`
5. Haz clic en **"Deploy"**

### Paso 3: Configurar dominio
1. Una vez desplegado, Vercel asignará una URL (ej: `tu-proyecto.vercel.app`)
2. Copia esta URL para configurar el CORS en el backend

### Paso 4: Actualizar CORS en Railway
1. Regresa a Railway → **Settings** → **Variables**
2. Actualiza `CORS_ALLOWED_ORIGINS` con la URL de Vercel:
   ```
   CORS_ALLOWED_ORIGINS=https://tu-proyecto.vercel.app
   ```
3. Si necesitas múltiples orígenes, sepáralos por comas

## 🔗 Configurar Proxy (Opcional)

El archivo `frontend/vercel.json` ya configura un proxy que redirige:
- `/api/*` → tu backend Railway
- `/admin/*` → panel de administración Django
- `/static/*` → archivos estáticos Django
- `/media/*` → archivos multimedia

Esto permite que el frontend haga peticiones a rutas relativas.

## 📊 Migración de Datos (Opcional)

### Exportar datos locales
```bash
cd backend
python manage.py dumpdata --exclude=auth.permission --exclude=contenttypes > datos.json
```

### Importar en Railway
1. Sube `datos.json` al shell de Railway
2. Ejecuta:
```bash
python manage.py loaddata datos.json
```

## 🧪 Verificar el Despliegue

### Backend
1. Visita `https://tu-backend.railway.app/api/` → deberías ver la API
2. Visita `https://tu-backend.railway.app/admin/` → login con superusuario

### Frontend
1. Visita tu URL de Vercel
2. Prueba login y todas las funcionalidades CRUD

## 🔧 Solución de Problemas Comunes

### 1. Error CORS
- Verifica que `CORS_ALLOWED_ORIGINS` incluya la URL exacta del frontend
- Revisa la consola del navegador para ver errores de CORS

### 2. Error de base de datos
- Verifica que las variables de entorno de PostgreSQL estén configuradas
- Revisa los logs de Railway

### 3. Archivos estáticos no cargan
- Ejecuta `python manage.py collectstatic` en Railway
- Verifica que `whitenoise` esté en `requirements.txt`

### 4. Proxy no funciona
- Verifica que `vercel.json` tenga la URL correcta del backend
- Revisa las rewrites en el dashboard de Vercel

## 📞 Soporte

- **Railway Docs**: https://docs.railway.app
- **Vercel Docs**: https://vercel.com/docs
- **Django Docs**: https://docs.djangoproject.com
- **Angular Docs**: https://angular.io/docs

## 🔄 Actualizaciones Futuras

Para actualizar el despliegue:
1. Sube cambios a GitHub
2. Railway y Vercel detectarán automáticamente los cambios
3. Se desplegarán nuevas versiones

---

**¡Sistema listo para producción!** 🎉

- Frontend: https://tu-proyecto.vercel.app
- Backend API: https://tu-proyecto.railway.app/api/
- Admin Django: https://tu-proyecto.railway.app/admin/
