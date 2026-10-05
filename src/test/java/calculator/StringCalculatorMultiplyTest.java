package calculator;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.util.stream.Stream;

import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.MethodSource;

class StringCalculatorMultiplyTest {

    private final StringCalculator calculator = new StringCalculator();

    @ParameterizedTest
    @MethodSource("validInputs")
    void validInputReturnsProduct(String input, int expected) {
        assertEquals(expected, calculator.multiply(input));
    }

    static Stream<Arguments> validInputs() {
        return Stream.of(
                Arguments.of("", 0),
                Arguments.of("2", 2),
                Arguments.of("2,3", 6),
                Arguments.of("2,3,4", 24),
                Arguments.of("2\n3", 6),
                Arguments.of("2\n3,4", 24),
                Arguments.of("//;\n2;3", 6),
                Arguments.of("//|\n2|3|4", 24),
                Arguments.of("//;\n2;3,4\n5", 120),
                Arguments.of("//***\n2***3", 6),
                Arguments.of("0", 0),
                Arguments.of("2,0,3", 0));
    }

    @ParameterizedTest
    @MethodSource("invalidInputs")
    void invalidInputReportsAllRecognizableErrors(String input, String expected) {
        IllegalArgumentException exception = assertThrows(
                IllegalArgumentException.class, () -> calculator.multiply(input));
        assertEquals(expected, exception.getMessage());
    }

    static Stream<Arguments> invalidInputs() {
        String invalidHeader =
                "Invalid delimiter header: expected //delimiter followed by a newline";
        String trailingDelimiter = "Input must not end with a delimiter";
        return Stream.of(
                Arguments.of("//;", invalidHeader),
                Arguments.of("//;2;3", invalidHeader),
                Arguments.of("//", invalidHeader),
                Arguments.of("//\n2,3", invalidHeader),
                Arguments.of("//;\n", "Missing number at position 1"),
                Arguments.of("2,3,", trailingDelimiter),
                Arguments.of("2\n3\n", trailingDelimiter),
                Arguments.of("//;\n2;3;", trailingDelimiter),
                Arguments.of(",2", "Missing number at position 1"),
                Arguments.of("2,,3", "Missing number at position 2"),
                Arguments.of("2,x", "Invalid number at position 2: x"),
                Arguments.of("2147483648", "Invalid number at position 1: 2147483648"),
                Arguments.of("-1,2", "Negative not allowed: -1"),
                Arguments.of("-1,2,-3", "Negative not allowed: -1,-3"),
                Arguments.of("-3\n2,-1", "Negative not allowed: -3,-1"),
                Arguments.of("//|\n-1|2|-3", "Negative not allowed: -1,-3"),
                Arguments.of("-1,,2", "Missing number at position 2; Negative not allowed: -1"),
                Arguments.of("//;\n-1;;2", "Missing number at position 2; Negative not allowed: -1"),
                Arguments.of("//|\n-1||2", "Missing number at position 2; Negative not allowed: -1"),
                Arguments.of("-1\n\n2", "Missing number at position 2; Negative not allowed: -1"),
                Arguments.of("0,x,-3", "Invalid number at position 2: x; Negative not allowed: -3"),
                Arguments.of(",x,-1,,2147483648,-1,",
                        "Missing number at position 1; Invalid number at position 2: x; "
                                + "Missing number at position 4; Invalid number at position 5: 2147483648; "
                                + "Input must not end with a delimiter; Negative not allowed: -1,-1"));
    }
}
