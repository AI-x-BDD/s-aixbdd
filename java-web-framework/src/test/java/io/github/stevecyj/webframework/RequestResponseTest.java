package io.github.stevecyj.webframework;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.Test;

class RequestResponseTest {
    @Test
    void requestAndResponseKeepIndependentCopies() {
        byte[] requestBody = {1, 2};
        List<String> values = new ArrayList<>(List.of("first"));
        Map<String, List<String>> query = new LinkedHashMap<>();
        query.put("tag", values);
        Request request = new Request("GET", "/", query,
                Map.of("X-Test", List.of("yes")), requestBody);

        requestBody[0] = 9;
        values.set(0, "changed");
        request.body()[1] = 9;
        assertArrayEquals(new byte[] {1, 2}, request.body());
        assertEquals("first", request.queryParameter("tag").orElseThrow());
        assertEquals("yes", request.header("x-test").orElseThrow());
        assertTrue(request.pathParameter("id").isEmpty());
        assertEquals("42", request.withPathParameters(Map.of("id", "42"))
                .pathParameter("id").orElseThrow());
        assertTrue(request.pathParameter("id").isEmpty());

        byte[] responseBody = {3, 4};
        Response response = new Response(200, Map.of("X-Test", "yes"), responseBody)
                .withHeader("x-test", "updated");
        responseBody[0] = 9;
        response.body()[1] = 9;
        assertArrayEquals(new byte[] {3, 4}, response.body());
        assertEquals("updated", response.headers().get("X-Test"));
    }
}
