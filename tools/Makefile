.PHONY: all etc html clean tags save load stage pkg test parallel

TOOLS ?= tools
SCONS ?= PYTHONPATH=$(TOOLS)/packages/SCons4 python3 $(TOOLS)/packages/SCons4/bin/scons

all:
	@$(SCONS) -f $(TOOLS)/SConstruct -j8 target-default

parallel:
	@$(SCONS) -f $(TOOLS)/SConstruct -j8 target-default

single:
	@$(SCONS) -f $(TOOLS)/SConstruct -j1 target-default

verbose:
	@PI_VERBOSE=1 $(SCONS) -f $(TOOLS)/SConstruct -j1 target-default

quiet:
	@$(SCONS) -f $(TOOLS)/SConstruct -j1 -s target-default

clean:
	@$(SCONS) -f $(TOOLS)/SConstruct -c
	rm -rf tmp env.sh dbg.sh tags
	find . -name \*.pyc -exec rm {} \;

tags:
	@$(SCONS) -f $(TOOLS)/SConstruct tags

stage:
	@$(SCONS) -f $(TOOLS)/SConstruct target-stage

mpkg:
	@$(SCONS) -f $(TOOLS)/SConstruct target-mpkg

pkg:
	@$(SCONS) -f $(TOOLS)/SConstruct target-pkg
