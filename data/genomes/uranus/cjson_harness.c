/* [DEFINITIVE - V4.0 "MORTAL BATTLEFIELD"] */
#include "cJSON.h"
#include <stdio.h>
#include <stdlib.h>

int main(void) {
    char buffer[128];
    gets(buffer); // The classic, unsafe vulnerability
    cJSON *json = cJSON_Parse(buffer);
    if (json != NULL) {
        cJSON_Delete(json);
    }
    return 0;
}