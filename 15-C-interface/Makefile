CC     := gcc
CFLAGS := -O3 -g -Wall -fPIC
LFLAGS := -shared -lm

DIR := libg
SRC := $(DIR)/libg.c
LIB := $(DIR)/libg.so

all: lib

lib: $(SRC)
	$(CC) $(CFLAGS) $(LFLAGS) -I $(DIR) -o $(LIB) $(SRC)

clean:
	rm -f $(LIB)

.PHONY: all clean
