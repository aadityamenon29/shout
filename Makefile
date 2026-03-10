MODEL_DIR := $(HOME)/.local/share/shout/models
MODEL_URL := https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.en.bin

.PHONY: run setup install-model check

setup: install-model
	@echo "Installing Python dependencies..."
	@uv sync
	@echo ""
	@echo "Setup complete! Run 'make run' to start Shout."
	@echo "On first run you'll be prompted to grant permissions."

run:
	uv run python main.py

install-model:
	@mkdir -p $(MODEL_DIR)
	@if [ -f "$(MODEL_DIR)/ggml-small.en.bin" ]; then \
		echo "Model already downloaded."; \
	else \
		echo "Downloading ggml-small.en model (~466MB)..."; \
		curl -L -o "$(MODEL_DIR)/ggml-small.en.bin" "$(MODEL_URL)"; \
		echo "Done."; \
	fi

check:
	@uv run python permissions.py
