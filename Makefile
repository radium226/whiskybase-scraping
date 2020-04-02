SHELL = /bin/bash
.SHELLFLAGS = -o pipefail -e -c
.ONESHELL :

.venv/bin/activate:
	python -m "venv" ".venv"
	pip install "pip" --upgrade

.PHONY: requirements
requirements: .venv/bin/activate
	source ".venv/bin/activate"
	pip install -r "requirements.txt"

SEARCH = macallan

.PHONY: test
test:
	source ".venv/bin/activate"
	python -m "unittest"
.PHONY: crawl
crawl:
	source ".venv/bin/activate"
	scrapy crawl "whiskies" -a search_term="$(SEARCH)" -o "$(SEARCH).csv"
	iconv -f "UTF-8" -t "ISO-8859-1//TRANSLAT" "$(SEARCH).csv" -o - | sponge >"$(SEARCH).csv"
	unoconv --format "xlsx" "$(SEARCH).csv"

