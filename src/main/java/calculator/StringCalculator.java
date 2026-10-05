package calculator;

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
        for (String part : parts) {
            sum += Integer.parseInt(part);
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
