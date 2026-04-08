package java_fundamentals_session1.oop;

import java.util.Scanner;

public class FactorialCalculator {
    // Using a loop to find factorial
    public static long findFactorial(int num) {
        long result = 1;
        for (int i = 2; i <= num; i++) {
            result = result * i;
        }
        return result;
    }

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        System.out.print("Enter a number to find its factorial: ");
        int number = sc.nextInt();

        if (number < 0) {
            System.out.println("Factorial is not defined for negative numbers.");
        } else {
            System.out.println("Factorial of " + number + " = " + findFactorial(number));
        }
        sc.close();
    }
}
