/* file: prob3.c
   author: David De Potter
   description: PF 1/3rd resit 2025, problem 3, 
                Remainder squash length
*/

#include <stdio.h>
#include <stdlib.h>
#include <assert.h>

//===================================================================
// Transforms an integer into the sum of its digits squared modulo m
int transform(int num, int m) {
  int sum = 0;
  while (num > 0) {
    int digit = num % 10;
    sum += digit * digit % m;
    num /= 10;
  }
  return sum;
}

//===================================================================

int main() {
  int n, m;
  int count = scanf("%d %d", &n, &m);
  assert(count == 2);

  int seen[1000] = {0}, prev = transform(n, m), idx = 1;
  
    // keep transforming the number until we find 
    // a previously seen value
  while (!seen[prev]) {
    seen[prev] = idx++;
    prev = transform(prev, m);
  }
    
    // print the cycle length = idx - seen[prev]
  printf("%d\n", idx - seen[prev]);

  return 0;
}