"""Minimal Gradio entrypoint placeholder for the V2 MVP."""

from app import run_pipeline


def generate(setting: str) -> dict:
    return run_pipeline(setting, steps=3, export=True)
