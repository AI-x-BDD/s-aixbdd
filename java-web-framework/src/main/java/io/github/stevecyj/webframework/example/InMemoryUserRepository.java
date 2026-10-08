package io.github.stevecyj.webframework.example;

import java.util.Map;
import java.util.Optional;

/** Small repository used by the runnable dependency injection example. */
public final class InMemoryUserRepository implements UserRepository {
    private final Map<String, String> names = Map.of("42", "Ada");

    public InMemoryUserRepository() {
    }

    @Override
    public Optional<String> findName(String id) {
        return Optional.ofNullable(names.get(id));
    }
}
