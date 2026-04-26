package java.session1.collections;
import java.util.ArrayList;
import java.util.HashMap;

public class DataTypesDemo {

    public static void main(String[] args) {

        int a = 10;
        int b = 3;

        System.out.println("Primitive Types:");
        System.out.println("int a: " + a + ", int b: " + b);

        String name = "Shaili";
        ArrayList<Integer> numbers = new ArrayList<>();
        numbers.add(10);
        numbers.add(20);
        numbers.add(30);

        HashMap<String, Integer> scores = new HashMap<>();
        scores.put("Maths", 95);
        scores.put("Science", 88);

        System.out.println("\nReference Types:");
        System.out.println("String: " + name);
        System.out.println("ArrayList: " + numbers);
        System.out.println("HashMap: " + scores);

        System.out.println("\nArithmetic:");
        System.out.println("a + b = " + (a + b));

        // ✅ FIXED relational
        System.out.println("\nRelational:");
        System.out.println("a > b: " + (a > b));
        System.out.println("a == b: " + (a == b));

        System.out.println("\nLogical:");
        System.out.println("(a > b && b > 0): " + (a > b && b > 0));
        System.out.println("(a < b || b > 0): " + (a < b || b > 0));
    }
}