package java_fundamentals_session1.oop;

public class StudentDemo {

    public static void main(String[] args) {

        Student s1 = new Student("Shaili", 101, 88.5);
        s1.displayInfo();

        System.out.println("-----");

        GraduateStudent g1 = new GraduateStudent("Rahul", 201, 91.0, "AI");
        g1.displayInfo();

        System.out.println("-----");

        Student poly = new GraduateStudent("Priya", 202, 85.0, "ML");
        System.out.println("Polymorphism: " + poly.getType());
    }
}