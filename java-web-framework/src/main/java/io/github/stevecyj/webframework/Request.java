package io.github.stevecyj.webframework;

import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.TreeMap;

/** An immutable HTTP request exposed to application handlers. */
public final class Request {
    private final String method;
    private final String path;
    private final Map<String, List<String>> queryParameters;
    private final Map<String, List<String>> headers;
    private final byte[] body;
    private final Map<String, String> pathParameters;

    public Request(
            String method,
            String path,
            Map<String, List<String>> queryParameters,
            Map<String, List<String>> headers,
            byte[] body) {
        this(method, path, queryParameters, headers, body, Map.of());
    }

    private Request(
            String method,
            String path,
            Map<String, List<String>> queryParameters,
            Map<String, List<String>> headers,
            byte[] body,
            Map<String, String> pathParameters) {
        this.method = Objects.requireNonNull(method, "method");
        this.path = Objects.requireNonNull(path, "path");
        this.queryParameters = copyValues(queryParameters, false);
        this.headers = copyValues(headers, true);
        this.body = Objects.requireNonNull(body, "body").clone();
        this.pathParameters = Collections.unmodifiableMap(new LinkedHashMap<>(pathParameters));
    }

    public String method() {
        return method;
    }

    public String path() {
        return path;
    }

    public Optional<String> pathParameter(String name) {
        return Optional.ofNullable(pathParameters.get(name));
    }

    public Optional<String> queryParameter(String name) {
        return firstValue(queryParameters.get(name));
    }

    public Optional<String> header(String name) {
        return firstValue(headers.get(name));
    }

    public byte[] body() {
        return body.clone();
    }

    public Request withPathParameters(Map<String, String> parameters) {
        return new Request(method, path, queryParameters, headers, body,
                Objects.requireNonNull(parameters, "parameters"));
    }

    private static Optional<String> firstValue(List<String> values) {
        return values == null || values.isEmpty() ? Optional.empty() : Optional.of(values.get(0));
    }

    private static Map<String, List<String>> copyValues(
            Map<String, List<String>> source, boolean caseInsensitive) {
        Objects.requireNonNull(source, "source");
        Map<String, List<String>> copy = caseInsensitive
                ? new TreeMap<>(String.CASE_INSENSITIVE_ORDER)
                : new LinkedHashMap<>();
        source.forEach((name, values) -> {
            Objects.requireNonNull(name, "name");
            copy.put(name, List.copyOf(Objects.requireNonNull(values, "values")));
        });
        return Collections.unmodifiableMap(copy);
    }
}
