VENV_PATH = $(HOME)/.virtualenvs/frigg-worker
BIN = $(VENV_PATH)/bin

all: $(VENV_PATH)

test: 
	tox	

$(VENV_PATH):
	mkvirtualenv frigg-worker 
	$(BIN)/pip install -r requirements.txt

build_test:
	rm -rf builds/
	redis-cli -n 2 lpush 'frigg:queue' '{"branch": "master", "sha": "superbhash", "clone_url": "https://github.com/frigg/frigg-worker.git", "owner": "frigg", "id": 2, "name": "frigg-worker"}'
	redis-cli -n 2 lpush 'frigg:queue' '{"branch": "hei-rolf", "sha": "superbhash", "clone_url": "https://github.com/frigg/frigg-worker.git", "owner": "frigg", "id": 3, "name": "frigg-worker", "pull_request_id": 17}'
	python -m frigg.worker.cli start
