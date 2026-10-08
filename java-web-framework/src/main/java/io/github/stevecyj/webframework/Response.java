package io.github.stevecyj.webframework;

import java.nio.charset.StandardCharsets;
import java.util.Collections;
import java.util.Map;
import java.util.Objects;
import java.util.TreeMap;

/** An immutable HTTP response returned by an application handler. */
public final class Response {
    private final int status;
    private final Map<String, String> headers;
    private final byte[] body;

    public Response(int status, Map<String, String> headers, byte[] body) {
        if (status < 100 || status > 599) {
            throw new IllegalArgumentException("HTTP status must be between 100 and 599");
        }
        this.status = status;
        Map<String, String> copy = new TreeMap<>(String.CASE_INSENSITIVE_ORDER);
        Objects.requireNonNull(headers, "headers").forEach((name, value) ->
                copy.put(Objects.requireNonNull(name, "header name"),
                        Objects.requireNonNull(value, "header value")));
        this.headers = Collections.unmodifiableMap(copy);
        this.body = Objects.requireNonNull(body, "body").clone();
    }

    public static Response text(int status, String body) {
        return new Response(status, Map.of("Content-Type", "text/plain; charset=utf-8"),
                Objects.requireNonNull(body, "body").getBytes(StandardCharsets.UTF_8));
    }

    public Response withHeader(String name, String value) {
        Map<String, String> updated = new TreeMap<>(String.CASE_INSENSITIVE_ORDER);
        updated.putAll(headers);
        updated.put(Objects.requireNonNull(name, "name"), Objects.requireNonNull(value, "value"));
        return new Response(status, updated, body);
    }

    public int status() {
        return status;
    }

    public Map<String, String> headers() {
        return headers;
    }

    public byte[] body() {
        return body.clone();
    }
}
