package calculator;

import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.api.Test;

class StringCalculatorTest {

    private final StringCalculator calculator = new StringCalculator();

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
}
