package io.github.stevecyj.webframework.example;

import java.util.Optional;

/** Looks up a user's name by ID. */
public interface UserRepository {
    Optional<String> findName(String id);
}
