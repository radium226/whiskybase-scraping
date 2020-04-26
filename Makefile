SHELL = /bin/bash
.SHELLFLAGS = -o pipefail -e -c
.ONESHELL :

OUTPUT = output

.venv/bin/activate:
	python -m "venv" ".venv"
	pip install "pip" --upgrade


.PHONY: requirements
requirements: .venv/bin/activate
	source ".venv/bin/activate"
	pip install -r "requirements.txt"


.PHONY: test
test:
	source ".venv/bin/activate"
	python -m "unittest"


.PHONY: crawl-search
crawl-search:
	source ".venv/bin/activate"
	scrapy crawl "whiskies" \
		-a type="search" \
		-a term="$(TERM)" \
		-o "$(TERM).csv"
	iconv \
		-f "UTF-8" \
		-t "ISO-8859-1//TRANSLAT" \
			"$(TERM).csv" -o - | sponge >"$(TERM).csv"
	unoconv --format "xlsx" "$(TERM).csv"


.PHONY: crawl-new-releases
crawl-new-releases: $(OUTPUT)/$(YEAR).xlsx

$(OUTPUT)/$(YEAR).xlsx: $(OUTPUT)/$(YEAR)_ASCII.csv
	test -s "$(OUTPUT)/$(YEAR)_ASCII.csv" && \
		unoconv \
			--format="xlsx" \
			--output="$(OUTPUT)/$(YEAR).xlsx" \
			"$(OUTPUT)/$(YEAR)_ASCII.csv" || \
		true

$(OUTPUT)/$(YEAR)_ASCII.csv: $(OUTPUT)/$(YEAR)_UTF-8.csv
	iconv \
		-f "UTF-8" \
		-t "ISO-8859-1//TRANSLIT" \
			"$(OUTPUT)/$(YEAR)_UTF-8.csv" \
			-o "$(OUTPUT)/$(YEAR)_ASCII.csv"

$(OUTPUT)/$(YEAR)_UTF-8.csv:
	source ".venv/bin/activate"
	mkdir -p "$(OUTPUT)" || true
	scrapy crawl "whiskies" \
		-a type="new-releases" \
		-a year="$(YEAR)" \
		-o "$(OUTPUT)/$(YEAR)_UTF-8.csv"

.PHONY: clean
clean:
	rm -Rf "$(OUTPUT)"

MIN_YEAR = 1870
MAX_YEAR = 2020

BACKGROUND = false

.PHONY: crawl-all
crawl-all:
	if $(BACKGROUND); then \
		systemd-run \
			--user \
			--same-dir \
			--unit="whiskybase-scraping" \
			make crawl-all BACKGROUND=false	; \
	else \
		{ seq $(MIN_YEAR) $(MAX_YEAR) | xargs -I {} sh -c 'make crawl-new-releases YEAR="{}" || exit 255 ; } ; \
	fi
