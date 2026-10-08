package io.github.stevecyj.webframework;

@FunctionalInterface
public interface Handler {
    Response handle(Request request);
}
