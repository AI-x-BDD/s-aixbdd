PROJECT ?= projects/ch2-workflow-test/project.toml
export UV_CACHE_DIR := $(CURDIR)/.cache/uv
SOURCE_ROOT ?=
PORT ?= 60071
RUN = uv run --frozen python scripts/video.py --config "$(PROJECT)"
ifneq ($(SOURCE_ROOT),)
RUN += --source-root "$(SOURCE_ROOT)"
endif

.PHONY: setup audio check render preview review test
setup:
	uv sync --frozen
	$(RUN) setup
audio:
	$(RUN) prepare-audio
check: audio
	$(RUN) check
	uv run --frozen python tests/check_recorded.py --config "$(PROJECT)" $(if $(SOURCE_ROOT),--source-root "$(SOURCE_ROOT)")
	uv run --frozen python tests/check_visuals.py --config "$(PROJECT)" $(if $(SOURCE_ROOT),--source-root "$(SOURCE_ROOT)")
render:
	$(RUN) render
preview:
	$(RUN) serve --port $(PORT)

.PHONY: visual-samples
visual-samples:
	@test "$(PROJECT)" = "projects/ch2-skill-engineering/project.toml" || { echo "歷史樣稿只接受明確指定 PROJECT=projects/ch2-skill-engineering/project.toml" >&2; exit 2; }
	uv run --frozen python scripts/visual_proposal.py --config "$(PROJECT)" $(if $(SOURCE_ROOT),--source-root "$(SOURCE_ROOT)")

review:
	uv run --frozen python scripts/review.py --config "$(PROJECT)" $(if $(SOURCE_ROOT),--source-root "$(SOURCE_ROOT)") --capture
test:
	uv run --frozen python tests/check_review.py
	uv run --frozen python tests/check_motion.py --config "$(PROJECT)" $(if $(SOURCE_ROOT),--source-root "$(SOURCE_ROOT)")
