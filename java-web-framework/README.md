# Java Web Framework

A small synchronous HTTP framework for Java 17 or later. It uses the JDK `jdk.httpserver` module and has no runtime dependencies.

## Quick start

From the repository root, build the JAR and open JShell:

```sh
mvn -q -DskipTests -f java-web-framework/pom.xml package
jshell --class-path java-web-framework/target/java-web-framework-0.1.0.jar
```

At the `jshell>` prompt, enter:

```java
import io.github.stevecyj.webframework.*;
var app = new WebApplication();
app.route("GET", "/", request -> Response.text(200, "Hello, world!"));
app.start(8080);
```

In another terminal:

```sh
curl http://127.0.0.1:8080/
# Hello, world!
```

Stop the server in JShell with `app.stop();`, then enter `/exit`.

## Routes

```java
app.route("GET", "/hello/{name}", request ->
        Response.text(200, "Hello, " + request.pathParameter("name").orElseThrow()));
```

Register routes before calling `start`. Route patterns support literal segments and `{name}` parameters. More specific literal routes take precedence; ties use registration order. A missing path returns 404, a matching path with another method returns 405 with `Allow`, and an uncaught handler exception returns 500.

## Constructor injection

Register a controller class as a route, and the framework builds its constructor dependencies recursively. Concrete classes need no registration. Bind an interface or abstract class to a concrete implementation before registering a controller route:

```java
new WebApplication()
        .bind(UserRepository.class, InMemoryUserRepository.class)
        .route("GET", "/users/{id}", UserController.class)
        .start(8080);
```

Each constructed class must be public and have exactly one public constructor. One instance of each concrete class is shared within the application. Missing bindings, ambiguous constructors, and dependency cycles fail when the controller route is registered, before the server starts. Bindings cannot change after the first dependency resolution. Existing lambda and `Handler` instance routes remain available.

The included example shows `UserController` receiving `UserService`, which receives `UserRepository`:

```sh
mvn -q package
java -cp target/java-web-framework-0.1.0.jar io.github.stevecyj.webframework.example.UserDirectoryExample
```

In another terminal:

```sh
curl http://127.0.0.1:8080/users/42
# Ada
curl -i http://127.0.0.1:8080/users/missing
# HTTP/1.1 404 Not Found
```

## Request logging

Annotate a controller class with `@Logged` to log each request it receives and each response it returns:

```java
@Logged
public final class UserController implements Handler {
    // ...
}
```

The annotation works for class routes and `Handler` instance routes. Logs use `System.Logger`, named after the controller class, at `INFO`; a controller exception is logged at `WARNING` and still returns 500. Requests that never reach a controller, such as 404, 405, and malformed-query 400 responses, are not logged. Lambda routes cannot carry the annotation.

The example `UserController` is annotated, so the requests above print:

```text
INFO: --> GET /users/42
INFO: <-- 200 GET /users/42 (0 ms)
INFO: --> GET /users/missing
INFO: <-- 404 GET /users/missing (0 ms)
```

Run tests with `mvn test` from this directory.
