PYTHON = python3
MAIN = main.py
MAP = maps/easy/01_linear_path.txt 

install:
	$(PYTHON) -m pip install -r requirements.txt

run:
	$(PYTHON) $(MAIN) $(MAP)

debug:
	$(PYTHON) -m pdb $(MAIN) $(MAP)

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .mypy_cache .pytest_cache

lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 .
	mypy . --strict


test:
	$(PYTHON) tests.py
