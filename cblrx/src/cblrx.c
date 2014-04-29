// stdlib requires this before #define or segfault on ptsname
#define _XOPEN_SOURCE 600
#include <stdlib.h>
#include <stdio.h>
#include <fcntl.h>
#include <errno.h>
#include <string.h>
#include <unistd.h>
// #include "cblrx.h"


#define CMD_ID(b) ((b >> 5) & 0x7)
// #define CMD_ID_FILTER 0xE0 // top three bits is cmd_id
#define CMD_ID_GET 0
#define CMD_ID_SET 1
#define CMD_ID_GET_BULK 2
#define CMD_ID_SET_BULK 3
#define CMD_ID_READ 4
#define CMD_ID_WRITE 5

#define CH_INDEX(b) ((b >> 2) & 0x7)


char rows[6] = {0, 0, 0, 0, 0, 0};


int openpt(void);
char get_channel(int i);
void set_channel(int i, char v);
void draw_codebug(void);


int main(void)
{
    int read_count;
    char buf = 0;

    int fd = openpt();
    if (fd < 0) {
        return 1;
    }

    printf("Fake CodeBug serial port is: %s\n", ptsname(fd));

    while (1) {
        // get first byte of packet
        read_count = read(fd, &buf, 1);
        if (read_count < 0) {
            fprintf(stderr, "%s\n", strerror(errno));
            break;
        }
        switch (CMD_ID(buf)) {
        case CMD_ID_GET:
            // printf("cmd: CMD_ID_GET\n");
            buf = get_channel(CH_INDEX(buf));
            write(fd, &buf, 1);
            break;
        case CMD_ID_SET:
            // printf("cmd: CMD_ID_SET\n");
            ; // can't have decleration after label
            const char index = CH_INDEX(buf);
            read(fd, &buf, 1);
            set_channel(index, buf);
            break;
        case CMD_ID_GET_BULK:
            printf("cmd: CMD_ID_GET_BULK\n");
            break;
        case CMD_ID_SET_BULK:
            printf("cmd: CMD_ID_SET_BULK\n");
            break;
        case CMD_ID_READ:
            printf("cmd: CMD_ID_READ\n");
            break;
        case CMD_ID_WRITE:
            printf("cmd: CMD_ID_WRITE\n");
            break;
        default:
            printf("ERR:Could not determine cmd.\n");
            return 1;
        }

        system("clear");
        draw_codebug();
    }

    return 0;
}

int openpt(void)
{
    int fd = posix_openpt(O_RDWR);
    if (fd < 0) {
        fprintf(stderr, "Error %d on posix_openpt()\n", errno);
        return -1;
    }

    // using read_count here becasue we don't need it yet
    if (grantpt(fd) != 0) {
        fprintf(stderr, "Error %d on grantpt()\n", errno);
        return -1;
    }

    if (unlockpt(fd) != 0) {
        fprintf(stderr, "Error %d on unlockpt()\n", errno);
        return -1;
    }

    return fd;
}

char get_channel(int i)
{
    return rows[i] & 0x1f; // get_row
}

void set_channel(int i, char v)
{
    rows[i] = v & 0x1f; // set_row
}

void draw_codebug(void)
{
    int i, j;
    char row[6] = {0, 0, 0, 0, 0, 0}; // sixth is EOL
    for (i = 0; i <= 4; i++) {
        for (j = 0; j <= 4; j++) {
            row[4-j] = (rows[i] >> j) & 1 ? '#' : '-';
        }
        printf("%s\n", row);
    }
}