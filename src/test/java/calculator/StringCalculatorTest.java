package calculator;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import org.junit.jupiter.api.Test;

class StringCalculatorTest {

    private final StringCalculator calculator = new StringCalculator();

    @Test
    void singleNegativeNumberIsRejected() {
        IllegalArgumentException exception =
                assertThrows(IllegalArgumentException.class, () -> calculator.add("-1,2"));
        assertEquals("Negative not allowed: -1", exception.getMessage());
    }

    @Test
    void allNegativeNumbersAreReportedInInputOrder() {
        IllegalArgumentException exception =
                assertThrows(IllegalArgumentException.class, () -> calculator.add("-1,2,-3"));
        assertEquals("Negative not allowed: -1,-3", exception.getMessage());
    }

    @Test
    void negativeNumbersWithNewlineSeparatorsAreRejected() {
        IllegalArgumentException exception =
                assertThrows(IllegalArgumentException.class, () -> calculator.add("-3\n2,-1"));
        assertEquals("Negative not allowed: -3,-1", exception.getMessage());
    }

    @Test
    void negativeNumbersWithCustomDelimiterAreRejected() {
        IllegalArgumentException exception =
                assertThrows(IllegalArgumentException.class, () -> calculator.add("//|\n-1|2|-3"));
        assertEquals("Negative not allowed: -1,-3", exception.getMessage());
    }

    @Test
    void zeroIsAllowed() {
        assertEquals(2, calculator.add("0,2"));
    }

    @Test
    void emptyStringReturnsZero() {
        assertEquals(0, calculator.add(""));
    }

    @Test
    void singleNumberReturnsItself() {
        assertEquals(1, calculator.add("1"));
    }

    @Test
    void twoCommaSeparatedNumbersReturnTheirSum() {
        assertEquals(3, calculator.add("1,2"));
    }

    @Test
    void threeCommaSeparatedNumbersReturnTheirSum() {
        assertEquals(6, calculator.add("1,2,3"));
    }

    @Test
    void fiveCommaSeparatedNumbersReturnTheirSum() {
        assertEquals(15, calculator.add("1,2,3,4,5"));
    }

    @Test
    void newlineAndCommaCanBeMixedAsSeparators() {
        assertEquals(6, calculator.add("1\n2,3"));
    }

    @Test
    void newlineAloneCanSeparateNumbers() {
        assertEquals(6, calculator.add("1\n2\n3"));
    }

    @Test
    void trailingCommaIsRejected() {
        IllegalArgumentException exception =
                assertThrows(IllegalArgumentException.class, () -> calculator.add("1,2,"));
        assertEquals("Input must not end with a delimiter", exception.getMessage());
    }

    @Test
    void trailingNewlineIsRejected() {
        IllegalArgumentException exception =
                assertThrows(IllegalArgumentException.class, () -> calculator.add("1\n2\n"));
        assertEquals("Input must not end with a delimiter", exception.getMessage());
    }

    @Test
    void customDelimiterSeparatesNumbers() {
        assertEquals(3, calculator.add("//;\n1;2"));
    }

    @Test
    void regexSpecialCharacterCanBeCustomDelimiter() {
        assertEquals(6, calculator.add("//|\n1|2|3"));
    }

    @Test
    void trailingCustomDelimiterIsRejected() {
        IllegalArgumentException exception =
                assertThrows(IllegalArgumentException.class, () -> calculator.add("//;\n1;2;"));
        assertEquals("Input must not end with a delimiter", exception.getMessage());
    }
}
