#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

void process_vulnerable_input(void) {
    char buffer[64];
    if (fgets(buffer, 64, stdin) == NULL) return;
    int mode = atoi(buffer);

    if (mode == 1) {
        /* Benign: I/O-bound. ~300ms, low CPU, low memory. */
        FILE *f = fopen("/tmp/cosmos_io_test.txt", "w");
        if (f) {
            for (int chunk = 0; chunk < 30; chunk++) {
                for (int i = 0; i < 20000; i++) fprintf(f, "%d\n", i);
                fflush(f);
                usleep(10000);
            }
            fclose(f);
            remove("/tmp/cosmos_io_test.txt");
        }
    } else if (mode == 2) {
        /* CPU attack: ~0.56s at 100% CPU. */
        volatile long long sink = 0;
        for (long long i = 0; i < 1500000000LL; i++) sink += i;
        if (sink == -42) printf("impossible\n");
    } else if (mode == 3) {
        /* Memory attack: ~200MB resident for 2s. */
        size_t sz = 200UL * 1024 * 1024;
        volatile char *big = malloc(sz);
        if (big) {
            for (size_t i = 0; i < sz; i += 4096) big[i] = 0x41;
            sleep(2);
            free((void*)big);
        }
    }
}
