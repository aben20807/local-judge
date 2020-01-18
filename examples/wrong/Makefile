CC := gcc
CFLAGS := -Wall
TARGET := scanner

all: $(TARGET)

$(TARGET): main.c
	$(CC) $(CFLAGS) -o $@ $^

clean:
	rm -f $(TARGET)