/* file: prob2.c
   author: David De Potter
   description: PF 1/3rd term 2026, problem 2, Road to zero
*/

#include <stdio.h>
#include <stdlib.h>
#include <assert.h>

//===================================================================
// Reverses the decimal digits of a given integer.
// Leading zeros in the reversed representation are discarded;
// for example, reverse(120) returns 21.
int reverse(int n) {
  int rev = 0;
  while (n) {
    rev = rev * 10 + n % 10;
    n /= 10;
  }
  return rev;
}

//===================================================================

int main() {
  int number, iter = 0, difference = 1;

  assert(scanf("%d", &number) == 1);
    
    // repeatedly replace the number with the absolute difference
    // between itself and its digit reversal until it becomes zero
  while (difference != 0) {
    int rev    = reverse(number);
    difference = abs(number - rev);
    number     = difference;
    ++iter;
  }
    
    // print the number of iterations it took to reach zero
  printf("%d\n", iter);

  return 0;
}