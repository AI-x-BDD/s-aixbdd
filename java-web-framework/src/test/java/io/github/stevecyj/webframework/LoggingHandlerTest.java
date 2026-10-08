package io.github.stevecyj.webframework;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.text.MessageFormat;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.ResourceBundle;
import org.junit.jupiter.api.Test;

class LoggingHandlerTest {
    private static final Request REQUEST = new Request("GET", "/users/42", Map.of(), Map.of(), new byte[0]);

    @Test
    void decoratesOnlyHandlersAnnotatedWithLogged() {
        Handler lambda = request -> Response.text(200, "ok");
        Handler plain = new PlainController();

        assertSame(lambda, LoggingHandler.decorate(lambda));
        assertSame(plain, LoggingHandler.decorate(plain));
        assertInstanceOf(LoggingHandler.class, LoggingHandler.decorate(new LoggedController()));
    }

    @Test
    void logsRequestBeforeAndResponseAfterTheController() {
        CapturingLogger logger = new CapturingLogger();
        List<String> order = new ArrayList<>();
        Handler handler = new LoggingHandler(request -> {
            order.add("controller after " + logger.entries.size() + " log entries");
            return Response.text(201, "created");
        }, logger);

        Response response = handler.handle(REQUEST);

        assertEquals(201, response.status());
        assertEquals(List.of("controller after 1 log entries"), order);
        assertEquals(2, logger.entries.size());
        assertEquals("INFO --> GET /users/42", logger.entries.get(0));
        assertTrue(logger.entries.get(1).matches("INFO <-- 201 GET /users/42 \\(\\d+ ms\\)"),
                logger.entries.get(1));
    }

    @Test
    void logsFailureAndRethrowsControllerException() {
        CapturingLogger logger = new CapturingLogger();
        IllegalStateException thrown = new IllegalStateException("boom");
        Handler handler = new LoggingHandler(request -> {
            throw thrown;
        }, logger);

        assertSame(thrown, assertThrows(IllegalStateException.class, () -> handler.handle(REQUEST)));
        assertEquals(2, logger.entries.size());
        assertTrue(logger.entries.get(1).matches(
                "WARNING <-- GET /users/42 failed after \\d+ ms: java.lang.IllegalStateException"),
                logger.entries.get(1));
    }

    @Logged
    private static final class LoggedController implements Handler {
        @Override
        public Response handle(Request request) {
            return Response.text(200, "logged");
        }
    }

    private static final class PlainController implements Handler {
        @Override
        public Response handle(Request request) {
            return Response.text(200, "plain");
        }
    }

    private static final class CapturingLogger implements System.Logger {
        private final List<String> entries = new ArrayList<>();

        @Override
        public String getName() {
            return "test";
        }

        @Override
        public boolean isLoggable(Level level) {
            return true;
        }

        @Override
        public void log(Level level, ResourceBundle bundle, String message, Throwable thrown) {
            entries.add(level + " " + message);
        }

        @Override
        public void log(Level level, ResourceBundle bundle, String format, Object... params) {
            entries.add(level + " " + (params == null ? format : MessageFormat.format(format, params)));
        }
    }
}
