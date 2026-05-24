#include <unistd.h>
#include <sys/wait.h>
#include <sys/stat.h>
#include <signal.h>
#include <fcntl.h>
#include <stdio.h>

int config_exists() {
    struct stat st;
    return stat("config.json", &st) == 0;
}

void create_default_config(const char *app_path) {
    int pipefd[2];
    pipe(pipefd);
    pid_t pid = fork();
    if (pid == 0) {
        dup2(pipefd[0], STDIN_FILENO);
        close(pipefd[0]);
        close(pipefd[1]);
        int null_fd = open("/dev/null", O_WRONLY);
        if (null_fd >= 0) {
            dup2(null_fd, STDOUT_FILENO);
            dup2(null_fd, STDERR_FILENO);
            close(null_fd);
        }
        execl(app_path, app_path, NULL);
        _exit(1);
    }
    close(pipefd[0]);
    write(pipefd[1], "\n", 1);
    close(pipefd[1]);
    while (!config_exists())
        usleep(100000);
    kill(pid, SIGTERM);
    waitpid(pid, NULL, 0);
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s <app_path>\n", argv[0]);
        return 1;
    }
    const char *app_path = argv[1];

    if (!config_exists())
        create_default_config(app_path);

    execl(app_path, app_path, NULL);
    return 1;
}
