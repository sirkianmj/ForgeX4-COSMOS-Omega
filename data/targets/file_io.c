#include <stdio.h>
#include <stdlib.h>
int main(void) {
    // A simple, I/O-intensive task.
    FILE *fp = fopen("/tmp/testfile.tmp", "w+");
    for (int i = 0; i < 100000; i++) {
        fprintf(fp, "COSMOS-OMEGA\n");
    }
    fclose(fp);
    return 0;
}