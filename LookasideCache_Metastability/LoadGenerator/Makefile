TARGET = TraceReplay
OBJS += TraceReplay.o
OBJS += TraceReader.o
LIBS += -lpthread
LIBS += -lcurl
LIBS += -lrt

CC = g++
#CFLAGS = -Wall -Werror -DDEBUG -g # debug flags
CFLAGS = -Wall -Werror -g -O2 # release flags
CFLAGS += -MMD -MP
LDFLAGS += -Llib $(LIBS)

default:	$(TARGET)
all:		$(TARGET)

$(TARGET):	$(OBJS)
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

%.o: %.c
	$(CC) $(CFLAGS) -c -o $@ $<

%.o: %.cpp
	$(CC) $(CFLAGS) -c -o $@ $<

DEPS = $(OBJS:%.o=%.d)
-include $(DEPS)

clean:
	-rm $(TARGET) $(OBJS) $(DEPS)
