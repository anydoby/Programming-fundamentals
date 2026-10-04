/* file: prob5.c
   author: David De Potter
   description: PF 1/3rd term 2026, problem 5,
                Designated survivor
*/

#include <stdio.h>
#include <stdlib.h>
#include <assert.h>


//===================================================================

int main() {
  int n, arr[1000];
    
    // read the number of elements and the array elements
  assert(scanf("%d\n", &n) == 1);
  for (int i = 0; i < n; ++i)
    assert(scanf(" %d", &arr[i]) == 1);

  int k = n, j = 0;

    // loop until only one element remains
  while (k > 1) {
    int current = j;
      // ignore complete laps around the remaining elements
    int jump = arr[j] % k;
    
      // jump to the next element step by step
      // skipping eliminated elements
    while (jump > 0) {
      if (arr[j] != 0)
        --jump;
      j = (j + 1) % n;
    }
      
      // eliminate the element from which the jump started 
      // by setting it to 0, and update the number of remaining elems
    arr[current] = 0;
    --k;

      // skip eliminated elements to reach the new current element;
      // this also selects the successor if the jump returned to 
      // its starting element
    while (arr[j] == 0)
      j = (j + 1) % n;
  }

    // print the designated survivor
  printf("%d\n", arr[j]);

  return 0;
}