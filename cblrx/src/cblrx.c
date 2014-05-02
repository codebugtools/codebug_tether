// stdlib requires this before #define or segfault on ptsname
#define _XOPEN_SOURCE 600
#include <stdlib.h>
#include <stdio.h>
#include <fcntl.h>
#include <errno.h>
#include <string.h>
#include <unistd.h>


#define PKT_BUF_SIZE 256

#define CMD_ID(b) ((b >> 5) & 0x7)
// #define CMD_ID_FILTER 0xE0 // top three bits is cmd_id
#define CMD_ID_GET 0
#define CMD_ID_SET 1
#define CMD_ID_GET_BULK 2
#define CMD_ID_SET_BULK 3
#define CMD_ID_READ 4
#define CMD_ID_WRITE 5
#define CMD_ID_ACK 6

#define CH_INDEX(b) ((b >> 2) & 0x7)
#define OR_MASK(b) ((b >> 1) & 0x1)


char rows[7] = {0, 0, 0, 0, 0, 0, 0};


int openpt(void);
char get_channel(int i);
void set_channel(int i, char v, char or_mask);
void draw_codebug(void);
void send_ack(int fd);


int main(void)
{
    // some useful vars
    char cv; // channel value
    char buf[PKT_BUF_SIZE];
    int start_ch, i, len,read_count;

    int fd = openpt();
    if (fd < 0) {
        return 1;
    }

    printf("Fake CodeBug serial port is: %s\n", ptsname(fd));

    while (1) {
        // get first byte of packet
        read_count = read(fd, buf, PKT_BUF_SIZE);
        if (read_count < 0) {
            fprintf(stderr, "%s\n", strerror(errno));
            break;
        }

        // act accordingly
        switch (CMD_ID(buf[0])) {
        case CMD_ID_GET:
            // get and return channel value
            cv = get_channel(CH_INDEX(buf[0]));
            write(fd, &cv, 1);
            break;

        case CMD_ID_SET:
            set_channel(CH_INDEX(buf[0]), buf[1], OR_MASK(buf[0]));
            send_ack(fd);
            break;

        case CMD_ID_GET_BULK:
            start_ch = CH_INDEX(buf[0]);
            len = buf[1];
            for (i = 0; i < len; i++) {
                buf[i] = get_channel(start_ch+i);
            }
            write(fd, buf, len);
            break;

        case CMD_ID_SET_BULK:
            start_ch = CH_INDEX(buf[0]);
            len = buf[1];
            for (i = 0; i < len; i++) {
                set_channel(start_ch+i, buf[2+i], OR_MASK(buf[0]));
            }
            send_ack(fd);
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

        // displaying 'leds'
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

void set_channel(int i, char v, char or_mask)
{
    if (or_mask) {
        v |= get_channel(i);
    }
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

void send_ack(int fd)
{
    const char ack_pkt = CMD_ID_ACK << 5;
    write(fd, &ack_pkt, 1);
}