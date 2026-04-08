package java_fundamentals_session1.oop;

public class ArrayOperations {
    // Find average of array elements
    public static double findAverage(int[] arr) {
        int total = 0;
        for (int num : arr) {
            total += num;
        }
        return (double) total / arr.length;
    }

    // Bubble sort in ascending order
    public static void bubbleSort(int[] arr) {
        int n = arr.length;
        for (int i = 0; i < n - 1; i++) {
            for (int j = 0; j < n - i - 1; j++) {
                if (arr[j] > arr[j + 1]) {
                    int temp = arr[j];
                    arr[j] = arr[j + 1];
                    arr[j + 1] = temp;
                }
            }
        }
    }

    // Linear search
    public static int linearSearch(int[] arr, int target) {
        for (int i = 0; i < arr.length; i++) {
            if (arr[i] == target) return i;
        }
        return -1;
    }

    public static void main(String[] args) {
        int[] numbers = {45, 12, 78, 3, 56, 23, 9};

        System.out.println("Average: " + findAverage(numbers));

        bubbleSort(numbers);
        System.out.print("Sorted Array: ");
        for (int n : numbers) System.out.print(n + " ");
        System.out.println();

        int index = linearSearch(numbers, 56);
        if (index != -1) {
            System.out.println("56 found at index: " + index);
        } else {
            System.out.println("Element not found.");
        }
    }  
}
