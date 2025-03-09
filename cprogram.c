#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define NUMBER_COUNT 10  // Define how many random numbers will be generated

int main() {
    int i;
    float sum = 0.0, average;
    int numbers[NUMBER_COUNT];

    // Initialize the seed for random number generation
    srand(time(NULL));

    // Generate random numbers and calculate the sum
    for (i = 0; i < NUMBER_COUNT; i++) {
        numbers[i] = rand() % 100;  // Generates a random number between 0 and 99
        sum += numbers[i];          // Accumulate the sum
    }

    // Calculate the average
    average = sum / NUMBER_COUNT;

    // Display the results
    printf("Generated numbers: ");
    for (i = 0; i < NUMBER_COUNT; i++) {
        printf("%d ", numbers[i]);
    }
    printf("\nThe sum of the numbers is: %.2f\n", sum);
    printf("The average of the numbers is: %.2f\n", average);

    return 0;
}
