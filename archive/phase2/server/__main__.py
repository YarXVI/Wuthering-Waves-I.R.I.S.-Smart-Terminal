"""启动 FastAPI 服务器"""
import uvicorn
from server.config import config

if __name__ == "__main__":
    uvicorn.run("server.api:app", host=config.host, port=config.port, reload=False)
