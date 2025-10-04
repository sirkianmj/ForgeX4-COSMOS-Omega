#include <stdio.h>
#include <string.h>

void inspect_and_sanitize(char *input);
int main()
{
  char buffer[16];
  char post_buffer_canary[] = "SAFE";
  printf("Enter data:\n");
  fgets(buffer, sizeof(buffer), stdin);
  inspect_and_sanitize(buffer);
  printf("Data entered: %s\n", buffer);
  printf("Canary status: %s\n", post_buffer_canary);
  if (strcmp(post_buffer_canary, "SAFE") != 0)
  {
    printf("!! STACK CORRUPTION DETECTED !!\n");
  }
  else
  {
    printf("Canary is intact.\n");
  }
  return 0;
}

