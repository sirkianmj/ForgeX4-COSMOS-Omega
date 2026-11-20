#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <linux/seccomp.h>
#include <netinet/in.h>
#include <poll.h>
#include <sched.h>
#include <seccomp.h>
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/prctl.h>
#include <sys/resource.h>
#include <sys/socket.h>
#include <sys/syscall.h>
#include <sys/time.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>

#if __has_include(<linux/landlock.h>)
#include <linux/landlock.h>
#define HAVE_LANDLOCK_HDR 1
#else
#define HAVE_LANDLOCK_HDR 0
#endif

static volatile pid_t g_child_pid = -1;
static volatile sig_atomic_t g_term_requested = 0;

static void on_term_signal(int sig) {
    (void)sig;
    g_term_requested = 1;
    if (g_child_pid > 0) {
        kill(-g_child_pid, SIGTERM);
    }
}

static uint64_t now_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000ULL + (uint64_t)(ts.tv_nsec / 1000000ULL);
}

static int resolve_executable(const char *cmd, char *out, size_t out_sz) {
    if (strchr(cmd, '/')) {
        if (strlen(cmd) >= out_sz) return -1;
        strcpy(out, cmd);
        return access(out, X_OK) == 0 ? 0 : -1;
    }
    const char *path_env = getenv("PATH");
    if (!path_env) path_env = "/usr/local/bin:/usr/bin:/bin";
    char *copy = strdup(path_env);
    if (!copy) return -1;
    char *saveptr = NULL;
    for (char *dir = strtok_r(copy, ":", &saveptr); dir; dir = strtok_r(NULL, ":", &saveptr)) {
        snprintf(out, out_sz, "%s/%s", dir, cmd);
        if (access(out, X_OK) == 0) {
            free(copy);
            return 0;
        }
    }
    free(copy);
    return -1;
}

static int send_fd(int sock, int fd) {
    char dummy = 'F';
    struct iovec iov = { .iov_base = &dummy, .iov_len = 1 };
    union {
        char buf[CMSG_SPACE(sizeof(int))];
        struct cmsghdr align;
    } u;
    memset(&u, 0, sizeof(u));
    struct msghdr msg = {0};
    msg.msg_iov = &iov;
    msg.msg_iovlen = 1;
    msg.msg_control = u.buf;
    msg.msg_controllen = sizeof(u.buf);
    struct cmsghdr *cmsg = CMSG_FIRSTHDR(&msg);
    cmsg->cmsg_level = SOL_SOCKET;
    cmsg->cmsg_type = SCM_RIGHTS;
    cmsg->cmsg_len = CMSG_LEN(sizeof(int));
    memcpy(CMSG_DATA(cmsg), &fd, sizeof(int));
    return sendmsg(sock, &msg, 0) < 0 ? -1 : 0;
}

static int recv_fd(int sock) {
    char dummy = 0;
    struct iovec iov = { .iov_base = &dummy, .iov_len = 1 };
    union {
        char buf[CMSG_SPACE(sizeof(int))];
        struct cmsghdr align;
    } u;
    memset(&u, 0, sizeof(u));
    struct msghdr msg = {0};
    msg.msg_iov = &iov;
    msg.msg_iovlen = 1;
    msg.msg_control = u.buf;
    msg.msg_controllen = sizeof(u.buf);
    if (recvmsg(sock, &msg, 0) <= 0) return -1;
    struct cmsghdr *cmsg = CMSG_FIRSTHDR(&msg);
    if (!cmsg || cmsg->cmsg_len != CMSG_LEN(sizeof(int))) return -1;
    int fd = -1;
    memcpy(&fd, CMSG_DATA(cmsg), sizeof(int));
    return fd;
}

static int probe_landlock_abi(void) {
#if HAVE_LANDLOCK_HDR && defined(__NR_landlock_create_ruleset) && defined(LANDLOCK_CREATE_RULESET_VERSION)
    int abi = (int)syscall(__NR_landlock_create_ruleset, NULL, 0, LANDLOCK_CREATE_RULESET_VERSION);
    return abi > 0 ? abi : 0;
#else
    return 0;
#endif
}

static void ll_add_path(int ruleset_fd, const char *path, uint64_t access_mask) {
#if HAVE_LANDLOCK_HDR && defined(__NR_landlock_add_rule)
    if (!path || !path[0]) return;
    int pfd = open(path, O_PATH | O_CLOEXEC);
    if (pfd < 0) return;
    struct landlock_path_beneath_attr pb = {0};
    pb.allowed_access = access_mask;
    pb.parent_fd = pfd;
    syscall(__NR_landlock_add_rule, ruleset_fd, LANDLOCK_RULE_PATH_BENEATH, &pb, 0);
    close(pfd);
#else
    (void)ruleset_fd; (void)path; (void)access_mask;
#endif
}

