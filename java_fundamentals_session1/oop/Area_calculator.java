package java_fundamentals_session1.oop;

import java.util.Scanner;

public class Area_calculator {

    static final double PI = 3.14159;

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        System.out.println("Choose a shape:");
        System.out.println("1. Circle");
        System.out.println("2. Rectangle");  
        System.out.println("3. Triangle");
        System.out.print("Enter your choice: ");

        int choice = sc.nextInt();

        switch (choice) {
            case 1:
                System.out.print("Enter radius: ");
                double radius = sc.nextDouble();
                System.out.println("Area of Circle = " + (PI * radius * radius));
                break;

            case 2:
                System.out.print("Enter length: ");
                double length = sc.nextDouble();
                System.out.print("Enter breadth: ");
                double breadth = sc.nextDouble();
                System.out.println("Area of Rectangle = " + (length * breadth));
                break;

            case 3:
                System.out.print("Enter base: ");
                double base = sc.nextDouble();
                System.out.print("Enter height: ");
                double height = sc.nextDouble();
                System.out.println("Area of Triangle = " + (0.5 * base * height));
                break;

            default:
                System.out.println("Invalid choice");
        }

        sc.close();
    }
}