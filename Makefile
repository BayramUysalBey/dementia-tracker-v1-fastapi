.PHONY: run install build clean

ifeq ($(OS),Windows_NT)
PYTHON = python
PIP = pip
else
PYTHON = python3
PIP = pip3
endif

install: requirements.txt
	$(PIP) install -r requirements.txt

# FastAPI run command
run:
	$(PYTHON) -m uvicorn app.main:app --reload

build: 
	docker build -t dementia-tracker-v1 .

docker-run:
	docker run -p 8000:8000 dementia-tracker-v1

test:
	$(PYTHON) -m pytest tests/test.py -v

clean:
ifeq ($(OS),Windows_NT)
	if exist "build" rd /s /q build
	if exist "dist" rd /s /q dist
	if exist "dementia_tracker_v1.egg-info" rd /s /q dementia_tracker_v1.egg-info
	if exist ".pytest_cache" rd /s /q .pytest_cache
	for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
else
	rm -rf build dist dementia_tracker_v1.egg-info .pytest_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
endif