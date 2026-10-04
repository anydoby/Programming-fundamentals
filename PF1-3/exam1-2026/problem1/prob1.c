/* file: prob1.c
   author: David De Potter
   description: PF 1/3rd term 2026, problem 1, Clock
*/

#include <stdio.h>
#include <stdlib.h>
#include <assert.h>

//=================================================================

int main() {
  int h, m, d;

  assert(scanf("%d %d %d", &h, &m, &d) == 3);
    
    // convert the time to minutes and add the offset in minutes
  int t = 60 * h + m + d;
    
    // print the resulting time in HH:MM format
  printf("%02d:%02d\n", (t / 60) % 24, t % 60);
  
  return 0;
}