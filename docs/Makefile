# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD  ?= sphinx-build
SOURCEDIR    = .
BUILDDIR     = _build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

# Custom targets for convenience
.PHONY: clean html livehtml serve

clean:
	rm -rf $(BUILDDIR)/*

html:
	@$(SPHINXBUILD) -b html "$(SOURCEDIR)" "$(BUILDDIR)/html" $(SPHINXOPTS)
	@echo
	@echo "Build finished. The HTML pages are in $(BUILDDIR)/html."

livehtml:
	sphinx-autobuild "$(SOURCEDIR)" "$(BUILDDIR)/html" $(SPHINXOPTS)

serve: html
	@echo "Serving documentation at http://localhost:8080"
	@cd $(BUILDDIR)/html && python -m http.server 8080

# Development commands
dev-setup:
	pip install sphinx sphinx-rtd-theme sphinx-autobuild

dev-build: clean html
	@echo "Development build complete"

dev-watch:
	sphinx-autobuild -b html "$(SOURCEDIR)" "$(BUILDDIR)/html" --host 0.0.0.0 --port 8080

# Production commands
prod-build: clean
	@$(SPHINXBUILD) -b html "$(SOURCEDIR)" "$(BUILDDIR)/html" -W --keep-going
	@echo "Production build complete"

# Check for broken links
linkcheck:
	@$(SPHINXBUILD) -b linkcheck "$(SOURCEDIR)" "$(BUILDDIR)/linkcheck" $(SPHINXOPTS)

# Generate API documentation
apidoc:
	sphinx-apidoc -o api/ ../apps/ --force --separate

# Build all formats
all: clean html epub pdf
	@echo "All documentation formats built"

epub:
	@$(SPHINXBUILD) -b epub "$(SOURCEDIR)" "$(BUILDDIR)/epub" $(SPHINXOPTS)
	@echo "Build finished. The epub file is in $(BUILDDIR)/epub."

latexpdf:
	@$(SPHINXBUILD) -b latex "$(SOURCEDIR)" "$(BUILDDIR)/latex" $(SPHINXOPTS)
	@echo "Running LaTeX files through pdflatex..."
	$(MAKE) -C $(BUILDDIR)/latex all-pdf
	@echo "pdflatex finished; the PDF files are in $(BUILDDIR)/latex."

pdf: latexpdf 