static int try_apply_landlock(const char *ro_path, const char *rw_path) {
#if HAVE_LANDLOCK_HDR && defined(__NR_landlock_create_ruleset)
    if (!ro_path && !rw_path) return 0;
    struct landlock_ruleset_attr attr = {0};
    attr.handled_access_fs =
        LANDLOCK_ACCESS_FS_EXECUTE |
        LANDLOCK_ACCESS_FS_WRITE_FILE |
        LANDLOCK_ACCESS_FS_READ_FILE |
        LANDLOCK_ACCESS_FS_READ_DIR |
        LANDLOCK_ACCESS_FS_REMOVE_DIR |
        LANDLOCK_ACCESS_FS_REMOVE_FILE |
        LANDLOCK_ACCESS_FS_MAKE_CHAR |
        LANDLOCK_ACCESS_FS_MAKE_DIR |
        LANDLOCK_ACCESS_FS_MAKE_REG |
        LANDLOCK_ACCESS_FS_MAKE_SOCK |
        LANDLOCK_ACCESS_FS_MAKE_FIFO |
        LANDLOCK_ACCESS_FS_MAKE_BLOCK |
        LANDLOCK_ACCESS_FS_MAKE_SYM;

    int ruleset_fd = (int)syscall(__NR_landlock_create_ruleset, &attr, sizeof(attr), 0);
    if (ruleset_fd < 0) return -1;

    ll_add_path(ruleset_fd, ro_path,
                LANDLOCK_ACCESS_FS_EXECUTE | LANDLOCK_ACCESS_FS_READ_FILE | LANDLOCK_ACCESS_FS_READ_DIR);
    ll_add_path(ruleset_fd, rw_path, attr.handled_access_fs);
    uint64_t dev_rw = LANDLOCK_ACCESS_FS_READ_FILE | LANDLOCK_ACCESS_FS_WRITE_FILE;
    ll_add_path(ruleset_fd, "/dev/null", dev_rw);
    ll_add_path(ruleset_fd, "/dev/urandom", dev_rw);
    ll_add_path(ruleset_fd, "/dev/zero", dev_rw);

    int rc = (int)syscall(__NR_landlock_restrict_self, ruleset_fd, 0);
    close(ruleset_fd);
    return rc == 0 ? 1 : -1;
#else
    (void)ro_path; (void)rw_path;
    return -1;
#endif
}

static int read_connect_family(int nfd, struct seccomp_notif *req) {
    uint64_t addr_ptr = req->data.args[1];
    uint64_t addr_len = req->data.args[2];
    if (addr_ptr == 0 || addr_len < sizeof(sa_family_t)) return -1;
    char mem_path[64];
    snprintf(mem_path, sizeof(mem_path), "/proc/%u/mem", req->pid);
    int mfd = open(mem_path, O_RDONLY | O_CLOEXEC);
    if (mfd < 0) {
        if (addr_len == sizeof(struct sockaddr_in)) return AF_INET;
        if (addr_len == sizeof(struct sockaddr_in6)) return AF_INET6;
        return -1;
    }
    sa_family_t fam = 0;
    ssize_t rd = pread(mfd, &fam, sizeof(fam), (off_t)addr_ptr);
    close(mfd);
    if (rd != (ssize_t)sizeof(fam)) return -1;
    if (seccomp_notify_id_valid(nfd, req->id) != 0) return -1;
    return (int)fam;
}

static void set_lim(int res, rlim_t val) {
    if (val == 0) return;
    struct rlimit rl = { .rlim_cur = val, .rlim_max = val };
    setrlimit(res, &rl);
}

static void emit_meta(const char *meta_file, const char *json_line) {
    if (meta_file && meta_file[0]) {
        FILE *f = fopen(meta_file, "w");
        if (f) {
            fputs(json_line, f);
            fclose(f);
            return;
        }
    }
    fputs(json_line, stdout);
}

