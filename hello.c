// A simple, standalone C program for bare-metal RISC-V
// Note: No #include <stdio.h> as we have no standard library.

// A simple implementation of puts to write to the QEMU console
void _puts(const char *s) {
    while (*s) {
        // Write character to the UART address for QEMU
        *(volatile unsigned int *)0x10000000 = *s++;
    }
}

void _start(void) {
    _puts("Hello, Bare-Metal World!\n");
    // Infinite loop to halt the processor
    while (1);
}