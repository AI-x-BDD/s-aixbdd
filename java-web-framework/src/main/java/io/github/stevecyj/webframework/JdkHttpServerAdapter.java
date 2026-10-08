package io.github.stevecyj.webframework;

import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpServer;
import java.io.IOException;
import java.io.UncheckedIOException;
import java.net.InetSocketAddress;
import java.net.URLDecoder;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;

/** Adapts the JDK HTTP server to the framework's request and response types. */
final class JdkHttpServerAdapter {
    private static final System.Logger LOGGER = System.getLogger(JdkHttpServerAdapter.class.getName());

    private final Router router;
    private HttpServer server;

    JdkHttpServerAdapter(Router router) {
        this.router = Objects.requireNonNull(router, "router");
    }

    public void start(int port) {
        if (server != null) {
            throw new IllegalStateException("Server is already running");
        }
        try {
            HttpServer created = HttpServer.create(new InetSocketAddress(port), 0);
            created.createContext("/", this::handle);
            created.start();
            server = created;
        } catch (IOException exception) {
            throw new UncheckedIOException("Cannot start HTTP server", exception);
        }
    }

    public void stop() {
        if (server != null) {
            server.stop(0);
            server = null;
        }
    }

    private void handle(HttpExchange exchange) throws IOException {
        try {
            Response response;
            try {
                response = process(exchange);
            } catch (Exception failure) {
                LOGGER.log(System.Logger.Level.ERROR, "Request handling failed", failure);
                response = Response.text(500, "Internal Server Error");
            }
            writeResponse(exchange, response);
        } finally {
            exchange.close();
        }
    }

    private Response process(HttpExchange exchange) throws IOException {
        Request request;
        try {
            request = new Request(
                    exchange.getRequestMethod(),
                    exchange.getRequestURI().getPath(),
                    parseQuery(exchange.getRequestURI().getRawQuery()),
                    exchange.getRequestHeaders(),
                    exchange.getRequestBody().readAllBytes());
        } catch (IllegalArgumentException malformedQuery) {
            return Response.text(400, "Bad Request");
        }
        return router.dispatch(request);
    }

    private static Map<String, List<String>> parseQuery(String rawQuery) {
        Map<String, List<String>> result = new LinkedHashMap<>();
        if (rawQuery == null || rawQuery.isEmpty()) {
            return result;
        }
        for (String part : rawQuery.split("&", -1)) {
            if (part.isEmpty()) {
                continue;
            }
            int equals = part.indexOf('=');
            String name = URLDecoder.decode(equals < 0 ? part : part.substring(0, equals),
                    StandardCharsets.UTF_8);
            String value = URLDecoder.decode(equals < 0 ? "" : part.substring(equals + 1),
                    StandardCharsets.UTF_8);
            result.computeIfAbsent(name, ignored -> new ArrayList<>()).add(value);
        }
        return result;
    }

    private static void writeResponse(HttpExchange exchange, Response response) throws IOException {
        response.headers().forEach((name, value) -> exchange.getResponseHeaders().set(name, value));
        byte[] body = response.body();
        int status = response.status();
        boolean hasBody = body.length > 0 && status != 204 && status != 304
                && !exchange.getRequestMethod().equalsIgnoreCase("HEAD");
        exchange.sendResponseHeaders(status, hasBody ? body.length : -1);
        if (hasBody) {
            exchange.getResponseBody().write(body);
        }
    }
}
