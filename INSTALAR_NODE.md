# Instalación de Node.js para Frontend Angular

## Paso 1: Descargar Node.js
1. Visitar https://nodejs.org/
2. Descargar la versión **LTS** (recomendada para la mayoría de usuarios)
3. Ejecutar el instalador `.msi`

## Paso 2: Instalar Node.js
Durante la instalación:
- ✅ Aceptar términos de licencia
- ✅ Elegir destino de instalación (predeterminado: `C:\Program Files\nodejs\`)
- ✅ **IMPORTANTE**: Marcar opción **"Add to PATH"**
- ✅ Continuar con instalación predeterminada

## Paso 3: Verificar Instalación
```cmd
node --version
npm --version
```
Debe mostrar versiones (ej: `v18.x.x` y `9.x.x`)

## Paso 4: Instalar Dependencias Angular
```cmd
cd E:\panaderia_proyecto\frontend
npm install
```

## Paso 5: Ejecutar Frontend
```cmd
npm start
```
El frontend estará disponible en: http://localhost:4200

## Solución de Problemas

### Error: "node no se reconoce"
- Reiniciar Command Prompt después de instalar Node.js
- Verificar que `C:\Program Files\nodejs\` esté en PATH:
  ```cmd
  echo %PATH%
  ```
- Si no está, agregar manualmente:
  ```cmd
  set PATH=C:\Program Files\nodejs;%PATH%
  ```

### Error: "npm install" falla
- Usar proxy si estás detrás de firewall corporativo:
  ```cmd
  npm config set proxy http://proxy:puerto
  npm config set https-proxy http://proxy:puerto
  ```
- Limpiar cache:
  ```cmd
  npm cache clean --force
  ```

### Error: "Port 4200 already in use"
```cmd
npm start -- --port 4201
```

## Instalación Rápida (Alternativa)
Si tienes **Chocolatey**:
```cmd
choco install nodejs
```

Si tienes **Winget**:
```cmd
winget install OpenJS.NodeJS
```

## Verificación Rápida
```cmd
cd E:\panaderia_proyecto\frontend
npx --version
```
Si `npx` funciona, Angular CLI está disponible.

## Credenciales para Login
Una vez ejecutado el frontend:
- **Usuario**: `admin`
- **Contraseña**: `admin123`
- **API URL**: http://localhost:8000 (backend Django)