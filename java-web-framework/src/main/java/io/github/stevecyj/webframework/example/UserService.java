package io.github.stevecyj.webframework.example;

import java.util.Objects;
import java.util.Optional;

/** Queries users through the repository supplied by the container. */
public final class UserService {
    private final UserRepository repository;

    public UserService(UserRepository repository) {
        this.repository = Objects.requireNonNull(repository, "repository");
    }

    public Optional<String> findName(String id) {
        return repository.findName(id);
    }
}