int main(int argc, char **argv) {
    uint64_t cpu_sec = 2;
    uint64_t mem_bytes = 256ULL * 1024ULL * 1024ULL;
    uint64_t fsize_bytes = 64ULL * 1024ULL * 1024ULL;
    uint64_t nofile = 128;
    uint64_t wall_ms_limit = 3000;
    int allow_execve = 0;
    int allow_net_bind = 0;
    int allow_net_outbound = 0;
    int allow_fork = 0;
    int allow_priv_ops = 0;
    int allow_debug_ops = 0;
    int kill_on_violation = 1;
    const char *ro_path = NULL;
    const char *rw_path = NULL;
    const char *meta_file = NULL;

    int cmd_idx = -1;
    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "--") == 0) { cmd_idx = i + 1; break; }
        else if (strcmp(argv[i], "--cpu-sec") == 0 && i + 1 < argc) cpu_sec = strtoull(argv[++i], NULL, 10);
        else if (strcmp(argv[i], "--mem-bytes") == 0 && i + 1 < argc) mem_bytes = strtoull(argv[++i], NULL, 10);
        else if (strcmp(argv[i], "--fsize-bytes") == 0 && i + 1 < argc) fsize_bytes = strtoull(argv[++i], NULL, 10);
        else if (strcmp(argv[i], "--nofile") == 0 && i + 1 < argc) nofile = strtoull(argv[++i], NULL, 10);
        else if (strcmp(argv[i], "--wall-ms") == 0 && i + 1 < argc) wall_ms_limit = strtoull(argv[++i], NULL, 10);
        else if (strcmp(argv[i], "--allow-execve") == 0 && i + 1 < argc) allow_execve = atoi(argv[++i]);
        else if (strcmp(argv[i], "--allow-network") == 0 && i + 1 < argc) { int v = atoi(argv[++i]); allow_net_bind = v; allow_net_outbound = v; }
        else if (strcmp(argv[i], "--allow-net-bind") == 0 && i + 1 < argc) allow_net_bind = atoi(argv[++i]);
        else if (strcmp(argv[i], "--allow-net-outbound") == 0 && i + 1 < argc) allow_net_outbound = atoi(argv[++i]);
        else if (strcmp(argv[i], "--allow-fork") == 0 && i + 1 < argc) allow_fork = atoi(argv[++i]);
        else if (strcmp(argv[i], "--allow-priv-ops") == 0 && i + 1 < argc) allow_priv_ops = atoi(argv[++i]);
        else if (strcmp(argv[i], "--allow-debug-ops") == 0 && i + 1 < argc) allow_debug_ops = atoi(argv[++i]);
        else if (strcmp(argv[i], "--kill-on-violation") == 0 && i + 1 < argc) kill_on_violation = atoi(argv[++i]);
        else if (strcmp(argv[i], "--ro-path") == 0 && i + 1 < argc) ro_path = argv[++i];
        else if (strcmp(argv[i], "--rw-path") == 0 && i + 1 < argc) rw_path = argv[++i];
        else if (strcmp(argv[i], "--meta-file") == 0 && i + 1 < argc) meta_file = argv[++i];
    }

    if (cmd_idx < 0 || cmd_idx >= argc) {
        fprintf(stderr, "Usage: cosmos_enforcer [flags] -- cmd [args...]\n");
        return 2;
    }

    char resolved_cmd[PATH_MAX];
    if (resolve_executable(argv[cmd_idx], resolved_cmd, sizeof(resolved_cmd)) != 0) {
        emit_meta(meta_file,
            "{\"outcome\":\"spawn_error\",\"exit_code\":127,\"signal\":0,"
            "\"violations\":\"\",\"seccomp_active\":0,\"landlock_abi\":0,"
            "\"wall_ms\":0,\"cpu_user_ms\":0.000,\"cpu_sys_ms\":0.000,"
            "\"max_rss_kb\":0,\"minflt\":0,\"majflt\":0}\n");
        return 0;
    }

    int ll_abi = probe_landlock_abi();
    int sv[2];
    if (socketpair(AF_UNIX, SOCK_STREAM, 0, sv) < 0) {
        perror("socketpair");
        return 2;
    }

    struct sigaction sa;
    memset(&sa, 0, sizeof(sa));
    sa.sa_handler = on_term_signal;
    sigaction(SIGTERM, &sa, NULL);
    sigaction(SIGINT, &sa, NULL);

    uint64_t t_start = now_ms();
    pid_t pid = fork();
    if (pid < 0) {
        perror("fork");
        return 2;
    }

    if (pid == 0) {
        setpgid(0, 0);
        close(sv[0]);
        set_lim(RLIMIT_CPU, (rlim_t)cpu_sec);
        set_lim(RLIMIT_AS, (rlim_t)mem_bytes);
        set_lim(RLIMIT_FSIZE, (rlim_t)fsize_bytes);
        set_lim(RLIMIT_NOFILE, (rlim_t)nofile);

        if (prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) < 0) _exit(120);
        try_apply_landlock(ro_path, rw_path);

        scmp_filter_ctx ctx = seccomp_init(SCMP_ACT_ALLOW);
        if (!ctx) _exit(121);

        seccomp_rule_add(ctx, SCMP_ACT_NOTIFY, SCMP_SYS(execve), 0);
        seccomp_rule_add(ctx, SCMP_ACT_NOTIFY, SCMP_SYS(execveat), 0);

        if (!allow_net_bind && !allow_net_outbound) {
            seccomp_rule_add(ctx, SCMP_ACT_NOTIFY, SCMP_SYS(socket), 0);
        } else if (!allow_net_outbound) {
            seccomp_rule_add(ctx, SCMP_ACT_NOTIFY, SCMP_SYS(connect), 0);
        }

        if (!allow_fork) {
            seccomp_rule_add(ctx, SCMP_ACT_ERRNO(ENOSYS), SCMP_SYS(clone3), 0);
            seccomp_rule_add(ctx, SCMP_ACT_NOTIFY, SCMP_SYS(clone), 1,
                             SCMP_A0(SCMP_CMP_MASKED_EQ, CLONE_THREAD, 0));
            seccomp_rule_add(ctx, SCMP_ACT_NOTIFY, SCMP_SYS(fork), 0);
            seccomp_rule_add(ctx, SCMP_ACT_NOTIFY, SCMP_SYS(vfork), 0);
        }

        if (!allow_priv_ops) {
            seccomp_rule_add(ctx, SCMP_ACT_NOTIFY, SCMP_SYS(fchmod), 0);
            seccomp_rule_add(ctx, SCMP_ACT_NOTIFY, SCMP_SYS(fchmodat), 0);
            seccomp_rule_add(ctx, SCMP_ACT_NOTIFY, SCMP_SYS(fchownat), 0);
        }
        if (!allow_debug_ops) {
            seccomp_rule_add(ctx, SCMP_ACT_NOTIFY, SCMP_SYS(ptrace), 0);
            seccomp_rule_add(ctx, SCMP_ACT_NOTIFY, SCMP_SYS(process_vm_readv), 0);
            seccomp_rule_add(ctx, SCMP_ACT_NOTIFY, SCMP_SYS(process_vm_writev), 0);
        }

        if (seccomp_load(ctx) < 0) _exit(122);
        int nfd = seccomp_notify_fd(ctx);
        if (nfd < 0 || send_fd(sv[1], nfd) < 0) _exit(123);

        char ack = 0;
        if (read(sv[1], &ack, 1) != 1) _exit(124);
        close(nfd);
        close(sv[1]);

        execv(resolved_cmd, &argv[cmd_idx]);
        _exit(127);
    }

    g_child_pid = pid;
    setpgid(pid, pid);
    close(sv[1]);
    int nfd = recv_fd(sv[0]);
    char ack = 'K';
    if (nfd >= 0) {
        if (write(sv[0], &ack, 1) != 1) { }
    }
    close(sv[0]);

    struct seccomp_notif *req = NULL;
    struct seccomp_notif_resp *resp = NULL;
    if (nfd >= 0) seccomp_notify_alloc(&req, &resp);

    int exec_count = 0;
    int policy_killed = 0;
    int timed_out = 0;
    uint64_t term_sent_ms = 0;
    char violations[1024] = "";
    int status = 0;
    struct rusage ru;
    memset(&ru, 0, sizeof(ru));
    int reaped = 0;

    while (!reaped) {
        uint64_t now = now_ms();
        uint64_t elapsed = now - t_start;
        if (g_term_requested) {
            if (term_sent_ms == 0) {
                term_sent_ms = now;
                kill(-pid, SIGTERM);
            } else if (now - term_sent_ms > 400) {
                kill(-pid, SIGKILL);
            }
        } else if (elapsed >= wall_ms_limit) {
            timed_out = 1;
            kill(-pid, SIGKILL);
        }

        if (nfd >= 0) {
            struct pollfd pfd = { .fd = nfd, .events = POLLIN, .revents = 0 };
            int pr = poll(&pfd, 1, 5);
            if (pr > 0 && (pfd.revents & POLLIN)) {
                memset(req, 0, sizeof(*req));
                if (seccomp_notify_receive(nfd, req) == 0) {
                    memset(resp, 0, sizeof(*resp));
                    resp->id = req->id;
                    int nr = req->data.nr;
                    int allow = 1;
                    const char *vname = NULL;

                    if (nr == SCMP_SYS(execve) || nr == SCMP_SYS(execveat)) {
                        exec_count++;
                        if (exec_count == 1) {
                            allow = 1;
                        } else if (!allow_execve) {
                            allow = 0;
                            vname = "execve";
                        }
                    } else if (nr == SCMP_SYS(socket)) {
                        uint64_t dom = req->data.args[0];
                        if (!allow_net_bind && !allow_net_outbound && (dom == AF_INET || dom == AF_INET6)) {
                            allow = 0;
                            vname = "net_socket";
                        }
                    } else if (nr == SCMP_SYS(connect)) {
                        if (!allow_net_outbound) {
                            int fam = read_connect_family(nfd, req);
                            if (fam == AF_INET || fam == AF_INET6) {
                                allow = 0;
                                vname = "net_outbound";
                            }
                        }
                    } else if (nr == SCMP_SYS(clone) || nr == SCMP_SYS(fork) || nr == SCMP_SYS(vfork)) {
                        if (!allow_fork) {
                            allow = 0;
                            vname = "fork";
                        }
                    } else if (nr == SCMP_SYS(fchmod) || nr == SCMP_SYS(fchmodat) || nr == SCMP_SYS(fchownat)) {
                        if (!allow_priv_ops) {
                            allow = 0;
                            vname = "priv_ops";
                        }
                    } else if (nr == SCMP_SYS(ptrace) || nr == SCMP_SYS(process_vm_readv) || nr == SCMP_SYS(process_vm_writev)) {
                        if (!allow_debug_ops) {
                            allow = 0;
                            vname = "debug_ops";
                        }
                    }

                    if (allow) {
                        resp->flags = SECCOMP_USER_NOTIF_FLAG_CONTINUE;
                    } else {
                        resp->error = -EPERM;
                        resp->flags = 0;
                        if (vname && strlen(violations) + strlen(vname) + 4 < sizeof(violations)) {
                            if (violations[0]) strcat(violations, ",");
                            strcat(violations, vname);
                        }
                        if (kill_on_violation) {
                            policy_killed = 1;
                        }
                    }
                    seccomp_notify_respond(nfd, resp);
                    if (!allow && kill_on_violation) {
                        kill(-pid, SIGKILL);
                    }
                }
            }
        } else {
            usleep(2000);
        }

        pid_t w = wait4(pid, &status, WNOHANG, &ru);
        if (w == pid) {
            reaped = 1;
        }
    }

    if (nfd >= 0) {
        seccomp_notify_free(req, resp);
        close(nfd);
    }

    uint64_t wall_ms = now_ms() - t_start;
    double user_ms = ru.ru_utime.tv_sec * 1000.0 + ru.ru_utime.tv_usec / 1000.0;
    double sys_ms = ru.ru_stime.tv_sec * 1000.0 + ru.ru_stime.tv_usec / 1000.0;
    int exit_code = WIFEXITED(status) ? WEXITSTATUS(status) : -1;
    int term_sig = WIFSIGNALED(status) ? WTERMSIG(status) : 0;

    const char *outcome = "survived";
    if (policy_killed) outcome = "policy_killed";
    else if (timed_out) outcome = "timed_out";
    else if (term_sig == SIGXCPU) outcome = "rlimit_cpu_killed";
    else if (term_sig == SIGXFSZ) outcome = "rlimit_fsize_killed";
    else if (term_sig != 0) outcome = "crashed";
    else if (exit_code != 0) outcome = "nonzero_exit";

    char outbuf[2048];
    snprintf(outbuf, sizeof(outbuf),
           "{\"outcome\":\"%s\",\"exit_code\":%d,\"signal\":%d,"
           "\"violations\":\"%s\",\"seccomp_active\":%d,\"landlock_abi\":%d,"
           "\"wall_ms\":%llu,\"cpu_user_ms\":%.3f,\"cpu_sys_ms\":%.3f,"
           "\"max_rss_kb\":%ld,\"minflt\":%ld,\"majflt\":%ld}\n",
           outcome, exit_code, term_sig, violations, (nfd >= 0 ? 1 : 0), ll_abi,
           (unsigned long long)wall_ms, user_ms, sys_ms,
           ru.ru_maxrss, ru.ru_minflt, ru.ru_majflt);
    emit_meta(meta_file, outbuf);

    return 0;
}
