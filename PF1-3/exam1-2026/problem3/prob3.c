/* file: prob3.c
   author: David De Potter
   description: PF 1/3rd term 2026, problem 3, Unit fractions
   approach: we rewrite 1/n = 1/a + 1/b as b = n * a / (a - n)
   and check whether it is an integer value, that is, whether 
   (n * a) % (a - n) == 0. Since a ≤ b, we have: 
   1/n = 1/a + 1/b ≤ 1/a + 1/a = 2/a, so a ≤ 2 * n. Thus the
   range of a is n < a ≤ 2 * n.
*/

#include <stdio.h>
#include <stdlib.h>
#include <assert.h>

//===================================================================

int main() {
  int n, a, count = 0;
  assert(scanf("%d", &n) == 1);
    
    // iterate over all possible values of a in the range (n, 2n]
    // and check whether b = n * a / (a - n) is an integer
  for (a = n + 1; a <= 2 * n; ++a) {
    if ((n * a) % (a - n) == 0) 
      ++count;
  }

    // print the total number of valid pairs (a, b)
  printf("%d\n", count);
  
  return 0;
}