#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>

typedef struct array_dims array_dims;
struct array_dims {
    uintptr_t upper_bound;  // TODO: replace this by extent
    uintptr_t stride;
    uintptr_t lower_bound;
};


typedef struct array_1d array_1d;
struct array_1d {
    void *base_addr;
    size_t elem_size;
    uintptr_t reserved;
    uintptr_t info;
    uintptr_t rank;
    uintptr_t reserved2;
    struct array_dims dim[1];
};

extern void test_(array_1d *x);

int main(int argc, char **argv) {
    printf("testing ifort\n");
    int len = 10;
    int size = sizeof(double);      
    double *data = (double*) malloc(len*size);
    
    int i;
    for (i=0; i<len; i++) data[i] = 0.0;
    
    array_1d x;
    x.base_addr = data;
    x.elem_size = size;
    x.reserved = 0;
    x.info = 0;
    x.info |= 1 << 1;
    printf("%x\n", x.info);
    
    x.info |= 1 << 2;
    x.info |= 1 << 3;
    x.info |= 1 << 8;
    x.rank = 1;
    x.reserved2 = 0;
    x.dim[0].upper_bound = len;
    x.dim[0].stride = sizeof(double);
    x.dim[0].lower_bound = 1;
    
    printf("%f %f\n", data[0], data[len-1]);
    test_(&x);
    printf("%f %f\n", data[0], data[len-1]);
    
    free(data);
}
