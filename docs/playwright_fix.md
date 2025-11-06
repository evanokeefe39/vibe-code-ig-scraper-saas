You’re experiencing a common issue: you have a Django app running inside a Docker container, and you’re trying to test it using Playwright via the Playwright MCP Server toolkit (via something like Claude Code or a similar MCP-client setup), but the Playwright/MCP process cannot reach `localhost` to access the Django site. Let’s unpack common causes **and** possible fixes (since your goal is automation + agentic workflows, you’ll likely want a robust solution). Based on your instructions: I’ll question assumptions and dig in.

---

## ✅ Checking assumptions

* You said “Playwright MPC (MCP) can’t connect to localhost” — I’ll assume the Django app is exposed at something like `http://localhost:8000` on your host, or perhaps at `http://localhost:<port>` via Docker port mapping.
* You’re running the Playwright/MCP server either on the host or in a container. You likely run the test client (MCP client) which triggers Playwright to navigate to the URL.
* The “can’t connect” error is likely “net::ERR_CONNECTION_REFUSED” or “page.goto failed”.

These assumptions match many Docker + Playwright issues. See this example:

> “_Error: net::ERR_CONNECTION_REFUSED at [http://app/_”](http://app/_”) (StackOverflow) ([Stack Overflow][1])
> And the Playwright Docker docs mention remote connection and `--host 0.0.0.0`. ([Playwright][2])

So your statement seems plausible.

---

## 🚧 Why this happens

There are a few common causes when “localhost” isn’t accessible from within a container or a separate network context:

1. **“localhost” inside container ≠ host machine**
   If Playwright (or your test code / MCP server) is inside a Docker container, `localhost` refers to the container itself, not the host machine. If your Django app is in another container (or on host), then `localhost` will fail.

2. **Networking / Docker port mapping / host‐gateway issues**
   If you mapped e.g. host port 8000 to container port 8000 for Django, but Playwright container isn’t using the host’s network or doesn’t know how to reach the host. Some options: use `host.docker.internal` (on Docker Desktop), or `--network host` (on Linux), or use `host-gateway` alias.

   Example from GitHub issue: when Playwright container tried to reach `http://localhost:3100/`, it failed, because the service was not visible. ([GitHub][3])

3. **Django only listening on 127.0.0.1 inside container**
   If the Django app is inside Docker and bound only to `127.0.0.1`, it might not be reachable from outside. You need to bind to `0.0.0.0`.

4. **MCP server and client config mismatch**
   If you are using MCP (Model Context Protocol) server such as `@playwright/mcp`, you might need to run the server with `--host 0.0.0.0` and expose the port so the client can reach it. See the docs. ([Playwright][2])

5. **Docker networks / same network / service discovery**
   If you run multiple containers (Django app + Playwright/MCP), you might want them on the *same Docker network* so that one container can refer to the other via service name. See MCP server docs: from other containers, use `playwright‐sse-mcp-server:${PORT}/sse`. ([Glama – MCP Hosting Platform][4])

---

## 🛠 How to fix / ensure connectivity

Given your scenario (Django in container + Playwright/MCP tool), here’s a recommended checklist and some strategies:

### Checklist

* Ensure Django is bound to `0.0.0.0` (not just `127.0.0.1`) inside its container so external hosts can reach it.
* Ensure Docker has port mapping from host → container (if relevant). Example: `docker run -p 8000:8000 mydjangoapp` or in `docker-compose.yml`.
* Determine where Playwright/MCP server is running: on host, or in a container.

  * If it's **on host**, then Django port mapping should allow `http://localhost:8000` to work.
  * If Playwright/MCP is in a **container**, then “localhost” inside that container refers to that container, not Django host. You either:

    * Use `host.docker.internal` (on Docker Desktop) or the host gateway address.
    * Use a Docker network and refer to Django container by its service name (e.g., `http://django-app:8000`).
    * Use `network_mode: host` (Linux only) to share host network.
* If using `@playwright/mcp` server in Docker, ensure you started it with `--host 0.0.0.0` so it listens on external interface and port mapping is correct. ([Playwright][2])
* In your MCP client (Claude Code), ensure the MCP server URL is correct (e.g., `http://localhost:3002/sse` or `http://playwright-sse-mcp-server:3002/sse`). ([Playbooks][5])

### Example configurations

Here are two scenarios:

**Scenario A – Playwright/MCP runs on host**

* Django container: `docker run -p 8000:8000 --name django-app mydjango:latest`. Django bound to `0.0.0.0:8000`.
* On host: Run MCP server: `npx @playwright/mcp --port 3002 --host 0.0.0.0` (or via Docker container but with port mapping).
* In your test code (or MCP client) you navigate to `http://localhost:8000`.

**Scenario B – Everything runs in Docker multi‐container setup (docker-compose)**

```yaml
version: '3'
services:
  django-app:
    image: mydjango:latest
    ports:
      - "8000:8000"
    command: python manage.py runserver 0.0.0.0:8000

  playwright-mcp:
    image: mcr.microsoft.com/playwright:v1.56.1-noble
    command: npx @playwright/mcp --port 3002 --host 0.0.0.0
    ports:
      - "3002:3002"
    networks:
      - testnet

networks:
  testnet:
    driver: bridge
```

* Tests (MCP client) run in host or another container, but if inside container, must refer to `http://django-app:8000`.
* MCP server URL in the client config: `http://localhost:3002/sse` (if host) or `http://playwright-mcp:3002/sse` (if container).

### Troubleshooting tips

* Try `curl http://localhost:8000` on the host machine to ensure the Django site is up.
* From inside the Playwright/MCP container (if applicable) run `curl http://django-app:8000` (or `http://host.docker.internal:8000`) to check connectivity.
* Check container logs for binding errors.
* For Playwright in Docker, docs warn about sandbox and memory issues: use `--ipc=host` when necessary. ([Playwright][2])
* If Playwright says “net::ERR_CONNECTION_REFUSED at [http://localhost:…”](http://localhost:…”) it means DNS/resolution ok but port unreachable. StackOverflow example: container “app” unreachable from test container. ([Stack Overflow][1])

---

## 🔍 Specific to MCP + Django in your setup

Since you’re using MCP for automation (via Claude Code) and a Django app in Docker, you’ll want a workflow like:

* Start Django container, bind to `0.0.0.0:8000`.
* Start MCP server (Playwright) either in host or its own container, listening on port (say 3002).
* Configure your MCP client (Claude Code) to point to the MCP server.
* In your test instructions (via the MCP client), navigate to the Django site URL (which must be reachable from the browser context that Playwright launches).
* Ensure the browser that Playwright opens is network-capable of reaching the Django service. If the browser is inside a container, use container hostname or host gateway. If browser runs on host, `localhost` works.

One subtlety: The browser launched by Playwright might run **inside** the same container (if MCP server container includes browser). That means that `localhost` inside that container is the container. If your Django container is separate, you must:

* Use `http://django-app:8000` (service name) **and** set `--host 0.0.0.0` and container network as shared or defined.
* Or run the Django service on host (not container) and from container use `host.docker.internal:8000`.

---

If you like, I can look up **exact example configuration** that others used with Playwright MCP + Django + Docker (including `docker-compose`) and tailor it to your lab setup (home lab + container). Would that be helpful for you?

[1]: https://stackoverflow.com/questions/69542361/playwright-error-connection-refused-in-docker?utm_source=chatgpt.com "Playwright error connection refused in docker - Stack Overflow"
[2]: https://playwright.dev/docs/docker?utm_source=chatgpt.com "Docker - Playwright"
[3]: https://github.com/microsoft/playwright/issues/31440?utm_source=chatgpt.com "Run Playwright server for component tests in docker #31440 - GitHub"
[4]: https://glama.ai/mcp/servers/%40torohash/playwright-sse-mcp-server?utm_source=chatgpt.com "Playwright SSE MCP Server - Glama"
[5]: https://playbooks.com/mcp/playwright-browser-automation?utm_source=chatgpt.com "Playwright Browser Automation MCP server for AI agents - Playbooks"
