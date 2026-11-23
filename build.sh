#!/usr/bin/env bash
# Render.com deployment script
# This script runs during the build phase on Render

set -e  # Exit on error

echo "=========================================="
echo "O-92 Website - Render.com Deployment"
echo "=========================================="

echo ""
echo "[1] Installing Python dependencies..."
pip install -r requirements.txt

echo ""
echo "[2] Creating database tables..."
python -c "
from app import create_app, db
app = create_app()
with app.app_context():
    db.create_all()
    print('[OK] Database tables created')
"

echo ""
echo "[3] Running Flask migrations..."
export FLASK_APP=run.py
flask db upgrade

echo ""
echo "[4] Parametrization status:"
if [ "$FILL_PARAM_TABLE" = "true" ] || [ "$FILL_PARAM_TABLE" = "1" ]; then
    echo "    FILL_PARAM_TABLE is enabled - will sync parametrization data"
else
    echo "    FILL_PARAM_TABLE is NOT set - will use database data as-is"
    echo "    To enable: add FILL_PARAM_TABLE=true to Render environment variables"
fi

echo ""
echo "=========================================="
echo "Deployment build completed successfully!"
echo "=========================================="
