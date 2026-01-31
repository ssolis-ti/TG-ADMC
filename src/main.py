import sys
import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from src.core.config import settings
from src.db.database import init_db
from src.bot.handlers import common, verification
from src.api import routes
from src.api.admin import admin_router

from loguru import logger
from src.core.logger import setup_logging
from starlette.middleware.base import BaseHTTPMiddleware
import time

# Logging Setup
setup_logging()

# Bot & Dispatcher Setup
bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Register Routers
dp.include_router(common.router)
dp.include_router(verification.router)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    [LIFESPAN]: El Ciclo de Vida del Organismo (Bot).
    Builds connections, starts the heart (scheduler), and hooks into the Matrix (Telegram).
    """
    # 1. [DB]: Conexión Sináptica con PostgreSQL
    await init_db()
    
    # 2. [HEARTBEAT]: Start Scheduler (El Reloj Biológico)
    # Controla tareas diferidas como "Check Scheduled Posts"
    from src.workers.scheduler import start_scheduler
    start_scheduler()
    
    # 3. [WEBHOOK]: Hook into the Matrix
    logger.info("Starting TG-ADMC Bot...")
    if settings.WEBHOOK_URL and "example.com" not in settings.WEBHOOK_URL:
        # [PROD MODE]: Usamos Webhook para alta concurrencia.
        # Evita "terminated by other getUpdates" conflict.
        webhook_url = f"{settings.WEBHOOK_URL}{settings.WEBHOOK_PATH}"
        logger.info(f"Setting webhook to: {webhook_url}")
        await bot.set_webhook(webhook_url)
    else:
        # [DEV MODE]: Polling para pruebas locales sin túnel.
        logger.info("Webhook URL not set. Polling mode recommended for local dev.")
    
    yield
    
    # [SHUTDOWN]: Hibernación Controlada
    logger.info("Shutting down...")
    await bot.delete_webhook()
    await bot.session.close()

app = FastAPI(lifespan=lifespan)

class RequestLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000
        
        # Colorized Status Code
        status_color = "<green>" if 200 <= response.status_code < 300 else "<red>"
        
        logger.info(
            f"HTTP {request.method} {request.url.path} | "
            f"{status_color}{response.status_code}</{status_color[1:]} | "
            f"{process_time:.2f}ms"
        )
        return response

app.add_middleware(RequestLogMiddleware)
app.include_router(routes.router)
app.include_router(admin_router)  # [DEMO] Admin endpoints

# Mount Static Files
os.makedirs("src/static", exist_ok=True) # Ensure dir exists
app.mount("/static", StaticFiles(directory="src/static"), name="static")

@app.get("/app")
async def serve_webapp():
    """
    Serves the Mini App Frontend.
    """
    return FileResponse("src/static/index.html")

@app.post(settings.WEBHOOK_PATH)
async def bot_webhook(update: dict):
    telegram_update = types.Update(**update)
    await dp.feed_update(bot, telegram_update)

@app.get("/")
async def root():
    """
    [UX]: Serve the Mini App immediately at root.
    """
    return FileResponse("src/static/index.html")

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "Telegram Ads Marketplace MVP"}
