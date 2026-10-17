PROJECT ?= projects/ch2-skill-engineering/project.toml
export UV_CACHE_DIR := $(CURDIR)/.cache/uv
SOURCE_ROOT ?=
PORT ?= 60070
RUN = uv run --frozen python scripts/video.py --config "$(PROJECT)"
ifneq ($(SOURCE_ROOT),)
RUN += --source-root "$(SOURCE_ROOT)"
endif

.PHONY: setup audio check render preview
setup:
	uv sync --frozen
audio:
	$(RUN) prepare-audio
check: audio
	$(RUN) check
render:
	$(RUN) render
preview:
	$(RUN) serve --port $(PORT)

.PHONY: visual-samples
visual-samples:
	uv run --frozen python scripts/visual_proposal.py --config "$(PROJECT)" $(if $(SOURCE_ROOT),--source-root "$(SOURCE_ROOT)")
