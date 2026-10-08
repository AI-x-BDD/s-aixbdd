package io.github.stevecyj.webframework;

import java.util.Objects;
import java.util.concurrent.TimeUnit;

/** Wraps a {@link Logged} controller and logs when a request arrives and when a response leaves. */
final class LoggingHandler implements Handler {
    private final Handler delegate;
    private final System.Logger logger;

    LoggingHandler(Handler delegate, System.Logger logger) {
        this.delegate = Objects.requireNonNull(delegate, "delegate");
        this.logger = Objects.requireNonNull(logger, "logger");
    }

    /** Wraps a handler whose class is annotated with {@link Logged}; returns other handlers unchanged. */
    static Handler decorate(Handler handler) {
        Objects.requireNonNull(handler, "handler");
        Class<?> type = handler.getClass();
        if (!type.isAnnotationPresent(Logged.class)) {
            return handler;
        }
        return new LoggingHandler(handler, System.getLogger(type.getName()));
    }

    @Override
    public Response handle(Request request) {
        String target = request.method() + " " + request.path();
        logger.log(System.Logger.Level.INFO, () -> "--> " + target);
        long started = System.nanoTime();
        Response response;
        try {
            response = Objects.requireNonNull(delegate.handle(request), "Handler returned null");
        } catch (RuntimeException | Error failure) {
            long elapsed = elapsedMillis(started);
            logger.log(System.Logger.Level.WARNING, () -> "<-- " + target + " failed after "
                    + elapsed + " ms: " + failure.getClass().getName());
            throw failure;
        }
        long elapsed = elapsedMillis(started);
        logger.log(System.Logger.Level.INFO, () -> "<-- " + response.status() + " " + target
                + " (" + elapsed + " ms)");
        return response;
    }

    private static long elapsedMillis(long started) {
        return TimeUnit.NANOSECONDS.toMillis(System.nanoTime() - started);
    }
}
