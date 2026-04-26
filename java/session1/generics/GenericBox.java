package java.session1.generics;
public class GenericBox<T> {

    private T value;

    public GenericBox(T value) {
        this.value = value;
    }

    public void displayType() {
        System.out.println("Type: " + value.getClass().getSimpleName());
        System.out.println("Value: " + value);  
    }

    public static void main(String[] args) {

        GenericBox<Integer> intBox = new GenericBox<>(42);
        intBox.displayType();  

        GenericBox<String> strBox = new GenericBox<>("Hello Java");
        strBox.displayType();

        GenericBox<Double> dblBox = new GenericBox<>(3.14);
        dblBox.displayType();
    }
}