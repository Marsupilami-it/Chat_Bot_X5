#!/bin/sh

#python -m alembic upgrade head && \
python -m uvicorn api_service:app --host 0.0.0.0 --port 5000 --workers 1  "${@}"
