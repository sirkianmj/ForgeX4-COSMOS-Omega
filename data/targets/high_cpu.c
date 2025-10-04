#include <stdio.h>
int main(void) {
    // A simple, CPU-intensive task.
    long long sum = 0;
    for (long long i = 0; i < 2000000000; i++) {
        sum += i;
    }
    printf("Result: %lld\n", sum);
    return 0;
}