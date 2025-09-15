UrbanMood Web App
=================

Production Deployment Prep
--------------------------

Stack:
- Python / Flask
- Gunicorn (WSGI)
- Static assets served by Flask (could be offloaded to CDN later)

Key Files:
- `app.py` : Flask application factory and routes
- `wsgi.py` : WSGI entrypoint (`gunicorn wsgi:application`)
- `render.yaml` : Render.com service definition
- `static/` : Production static assets
- `templates/index.html` : Main HTML template

Environment Variables:
- `MAILERSEND_API_KEY` (required for /send-email endpoint)
- `PORT` (optional; Render sets automatically)
- `FLASK_DEBUG` (optional; leave unset or `0` in production)
- `LOG_LEVEL` (default INFO)

Health Check:
`/health` returns `{ "status": "ok" }` for uptime monitoring.

Running Locally:
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export FLASK_DEBUG=1
python app.py
# or
gunicorn wsgi:application -b 0.0.0.0:5001 --log-level info
```

Render Deployment:
Render picks up `render.yaml` and executes:
```
buildCommand: pip install -r requirements.txt
startCommand: gunicorn app:app
```
You can optionally change startCommand to:
```
gunicorn wsgi:application -k gthread --threads 4 --timeout 60 --bind 0.0.0.0:$PORT
```

Missing Schedule Images:
If `clases-palermo.png` or `clases-cordon.png` are absent, UI shows a placeholder message instead of broken images. Upload real images to:
```
static/images/clases-palermo.png
static/images/clases-cordon.png
```

Caching:
Static assets served with `Cache-Control: public, max-age=86400, immutable`.

Security Headers Added:
- X-Content-Type-Options: nosniff
- X-Frame-Options: SAMEORIGIN
- Referrer-Policy: strict-origin-when-cross-origin

Next Improvements (Not Yet Implemented):
- Move static to CDN or object storage
- Add rate limiting to `/send-email`
- Add Sentry or similar error monitoring
- Add integration tests for `/send-email`

License: Proprietary / All rights reserved.
