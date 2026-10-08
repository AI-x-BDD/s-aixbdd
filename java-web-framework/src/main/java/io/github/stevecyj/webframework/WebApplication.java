package io.github.stevecyj.webframework;

/** Entry point for registering routes and running the HTTP server. */
public final class WebApplication {
    private final Router router = new Router();
    private final DependencyContainer container = new DependencyContainer();
    private JdkHttpServerAdapter adapter;

    /** Binds an abstraction before any class-based route resolves dependencies. */
    public synchronized <T> WebApplication bind(
            Class<T> abstraction, Class<? extends T> implementation) {
        if (adapter != null) {
            throw new IllegalStateException("Cannot bind dependencies while the server is running");
        }
        container.bind(abstraction, implementation);
        return this;
    }

    /** Registers a handler, adding request and response logging when its class is {@link Logged}. */
    public synchronized WebApplication route(String method, String pattern, Handler handler) {
        if (adapter != null) {
            throw new IllegalStateException("Cannot register routes while the server is running");
        }
        router.register(method, pattern, LoggingHandler.decorate(handler));
        return this;
    }

    /** Resolves a controller and its dependencies, then registers it like a handler instance. */
    public synchronized WebApplication route(
            String method, String pattern, Class<? extends Handler> handlerType) {
        if (adapter != null) {
            throw new IllegalStateException("Cannot register routes while the server is running");
        }
        router.register(method, pattern, LoggingHandler.decorate(container.resolve(handlerType)));
        return this;
    }

    public synchronized void start(int port) {
        if (adapter != null) {
            throw new IllegalStateException("Server is already running");
        }
        JdkHttpServerAdapter created = new JdkHttpServerAdapter(router);
        created.start(port);
        adapter = created;
    }

    public synchronized void stop() {
        if (adapter != null) {
            adapter.stop();
            adapter = null;
        }
    }
}
