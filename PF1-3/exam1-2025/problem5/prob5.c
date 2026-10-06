/* file: prob5.c
   author: David De Potter
   description: PF 1/3rd term 2025, problem 5,
                descriptive numbers
*/

#include <stdio.h>
#include <stdlib.h>
#include <assert.h>

//===================================================================
// Replaces runs with its next run-length encoding.
// Returns the new number of digits.
int computeRuns(int *runs, int len) {
  int next[965], j = 0;
    
  for (int i = 0; i < len; ) {
    int digit = runs[i], count = 0;

      // Count and consume one complete run of identical digits
    do {
      ++count;
      ++i;
    } while (i < len && runs[i] == digit);
      
      // Append the count followed by the digit
    next[j++] = count;
    next[j++] = digit;
  }
    
    // Copy the completed encoding back into the input array
  for (int i = 0; i < j; ++i)
    runs[i] = next[i];

  return j;
}


//===================================================================

int main() {
  int n, s, runs[965];
  assert(scanf("%d %d", &n, &s) == 2);
    
    // initialize the input array with the digits of n
  int len = 0;
  if (n >= 10)
    runs[len++] = n / 10;
  runs[len++] = n % 10;

    // compute s successive run-length encodings
  for (int i = 0; i < s; ++i)  
    len = computeRuns(runs, len);
  
    // print the resulting array
  for (int i = 0; i < len; ++i)
    printf("%d", runs[i]);
  printf("\n");

  return 0;
}