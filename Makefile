.PHONY: serve sync

sync:
	uv sync

serve:
	uv run app.py
