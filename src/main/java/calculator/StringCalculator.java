package calculator;

public class StringCalculator {

    public int add(String numbers) {
        if (numbers.isEmpty()) {
            return 0;
        }
        String[] parts = numbers.split(",");
        if (parts.length == 1) {
            return Integer.parseInt(parts[0]);
        }
        return Integer.parseInt(parts[0]) + Integer.parseInt(parts[1]);
    }
}
