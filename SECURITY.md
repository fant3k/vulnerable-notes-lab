# Security policy

This repository contains intentionally vulnerable software.

Run it only on a local machine or an isolated training environment. Do not bind
the application to a public interface and do not deploy it to an internet-facing
host. Docker Compose is configured to publish the lab on `127.0.0.1` only.

If you find an undocumented vulnerability, a scenario that does not reproduce,
or a way to escape the documented lab boundaries, open an issue without
including real secrets or third-party data.

