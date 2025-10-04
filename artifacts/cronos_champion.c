#include <stdio.h>
#include <string.h>

void process_vulnerable_input(void)
{
  char buffer[16];
  printf("Cronos is waiting for vulnerable input...\n");
  fgets(buffer, 16, stdin);
  printf("Cronos processed the input.\n");
}

