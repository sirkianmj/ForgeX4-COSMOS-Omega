/*
 * uranus_v1.0.c - The Static Test Harness
 * [DEFINITIVE STATIC ASSET] This file provides the main() function. It is
 * no longer treated as a genome and will be compiled directly.
 */
#include <stdio.h>

// Forward declaration for the function in the Cronos genome we are testing.
void process_vulnerable_input(void);

int main() {
    // This harness does one thing: it calls the vulnerable function.
    process_vulnerable_input();
    return 0;
}