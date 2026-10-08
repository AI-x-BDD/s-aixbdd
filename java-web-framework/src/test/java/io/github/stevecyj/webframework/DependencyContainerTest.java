package io.github.stevecyj.webframework;

import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import io.github.stevecyj.webframework.example.InMemoryUserRepository;
import io.github.stevecyj.webframework.example.UserController;
import io.github.stevecyj.webframework.example.UserRepository;
import io.github.stevecyj.webframework.example.UserService;
import org.junit.jupiter.api.Test;

class DependencyContainerTest {
    @Test
    void resolvesDependencyChainAndSharesConcreteInstances() {
        DependencyContainer container = new DependencyContainer();
        container.bind(UserRepository.class, InMemoryUserRepository.class);

        assertSame(container.resolve(UserController.class), container.resolve(UserController.class));
        assertSame(container.resolve(UserService.class), container.resolve(UserService.class));
        assertSame(container.resolve(UserRepository.class),
                container.resolve(InMemoryUserRepository.class));
    }

    @Test
    void reportsTheFullPathToAnUnboundInterface() {
        DependencyContainer container = new DependencyContainer();

        IllegalStateException failure = assertThrows(IllegalStateException.class,
                () -> container.resolve(UserController.class));

        assertTrue(failure.getMessage().contains("UserController"));
        assertTrue(failure.getMessage().contains("UserService"));
        assertTrue(failure.getMessage().contains("UserRepository"));
    }

    @Test
    void rejectsAmbiguousConstructorsAndCircularDependencies() {
        DependencyContainer container = new DependencyContainer();

        IllegalStateException ambiguous = assertThrows(IllegalStateException.class,
                () -> container.resolve(Ambiguous.class));
        assertTrue(ambiguous.getMessage().contains("exactly one public constructor"));

        IllegalStateException cycle = assertThrows(IllegalStateException.class,
                () -> container.resolve(CircularFirst.class));
        assertTrue(cycle.getMessage().contains("Circular dependency"));
        assertTrue(cycle.getMessage().contains("CircularFirst"));
        assertTrue(cycle.getMessage().contains("CircularSecond"));
    }

    @Test
    void rejectsBindingsAfterResolutionBegins() {
        DependencyContainer container = new DependencyContainer();
        container.resolve(InMemoryUserRepository.class);

        assertThrows(IllegalStateException.class,
                () -> container.bind(UserRepository.class, InMemoryUserRepository.class));
    }

    public static final class Ambiguous {
        public Ambiguous() {
        }

        public Ambiguous(String value) {
        }
    }

    public static final class CircularFirst {
        public CircularFirst(CircularSecond second) {
        }
    }

    public static final class CircularSecond {
        public CircularSecond(CircularFirst first) {
        }
    }
}
