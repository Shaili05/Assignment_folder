package java_fundamentals_session1.oop;

public class GraduateStudent extends Student {

    private String researchTopic;

    public GraduateStudent(String name, int rollNumber, double marks, String researchTopic) {
        super(name, rollNumber, marks);  // THIS LINE NEEDS Student
        this.researchTopic = researchTopic;
    }

    @Override
    public String getType() {
        return "Graduate Student";
    }

    public void displayInfo() {
        super.displayInfo();
        System.out.println("Research Topic: " + researchTopic);
    }
}