package calculator;

import java.util.StringJoiner;
import java.util.regex.Pattern;

public class StringCalculator {

    public int add(String numbers) {
        if (numbers.isEmpty()) {
            return 0;
        }
        String[] parts = tokenize(numbers);
        if (parts[parts.length - 1].isEmpty()) {
            throw new IllegalArgumentException("Input must not end with a delimiter");
        }
        int sum = 0;
        StringJoiner negatives = new StringJoiner(",");
        for (String part : parts) {
            int number = Integer.parseInt(part);
            if (number < 0) {
                negatives.add(Integer.toString(number));
            }
            sum += number;
        }
        if (negatives.length() > 0) {
            throw new IllegalArgumentException("Negative not allowed: " + negatives);
        }
        return sum;
    }

    private String[] tokenize(String numbers) {
        if (numbers.startsWith("//")) {
            int headerEnd = numbers.indexOf('\n');
            String delimiter = numbers.substring(2, headerEnd);
            return numbers.substring(headerEnd + 1).split("[,\n]|" + Pattern.quote(delimiter), -1);
        }
        return numbers.split("[,\n]", -1);
    }
}
