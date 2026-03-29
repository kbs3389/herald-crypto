"""
Herald Crypto Exchange - Main Entry Point

Starts the FastAPI server with all services initialized.
Usage: python main.py
"""
import uvicorn


def main():
    uvicorn.run(
        "src.services.gateway.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )


if __name__ == "__main__":
    main()
