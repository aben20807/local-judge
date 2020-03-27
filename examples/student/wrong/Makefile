CC := gcc
CFLAGS := -Wall
TARGET := scanner
v := 0

all: $(TARGET)

$(TARGET): main.c
	$(CC) $(CFLAGS) -o $@ $^

judge: all
	@python3 ../../../judge/judge.py -v ${v} || printf "or \`make judge v=1\`"

clean:
	rm -f $(TARGET)
