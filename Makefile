install:
	install -d ~/bin/macro_expander
	install macro_expander/* ~/bin/macro_expander
	install scripts/expand-macros.py ~/bin
