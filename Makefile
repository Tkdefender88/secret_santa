.PHONY: venv test install help run

help:
	@echo "Available commands:"
	@echo "  make venv       - Create virtual environment"
	@echo "  make install    - Install dependencies"
	@echo "  make test       - Run tests"
	@echo "  make run        - Start Flask server"
	@echo "  make shell      - Activate venv (run: source venv.sh)"

venv:
	uv venv

install:
	uv pip install pytest flask --python .venv/bin/python

test:
	@.venv/bin/python -m pytest test_santa.py -v

run:
	.venv/bin/python app.py

shell:
	@echo "Run: source .venv/bin/activate"
