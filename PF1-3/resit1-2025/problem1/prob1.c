/* file: prob1.c
   author: David De Potter
   description: PF 1/3rd resit 2025, problem 1, Speeding fine
*/

#include <stdio.h>
#include <stdlib.h>
#include <assert.h>

//===================================================================
// evaluates the speeding fine based on R 
void evaluateSpeedingFine(double R) {
  if (R <= 1) {
    printf("LEGAL\n");
  } else if (R <= 1.2) {
    printf("MINOR\n");
  } else if (R <= 1.5) {
    printf("MAJOR\n");
  } else {
    printf("SEVERE\n");
  }
}

//===================================================================

int main() {
  int s, l;
  int count = scanf("%d %d", &l, &s);
  assert(count == 2);

  evaluateSpeedingFine((double)s / l);

  return 0;
}