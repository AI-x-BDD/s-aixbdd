package io.github.stevecyj.webframework.example;

import io.github.stevecyj.webframework.Handler;
import io.github.stevecyj.webframework.Logged;
import io.github.stevecyj.webframework.Request;
import io.github.stevecyj.webframework.Response;
import java.util.Objects;

/** Handles the example route using a service supplied by the container. */
@Logged
public final class UserController implements Handler {
    private final UserService service;

    public UserController(UserService service) {
        this.service = Objects.requireNonNull(service, "service");
    }

    @Override
    public Response handle(Request request) {
        String id = request.pathParameter("id").orElseThrow();
        return service.findName(id)
                .map(name -> Response.text(200, name))
                .orElseGet(() -> Response.text(404, "User Not Found"));
    }
}
