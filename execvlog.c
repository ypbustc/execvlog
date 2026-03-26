#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <time.h>
#include <dlfcn.h>
#include <string.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <fcntl.h>

// 原始execve函数指针
static int (*original_execve)(const char *filename, char *const argv[], char *const envp[]) = NULL;

#define LOGHOST "202.38.95.44"
#define LOGPORT 9999

// 获取当前时间字符串
void get_time_str(char *buf, size_t size) {
    time_t now = time(NULL);
    struct tm *tm_info = localtime(&now);
    strftime(buf, size, "%Y-%m-%d %H:%M:%S", tm_info);
}

void sendudp(char *buf, int len, char *host, int port)
{
        struct sockaddr_in si_other;
        int s, slen = sizeof(si_other);
        int l;
        if ((s = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)) == -1) {
                return;
        }
        memset((char *) &si_other, 0, sizeof(si_other));
        si_other.sin_family = AF_INET;
        si_other.sin_port = htons(port);
        if (inet_aton(host, &si_other.sin_addr) == 0) {
                close(s);
                return;
        }
        l = sendto(s, buf, len, 0, (const struct sockaddr *)&si_other, slen);
        close(s);
}


// 写入日志
void write_log(const char *filename, char *const argv[]) {
    char time_buf[64];
    int i;
    get_time_str(time_buf, sizeof(time_buf));
    
    // 构建命令行字符串
    char cmdline[1024] = {0};
    if (argv) {
        for (i = 0; argv[i] != NULL; i++) {
            if (i > 0) strncat(cmdline, " ", sizeof(cmdline) - strlen(cmdline) - 1);
            strncat(cmdline, argv[i], sizeof(cmdline) - strlen(cmdline) - 1);
        }
    }

    char buf[2048];

    snprintf(buf, 2047, "[%s] UID=%d PPID=%d PID=%d CMD=%s ARGS=%s\n",
                time_buf, getuid(), getppid(), getpid(), filename, cmdline);
    sendudp(buf, strlen(buf), LOGHOST, LOGPORT);
}

// 重写的execve函数
int execve(const char *filename, char *const argv[], char *const envp[]) {
    // 初始化原始execve函数
    if (!original_execve) {
        original_execve = dlsym(RTLD_NEXT, "execve");
    }
    
    // 记录进程信息
    write_log(filename, argv);
    
    // 调用原始execve函数
    return original_execve(filename, argv, envp);
}

// 构造函数，在库加载时自动执行
__attribute__((constructor)) void init(void) {
     original_execve = dlsym(RTLD_NEXT, "execve");
}
