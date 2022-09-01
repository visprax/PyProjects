CC     := gcc
CFLAGS := -O3 -g -Wall -fPIC 
LFLAGS := -shared -lm

DIR := clib
SRC := $(DIR)/directg.c
LIB := $(DIR)/directg.so

all: libg

libg: $(SRC)
	$(CC) $(CFLAGS) $(LFLAGS) -I $(DIR) -o $(LIB) $(SRC)

clean:
	rm -f $(DIR)/directg.so

.PHONY: all clean
