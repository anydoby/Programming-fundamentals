/* file: prob4.c
   author: David De Potter
   description: PF 1/3rd resit 2025, problem 4, 
                Pair cancellation
*/

#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <string.h>

//===================================================================
// Cancels adjacent equal-letter pairs in the given word
// Returns 1 if any cancellations were made, 0 otherwise
int cancelPairs(char *word) {
  int len = strlen(word);
  for (int i = 0; i < len - 1; ++i) {
    if (word[i] == word[i + 1]) {
      for (int j = i; j < len - 2; ++j)
        word[j] = word[j + 2];
      word[len - 2] = '\0';
      return 1;
    }
  }
  return 0;
}

//===================================================================

int main() {
  char word[21] = {0};
  int count = scanf("%s", word);
  assert(count == 1);

    // keep checking for adjacent equal-letter pairs and cancel them
    // until no cancellations can be made anymore
  while (cancelPairs(word));

  printf(strlen(word)? "%s\n" : "###\n", word);

  return 0;
}