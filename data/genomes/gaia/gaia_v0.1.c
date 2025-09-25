/*
 * gaia_v0.1.c
 * The initial, vulnerable application.
 *
 * This program contains a classic buffer overflow vulnerability. It reads user
 * input into a buffer that is too small, using the unsafe gets() function.
 */
#include <stdio.h>
#include <string.h>

// Forward declaration for the function that Cronos will provide.
// In a real scenario, this would be in a shared header file.
void inspect_and_sanitize(char* input);

int main() {
    // A small buffer that is easy to overflow.
    char buffer[16];
    char post_buffer_canary[] = "SAFE"; // A simple "canary" to check for overflow.

    printf("Enter data:\n");

    // The vulnerability: gets() does not check buffer length.
    // An input longer than 15 characters will corrupt the stack.
    gets(buffer);

    // This is the hook for our defender. Cronos's job will be to
    // inspect the input. In v0.1, it does nothing.
    inspect_and_sanitize(buffer);

    printf("Data entered: %s\n", buffer);
    printf("Canary status: %s\n", post_buffer_canary);

    // Check if the canary has been corrupted.
    if (strcmp(post_buffer_canary, "SAFE") != 0) {
        printf("!! STACK CORRUPTION DETECTED !!\n");
    } else {
        printf("Canary is intact.\n");
    }

    return 0;
}