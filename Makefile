.PHONY: help install test notebook deck all clean lint

# Default target
help:
	@echo "Comandos disponibles en DT_DSL:"
	@echo "  make install   - Instala dependencias con uv / pip"
	@echo "  make test      - Ejecuta la suite completa de 20 pruebas unitarias con pytest"
	@echo "  make notebook  - Genera y ejecuta de extremo a extremo el cuaderno 01_analisis_y_modelado_e2e.ipynb"
	@echo "  make deck      - Genera la presentación ejecutiva oficial (10 diapositivas en PDF y PPTX)"
	@echo "  make all       - Ejecuta tests, regenera el cuaderno y compila el deck"
	@echo "  make clean     - Limpia caches de python y temporales"

install:
	uv pip install -e ".[dev]" || pip install -e .

test:
	uv run pytest tests/ -v

notebook:
	uv run jupyter nbconvert --to notebook --execute --inplace notebooks/01_analisis_y_modelado_e2e.ipynb

deck:
	python scripts/generate_pdf_deck_10_slides.py
	python scripts/generate_pptx_deck_10_slides.py

all: test notebook deck
	@echo "[OK] Pipeline completo ejecutado con éxito."

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
