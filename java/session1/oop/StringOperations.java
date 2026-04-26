package java.session1.oop;
public class StringOperations {
    // Reverse a string
    public static String reverseString(String str) {
        String reversed = "";
        for (int i = str.length() - 1; i >= 0; i--) {
            reversed = reversed + str.charAt(i);
        }
        return reversed;
    }

    // Count vowels in a string
    public static int countVowels(String str) {
        int count = 0;
        str = str.toLowerCase();
        for (int i = 0; i < str.length(); i++) {
            char ch = str.charAt(i);
            if (ch == 'a' || ch == 'e' || ch == 'i' || ch == 'o' || ch == 'u') {
                count++;
            }
        }
        return count;
    }

    // Check if two strings are anagrams
    public static boolean areAnagrams(String str1, String str2) {
        if (str1.length() != str2.length()) return false;

        int[] charCount = new int[26];
        str1 = str1.toLowerCase();
        str2 = str2.toLowerCase();

        for (int i = 0; i < str1.length(); i++) {
            charCount[str1.charAt(i) - 'a']++;
            charCount[str2.charAt(i) - 'a']--;
        }

        for (int count : charCount) {
            if (count != 0) return false;
        }
        return true;
    }

    public static void main(String[] args) {
        String word = "Hello";
        System.out.println("Reversed: " + reverseString(word));
        System.out.println("Vowel count in '" + word + "': " + countVowels(word));

        String s1 = "listen";
        String s2 = "silent";
        System.out.println("'" + s1 + "' and '" + s2 + "' are anagrams: " + areAnagrams(s1, s2));
    }
}
