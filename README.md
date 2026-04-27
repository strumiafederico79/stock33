# Stock Control Pro Enterprise V2

## Incluye
- Docker + SQLite
- Login JWT
- Roles admin / operador
- Capacitor preparado
- ZXing JS
- Alembic preparado
- ReportLab contratos PDF premium
- Recharts dashboard admin avanzado
- Escáner QR / barcode real
- Clientes
- Equipos
- Eventos
- Checklists
- Backups

## Instalación
```bash
docker compose build --no-cache
docker compose up -d
```

## Acceso
- App: http://3.91.156.70/
- API: http://3.91.156.70:8000/docs
- Usuario: admin
- Contraseña: admin1234

## Cámara QR
En navegador móvil puede requerir HTTPS. Por IP HTTP puede fallar. Para uso real en móvil, compilar con Capacitor.

## Capacitor
```bash
cd frontend
npm install
npm run build
npx cap add android
npx cap sync android
npx cap open android
```
