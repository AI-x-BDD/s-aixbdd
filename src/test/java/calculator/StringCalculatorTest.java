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
}
