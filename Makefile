VENV_PATH = $(HOME)/.virtualenvs/frigg-worker
BIN = $(VENV_PATH)/bin

all: $(VENV_PATH)

test: 
	tox	

$(VENV_PATH):
	mkvirtualenv frigg-worker 
	$(BIN)/pip install -r requirements.txt

build_test:
	redis-cli -n 2 lpush 'frigg:queue' '{"branch": "master", "sha": "superbhash", "clone_url": "https://github.com/frigg/frigg-worker.git", "owner": "frigg", "id": 2, "name": "frigg-worker"}'
	python -m frigg.worker.cli start
