/* file: prob2.c
   author: David De Potter
   description: PF 1/3rd resit 2025, problem 2, 
                Max–min replacement until stability
*/

#include <stdio.h>
#include <stdlib.h>
#include <assert.h>

//===================================================================
// computes the transformation of n by replacing every occurrence of
// the maximum digit in n by d = max digit - min digit
int transform(int n) {
  int maxDigit = 0, minDigit = 9, num = n;

  while (num) {
    int digit = num % 10;
    if (digit > maxDigit) maxDigit = digit;
    if (digit < minDigit) minDigit = digit;
    num /= 10;
  }

  int d = maxDigit - minDigit;
  int result = 0, pos = 1;

  while (n) {
    int digit = n % 10;
    if (digit == maxDigit) digit = d;
    result += digit * pos;
    pos *= 10;
    n /= 10;
  }

  return result;
}

//===================================================================

int main() {
  int number, iter;
  int count = scanf("%d", &number);
  assert(count == 1);

  iter = 0;
  while (1) {
    int newNumber = transform(number);
    if (newNumber == number) break;
    number = newNumber;
    ++iter;
  }

  printf("%d %d\n", number, iter);

  return 0;
}