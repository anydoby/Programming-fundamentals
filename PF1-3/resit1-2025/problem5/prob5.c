/* file: prob5.c
   author: David De Potter
   description: PF 1/3rd resit 2025, problem 5,
                Digit inventory numbers
*/

#include <stdio.h>
#include <stdlib.h>
#include <assert.h>

//===================================================================
// Counts how many times each digit appears in the array and stores 
// for each digit d its count followed by the digit d itself
// Returns the new length of the transformed array
int countDigitOccurrences(int *digits, int len) {
  int counts[10] = {0}, j = 0;
  
    // count the occurrences of each digit
  for (int i = 0; i < len; ++i)
    ++counts[digits[i]];

    // store the counts and corresponding digits back into the array
  for (int d = 0; d < 10; ++d){
    if (counts[d]) {
      if (counts[d] >= 10) 
        digits[j++] = counts[d] / 10;
      digits[j++] = counts[d] % 10;
      digits[j++] = d;
    }
  }

  return j;
}

//===================================================================

int main() {
  int digits[100], n, s;
  int count = scanf("%d %d", &n, &s);
  assert(count == 2);

    // initialize the input array with the digits of n
  int len = 0;
  if (n >= 10)
    digits[len++] = n / 10;
  digits[len++] = n % 10;

    // transform the input array s times
  for (int i = 0; i < s; ++i)  
    len = countDigitOccurrences(digits, len);
  
    // print the resulting array
  for (int i = 0; i < len; ++i)
    printf("%d", digits[i]);
  printf("\n");

  return 0;
}