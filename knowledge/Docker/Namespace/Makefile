TARGETS = uts_namespace clone_simple ipc_namespace

all: $(TARGETS)

ipc_namespace: ipc_namespace.c
	$(CC) $^ -o $@
	@chmod +x $@

uts_namespace: uts_namespace.c
	$(CC) $^ -o $@
	@chmod +x $@

clone_simple: clone_simple1.c
	$(CC) $< -o $@
	@chmod +x $@

PHONY: clean
clean:
	rm -rf $(TARGETS)
