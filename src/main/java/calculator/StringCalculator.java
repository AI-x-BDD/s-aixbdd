package calculator;

public class StringCalculator {

    public int add(String numbers) {
        if (numbers.isEmpty()) {
            return 0;
        }
        String[] parts = numbers.split("[,\n]", -1);
        if (parts[parts.length - 1].isEmpty()) {
            throw new IllegalArgumentException("Input must not end with a delimiter");
        }
        int sum = 0;
        for (String part : parts) {
            sum += Integer.parseInt(part);
        }
        return sum;
    }
}
