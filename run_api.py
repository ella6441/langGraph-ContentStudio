"""API Server entry point"""
import uvicorn
from src.backend.app import create_app
from configs.config import config

if __name__ == "__main__":
    app = create_app()
    
    print(f"""
    NotebookLM Studio API Server
    ===============================
    
    Starting server on {config.API_HOST}:{config.API_PORT}
    Debug mode: {config.DEBUG}
    
    API Documentation:
    - Swagger UI: http://{config.API_HOST}:{config.API_PORT}/docs
    - ReDoc: http://{config.API_HOST}:{config.API_PORT}/redoc
    
    """)
    
    uvicorn.run(
        app,
        host=config.API_HOST,
        port=config.API_PORT,
        reload=config.DEBUG,
        log_level="info"
    )
