package java_fundamentals_session1.exception;

import java.io.*;
import java.util.Scanner;

public class ExceptionDemo {

    // Division demo with exception handling
    public static void divisionDemo() {
        Scanner sc = new Scanner(System.in);
        try {
            System.out.print("Enter numerator: ");
            int num = sc.nextInt();

            System.out.print("Enter denominator: ");
            int den = sc.nextInt();

            int result = num / den;
            System.out.println("Result: " + result);

        } catch (ArithmeticException e) {
            System.out.println("Error: Cannot divide by zero.");
        } catch (Exception e) {
            System.out.println("Unexpected error: " + e.getMessage());
        } finally {
            sc.close();  // ✅ FIXED (resource leak solved)
            System.out.println("Division operation completed.");
        }
    }

    // File reading demo
    public static void fileReadDemo() {
        try {
            FileReader fr = new FileReader("sample.txt");
            BufferedReader br = new BufferedReader(fr);

            String line;
            System.out.println("Reading from file:");
            while ((line = br.readLine()) != null) {
                System.out.println(line);
            }

            br.close();

        } catch (FileNotFoundException e) {
            System.out.println("File not found.");
        } catch (IOException e) {
            System.out.println("Error reading file.");
        }
    }

    public static void main(String[] args) {
        divisionDemo();
        System.out.println("-----");
        fileReadDemo();
    }
}