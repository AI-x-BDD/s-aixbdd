package io.github.stevecyj.webframework.example;

import io.github.stevecyj.webframework.WebApplication;

/** Starts a route whose controller, service, and repository are constructor-injected. */
public final class UserDirectoryExample {
    private UserDirectoryExample() {
    }

    public static void main(String[] args) {
        new WebApplication()
                .bind(UserRepository.class, InMemoryUserRepository.class)
                .route("GET", "/users/{id}", UserController.class)
                .start(8080);
        System.out.println("User directory listening on http://127.0.0.1:8080/users/42");
    }
}
