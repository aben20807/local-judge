CC := gcc
CFLAGS := -Wall
TARGET := scanner

all: $(TARGET)

$(TARGET): main.c
	$(CC) $(CFLAGS) -o $@ $^

judge: all
	python3 ../../../judge/judge.py -v 1

clean:
	rm -f $(TARGET)
