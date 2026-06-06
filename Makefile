.PHONY: install run debug clean lint lint-strict

install:
	python3 -m pip install -r requirements.txt

run:
	python3 main.py maps/challenger/01_the_impossible_dream.txt

debug:
	python3 -m pdb main.py maps/challenger/01_the_impossible_dream.txt

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".mypy_cache" -exec rm -rf {} +

lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 .
	mypy . --strict