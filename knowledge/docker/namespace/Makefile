SRCS := uts_namespace.c clone_simple.c ipc_namespace.c pid_namespace.c mount_namespace.c
TARGETS := $(basename $(SRCS))

-include sub.make

all: $(TARGETS)

sub.make: Makefile
	$(foreach ssrc, $(SRCS), $(shell printf "$(basename $(ssrc)): $(ssrc)\n\t$(CC) $(ssrc) -o $(basename $(ssrc))\n\t@chmod +x $(basename $(ssrc))\n" >> $@))

PHONY: clean
clean:
	rm -rf $(TARGETS) sub.make
