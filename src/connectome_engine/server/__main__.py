"""CLI entrypoint for running the Connectome Telemetry Engine server via `python -m connectome_engine.server`."""

import uvicorn


def main() -> None:
    uvicorn.run(
        "connectome_engine.server.app:app",
        host="127.0.0.1",
        port=8000,
        ws_ping_interval=30,
        ws_ping_timeout=60,
        access_log=True,
        log_level="info",
    )


if __name__ == "__main__":
    main()
