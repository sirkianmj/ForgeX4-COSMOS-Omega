// data/genomes/cjson/cjson_parse_shim.h

/*
 * This is a shim header file for pycparser.
 * It includes the necessary fake libc headers to allow the parsing
 * of real-world C files like cJSON.c that have implicit dependencies
 * on standard library functions and types.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <math.h>
#include <float.h>