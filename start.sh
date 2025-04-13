#!/bin/bash
cd src
uvicorn analogapi.main:app --host 0.0.0.0 --port $PORT