# ----------------------------------------------------------------------------
# Self-Documented Makefile
# ref: http://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
# ----------------------------------------------------------------------------
.PHONY: help
.DEFAULT_GOAL := help

help:											## ⁉️  - Display help comments for each make command
	@grep -E '^[0-9a-zA-Z_-]+:.*? .*$$'  \
		$(MAKEFILE_LIST)  \
		| awk 'BEGIN { FS=":.*?## " }; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'  \
		| sort

clean:	## 🗑️  - Removes pycache and test artifacts
	@echo "🗑️ - Removing __pycache__ and test artifacts"
	rm -rf .tox
	find . -type d -name  "__pycache__" -exec rm -r {} +

package-setup:
	@echo "📦 - Packaging for PyPI"
	flit build --setup-py

package: clean package-setup  ## 📦 - Package for PyPI

test:  ## 🧪 - Run test suite
	@echo "🧪 - Running test suite"
	tox
