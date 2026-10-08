package io.github.stevecyj.webframework;

import java.util.Collections;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.Locale;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;

/** A single method and path pattern bound to an application handler. */
final class Route {
    private final String method;
    private final String pattern;
    private final String[] segments;
    private final Handler handler;
    private final int literalCount;

    Route(String method, String pattern, Handler handler) {
        Objects.requireNonNull(method, "method");
        if (!method.matches("[!#$%&'*+.^_`|~0-9A-Za-z-]+")) {
            throw new IllegalArgumentException("Invalid HTTP method: " + method);
        }
        this.method = method.toUpperCase(Locale.ROOT);
        this.pattern = Objects.requireNonNull(pattern, "pattern");
        if (!pattern.startsWith("/")) {
            throw new IllegalArgumentException("Route pattern must start with /");
        }
        this.handler = Objects.requireNonNull(handler, "handler");
        this.segments = pattern.split("/", -1);

        Set<String> parameters = new HashSet<>();
        int literals = 0;
        for (int index = 1; index < segments.length; index++) {
            String segment = segments[index];
            if (segment.startsWith("{") || segment.endsWith("}")) {
                if (!segment.matches("\\{[A-Za-z][A-Za-z0-9_]*}")) {
                    throw new IllegalArgumentException("Invalid path parameter: " + segment);
                }
                String name = segment.substring(1, segment.length() - 1);
                if (!parameters.add(name)) {
                    throw new IllegalArgumentException("Duplicate path parameter: " + name);
                }
            } else {
                literals++;
            }
        }
        this.literalCount = literals;
    }

    public String method() {
        return method;
    }

    String pattern() {
        return pattern;
    }

    int literalCount() {
        return literalCount;
    }

    public Optional<Map<String, String>> match(String path) {
        Objects.requireNonNull(path, "path");
        if (!path.startsWith("/")) {
            return Optional.empty();
        }
        String[] parts = path.split("/", -1);
        if (parts.length != segments.length) {
            return Optional.empty();
        }
        Map<String, String> parameters = new LinkedHashMap<>();
        for (int index = 1; index < segments.length; index++) {
            String segment = segments[index];
            String part = parts[index];
            if (segment.startsWith("{")) {
                if (part.isEmpty()) {
                    return Optional.empty();
                }
                parameters.put(segment.substring(1, segment.length() - 1), part);
            } else if (!segment.equals(part)) {
                return Optional.empty();
            }
        }
        return Optional.of(Collections.unmodifiableMap(parameters));
    }

    public Response handle(Request request) {
        return Objects.requireNonNull(handler.handle(request), "Handler returned null");
    }
}
