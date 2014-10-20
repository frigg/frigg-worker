VENV_PATH = $(HOME)/.virtualenvs/frigg-worker
BIN = $(VENV_PATH)/bin

all: $(VENV_PATH)

test: 
	tox	

$(VENV_PATH):
	mkvirtualenv frigg-worker 
	$(BIN)/pip install -r requirements.txt
