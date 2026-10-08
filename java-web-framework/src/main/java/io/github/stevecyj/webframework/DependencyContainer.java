package io.github.stevecyj.webframework;

import java.lang.reflect.Constructor;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Modifier;
import java.util.ArrayDeque;
import java.util.Deque;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.stream.Collectors;

/** Builds one instance of each concrete type by recursively resolving constructor parameters. */
public final class DependencyContainer {
    private final Map<Class<?>, Class<?>> bindings = new HashMap<>();
    private final Map<Class<?>, Object> instances = new HashMap<>();
    private boolean resolutionStarted;

    /** Selects an implementation for an interface or abstract dependency before resolution starts. */
    public synchronized <T> void bind(Class<T> abstraction, Class<? extends T> implementation) {
        Objects.requireNonNull(abstraction, "abstraction");
        Objects.requireNonNull(implementation, "implementation");
        if (resolutionStarted) {
            throw new IllegalStateException("Cannot bind after dependency resolution has started");
        }
        if (!abstraction.isAssignableFrom(implementation)
                || implementation.isInterface()
                || Modifier.isAbstract(implementation.getModifiers())) {
            throw new IllegalArgumentException("Implementation must be a concrete subtype of "
                    + abstraction.getName());
        }
        if (bindings.putIfAbsent(abstraction, implementation) != null) {
            throw new IllegalArgumentException("Duplicate binding for " + abstraction.getName());
        }
    }

    /** Resolves a type, constructing its complete dependency graph on the first call. */
    public synchronized <T> T resolve(Class<T> type) {
        Objects.requireNonNull(type, "type");
        resolutionStarted = true;
        return type.cast(resolveType(type, new ArrayDeque<>(), new HashSet<>()));
    }

    private Object resolveType(Class<?> type, Deque<Class<?>> path, Set<Class<?>> constructing) {
        path.addLast(type);
        try {
            Class<?> implementation = bindings.getOrDefault(type, type);
            Object existing = instances.get(implementation);
            if (existing != null) {
                return existing;
            }
            if (implementation.isInterface() || Modifier.isAbstract(implementation.getModifiers())) {
                throw failure("No concrete binding for " + type.getName(), path, null);
            }
            if (!Modifier.isPublic(implementation.getModifiers())) {
                throw failure("Implementation must be public: " + implementation.getName(), path, null);
            }
            if (!constructing.add(implementation)) {
                throw failure("Circular dependency", path, null);
            }
            try {
                Constructor<?>[] constructors = implementation.getConstructors();
                if (constructors.length != 1) {
                    throw failure("Expected exactly one public constructor for "
                            + implementation.getName(), path, null);
                }
                Constructor<?> constructor = constructors[0];
                Class<?>[] parameterTypes = constructor.getParameterTypes();
                Object[] arguments = new Object[parameterTypes.length];
                for (int index = 0; index < parameterTypes.length; index++) {
                    arguments[index] = resolveType(parameterTypes[index], path, constructing);
                }
                Object created;
                try {
                    created = constructor.newInstance(arguments);
                } catch (InvocationTargetException exception) {
                    throw failure("Constructor failed for " + implementation.getName(),
                            path, exception.getCause());
                } catch (ReflectiveOperationException exception) {
                    throw failure("Cannot construct " + implementation.getName(), path, exception);
                }
                instances.put(implementation, created);
                return created;
            } finally {
                constructing.remove(implementation);
            }
        } finally {
            path.removeLast();
        }
    }

    private static IllegalStateException failure(String reason, Deque<Class<?>> path, Throwable cause) {
        String chain = path.stream().map(Class::getName).collect(Collectors.joining(" -> "));
        return new IllegalStateException(reason + " (dependency path: " + chain + ")", cause);
    }
}
