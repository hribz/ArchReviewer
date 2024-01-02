#include <stdio.h>
#include <mmintrin.h>
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
#define new_add 2
int c=0;
#elif defined(__arm__)
#define arm_defined 2
#elif defined(__aarch64__) || defined(__mips__)
#define aarch_defined 3
#endif


#define N 100000
#define M 1024
int a[M], b[M], c[M];
 
int add_sse2(int size, int *a, int *b, int *c) {
    int i = 0;
    for (; i + 4 <= size; i += 4) {
        __m64 ma = *((__m64*) &a[i]);
        __m64 mb = *((__m64*) &b[i]);
 
        ma = _mm_add_pi32(ma, mb);
        
        _mm_storeu_si128((__m64*) &c[i], ma);
    }
}

int main() {
    #if (x86_defined && a) && defined(__x86_64__)
    printf("x86\n");
    #endif

    #if arm_defined
    printf("arm\n");
    #endif

    return 0;
}