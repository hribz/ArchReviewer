#include <stdio.h>
#include <immintrin.h>

// test.c
/* this is 
a test file */
#define offset 1
#define func(a) int aa;\
                a=100;\
int a=0;

#ifdef __x86_64__
#define x86_defined 1
int c=0;
#elif defined(__arm__)
#define arm_defined 2
#elif defined(__aarch64__) || defined(__mips__)
#define aarch_defined 3
#endif

int main() {
    #if (x86_defined && a) && defined(__x86_64__)
    printf("x86\n");
    #endif

    #if arm_defined
    printf("arm\n");
    #endif
    return 0;
}