PHONY:all
all: test-if test-foreach test-patsubst test-filter test-targetval
	@echo tangjiajia-1stdependency $<
	@echo tangjiajia-alldependencies $^
	@echo tangjiajia-target $@
LOCAL_SRC := $(if $(SRC) $(SRC),'/home/tangjiajia')
test-if:
	@echo test-if $(LOCAL_SRC)
my-dir := /home/tangjiajia/workspace/my-codes/scmroad/scripts/bash \
/home/tangjiajia/workspace/my-codes/scmroad/scripts/gerrit_op

LOCAL_FILES := $(foreach dir, $(my-dir), $(wildcard $(dir)/*))
test-foreach: 
	@echo test-foreach $(LOCAL_FILES)

#$(patsubst PATTERN, REPLACEMENT, TEXT) 
PATSUBST_FILES := $(patsubst %.py, %.pyc, $(foreach file, $(LOCAL_FILES), $(notdir $(file))))
test-patsubst:
	@echo test-patsubst $(PATSUBST_FILES)

test-filter:
	@echo test-filter $(sort $(filter %.sh %.c, $(PATSUBST_FILES)))

test-targetval: LOCAL_SRC := a.c
test-targetval: LOCAL_SRC += b.c c.c
test-targetval: LOCAL_SRC ?= d.c e.c f.c
test-targetval:
	@echo test-targetval $(LOCAL_SRC)
