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

int c0;

#elif defined(__arm__)
#define arm_defined 5
int c1;
#elif defined(__aarch64__) || defined(__arm__)
#define aarch_defined 3
int c2;
#endif

int main() {
    #if (x86_defined && a) && defined(__x86_64__)
    printf("x86\n");
    #endif

    #if arm_defined
    printf("arm\n");
    #endif
    printf("git diff");
    return 0;
}