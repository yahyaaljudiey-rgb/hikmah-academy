# Hikmah Academy Deployment

## Production files

- `wsgi.py`: WSGI entrypoint for production servers
- `requirements.txt`: minimal runtime dependencies
- `scripts/run_production.sh`: Gunicorn startup script

## 1. Install dependencies

```bash
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
```

## 2. Review runtime environment

Edit:

- `instance/runtime.env`
- use `instance/runtime.env.example` as the safe template

Important values:

- `FLASK_SECRET_KEY`
- `ADMIN_ACCESS_CODE`
- `TEACHER_ACCESS_CODE`
- `DATABASE_URL` if you move away from SQLite
- `SESSION_COOKIE_SECURE=1` in HTTPS production

Quick production checklist for `runtime.env`:

- replace all access codes if you will open the system publicly
- keep `FLASK_SECRET_KEY` long and random
- set `SESSION_COOKIE_SECURE=1` when HTTPS is active
- keep the SQLite path inside `instance/` unless you are moving to another database

## 3. Start production server

```bash
chmod +x scripts/run_production.sh
./scripts/run_production.sh
```

Default bind:

- `0.0.0.0:5000`

Optional overrides:

```bash
FLASK_HOST=0.0.0.0
FLASK_PORT=8000
GUNICORN_WORKERS=2
GUNICORN_THREADS=4
GUNICORN_TIMEOUT=120
./scripts/run_production.sh
```

## 4. Reverse proxy

Recommended:

- Nginx in front of Gunicorn
- HTTPS enabled
- proxy to `127.0.0.1:5000` or chosen internal port

Ready template:

- `deploy/nginx-hikmah-academy.conf`

Example flow:

```bash
sudo cp deploy/nginx-hikmah-academy.conf /etc/nginx/sites-available/hikmah-academy
sudo ln -s /etc/nginx/sites-available/hikmah-academy /etc/nginx/sites-enabled/hikmah-academy
sudo nginx -t
sudo systemctl reload nginx
```

Then update:

- `server_name`
- internal proxy port if you use a different Gunicorn port
- SSL later with Certbot or your preferred certificate flow

## 5. Current readiness

The app's internal readiness check is now passing.

Before public launch, verify:

- domain and HTTPS
- backup of `instance/hikmah_academy.db`
- file permissions for `data/` and `instance/`
- external access from teacher and student devices

## 6. Suggested systemd service

```ini
[Unit]
Description=Hikmah Academy
After=network.target

[Service]
User=yahya
WorkingDirectory=/home/yahya/hikmah_academy
Environment=FLASK_HOST=127.0.0.1
Environment=FLASK_PORT=5000
ExecStart=/home/yahya/hikmah_academy/scripts/run_production.sh
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```
