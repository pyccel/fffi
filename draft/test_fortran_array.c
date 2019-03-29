#include <stddef.h>

  struct descr_dims {
    ptrdiff_t stride;
    ptrdiff_t lower_bound;
    ptrdiff_t upper_bound;
  };

  struct descr {
    void *base_addr;
    size_t offset;
    ptrdiff_t dtype;
    struct descr_dims dim[1]; // TODO: make this dynamic
  };
  
  
  
  
  
