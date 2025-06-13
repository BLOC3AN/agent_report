#!/bin/bash

# Start FastAPI in the background
uvicorn main:app --host 0.0.0.0 --port 5000 &

# Start Streamlit
# cd /app
streamlit run gui/gui_streamlit.py --server.port 8501 --server.address 0.0.0.0