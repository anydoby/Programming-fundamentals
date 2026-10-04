/* file: prob4.c
   author: David De Potter
   description: PF 1/3rd term 2026, problem 4, Array folding
*/

#include <stdio.h>
#include <stdlib.h>
#include <assert.h>

//===================================================================

int main() {
  int n, k, arr[1000];
  assert(scanf(" %d %d", &n, &k) == 2);

    // read the array elements
  for (int i = 0; i < n; ++i)
    assert(scanf("%d ", &arr[i]) == 1);
    
    // perform k folds of the array
  for (int fold = 0; fold < k; ++fold) {
    int mid = n / 2;
      
      // fold the array by summing the first half with 
      // the mirrored second half
    for (int i = 0; i < mid; ++i)
      arr[i] += arr[n - 1 - i];

      // if the old length is odd, the middle element remains 
      // unchanged, so we count one extra element in the new length
    n = mid + (n % 2); 
  }
  
    // print the resulting folded array
  printf("[");
  for (int i = 0; i < n; ++i){
    printf("%d", arr[i]);
    printf(i < n - 1 ? "," : "]\n");
  }

  return 0;
}