package calculator;

import java.util.StringJoiner;
import java.util.regex.Pattern;

public class StringCalculator {

    public int add(String numbers) {
        if (numbers.isEmpty()) {
            return 0;
        }
        String[] parts = tokenize(numbers);
        int[] values = parseAndValidate(parts);
        int sum = 0;
        for (int value : values) {
            sum += value;
        }
        return sum;
    }

    private int[] parseAndValidate(String[] parts) {
        int[] values = new int[parts.length];
        StringJoiner errors = new StringJoiner("; ");
        StringJoiner negatives = new StringJoiner(",");
        for (int i = 0; i < parts.length; i++) {
            if (parts[i].isEmpty()) {
                errors.add(i == parts.length - 1 && parts.length > 1
                        ? "Input must not end with a delimiter"
                        : "Missing number at position " + (i + 1));
                continue;
            }
            int number;
            try {
                number = Integer.parseInt(parts[i]);
            } catch (NumberFormatException exception) {
                errors.add("Invalid number at position " + (i + 1) + ": " + parts[i]);
                continue;
            }
            values[i] = number;
            if (number < 0) {
                negatives.add(Integer.toString(number));
            }
        }
        if (negatives.length() > 0) {
            errors.add("Negative not allowed: " + negatives);
        }
        if (errors.length() > 0) {
            throw new IllegalArgumentException(errors.toString());
        }
        return values;
    }

    private String[] tokenize(String numbers) {
        if (numbers.startsWith("//")) {
            int headerEnd = numbers.indexOf('\n');
            if (headerEnd <= 2) {
                throw new IllegalArgumentException(
                        "Invalid delimiter header: expected //delimiter followed by a newline");
            }
            String delimiter = numbers.substring(2, headerEnd);
            return numbers.substring(headerEnd + 1).split("[,\n]|" + Pattern.quote(delimiter), -1);
        }
        return numbers.split("[,\n]", -1);
    }
}
