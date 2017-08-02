all: clone_simple

clone_simple: clone_simple1.c
	$(CC) $< -o $@
	chmod +x $@

PHONY: clean
clean:
	rm -rf clone_simple
