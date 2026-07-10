"""Shared utilities for the Streamlit dashboard."""

import sys
from pathlib import Path

# Make the repo root importable so `from src...` works regardless of how
# Streamlit is launched (locally or on Streamlit Cloud).
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import joblib
import streamlit as st

from src.config import MODEL_FILE
from src.data_loader import load_matches


@st.cache_data
def get_matches():
    """Load the cleaned matches dataset once per session; cached across pages."""
    return load_matches()


@st.cache_resource
def get_model_bundle():
    """Load the trained model bundle once; cached across pages and users."""
    return joblib.load(MODEL_FILE)