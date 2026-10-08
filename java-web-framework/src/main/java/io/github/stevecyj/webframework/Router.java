package io.github.stevecyj.webframework;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.TreeSet;

/** Owns route registrations and selects a handler for each request. */
final class Router {
    private final List<Route> routes = new ArrayList<>();

    public void register(String method, String pattern, Handler handler) {
        Route route = new Route(method, pattern, handler);
        for (Route existing : routes) {
            if (existing.method().equals(route.method()) && existing.pattern().equals(route.pattern())) {
                throw new IllegalArgumentException("Duplicate route: " + route.method() + " " + route.pattern());
            }
        }
        routes.add(route);
    }

    public Response dispatch(Request request) {
        Objects.requireNonNull(request, "request");
        Route selected = null;
        Map<String, String> selectedParameters = Map.of();
        Set<String> allowedMethods = new TreeSet<>();

        for (Route route : routes) {
            var match = route.match(request.path());
            if (match.isEmpty()) {
                continue;
            }
            allowedMethods.add(route.method());
            if (route.method().equalsIgnoreCase(request.method())
                    && (selected == null || route.literalCount() > selected.literalCount())) {
                selected = route;
                selectedParameters = match.get();
            }
        }

        if (selected != null) {
            return selected.handle(request.withPathParameters(selectedParameters));
        }
        if (!allowedMethods.isEmpty()) {
            return Response.text(405, "Method Not Allowed")
                    .withHeader("Allow", String.join(", ", allowedMethods));
        }
        return Response.text(404, "Not Found");
    }
}
