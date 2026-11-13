#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

void process_vulnerable_input(void) {
    char buffer[64];
    if (fgets(buffer, 64, stdin) == NULL) return;
    int mode = atoi(buffer);

    if (mode == 1) {
        /* Benign: I/O-bound. 300ms sustained I/O, low CPU. */
        FILE *f = fopen("/tmp/cosmos_io_test.txt", "w");
        if (f) {
            for (int chunk = 0; chunk < 30; chunk++) {
                for (int i = 0; i < 20000; i++) fprintf(f, "%d\n", i);
                fflush(f);
                usleep(10000);   /* 10ms sleep per chunk = 300ms total */
            }
            fclose(f);
            remove("/tmp/cosmos_io_test.txt");
        }
    } else {
        /* Attack: CPU-bound. ~0.56s at 100% on M5. */
        volatile long long sink = 0;
        for (long long i = 0; i < 1500000000LL; i++) sink += i;
        if (sink == -42) printf("impossible\n");
    }
}
