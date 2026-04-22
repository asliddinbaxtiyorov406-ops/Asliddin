import asyncio
import logging
import os
from contextlib import asynccontextmanager

from aiogram import Bot
from aiogram.types import Update
from fastapi import FastAPI, Header, HTTPException, Request, status

from main import BOT_TOKEN, dp, init_db, setup_bot_commands


logging.basicConfig(level=logging.INFO)

WEBHOOK_SECRET_TOKEN = (os.getenv("WEBHOOK_SECRET_TOKEN") or "").strip()
WEBHOOK_SETUP_TOKEN = (os.getenv("WEBHOOK_SETUP_TOKEN") or "").strip()
WEBHOOK_PATH = (os.getenv("WEBHOOK_PATH") or "/telegram/webhook").strip()
WEBHOOK_URL = (os.getenv("WEBHOOK_URL") or "").strip()

if not WEBHOOK_PATH.startswith("/"):
    WEBHOOK_PATH = f"/{WEBHOOK_PATH}"

WEBHOOK_PATH_ALIAS = None if WEBHOOK_PATH.startswith("/api/") else f"/api{WEBHOOK_PATH}"
SETUP_WEBHOOK_PATH = "/setup-webhook"
SETUP_WEBHOOK_PATH_ALIAS = "/api/setup-webhook"
HEALTHZ_PATH = "/healthz"
HEALTHZ_PATH_ALIAS = "/api/healthz"

bot = Bot(token=BOT_TOKEN)
init_lock = asyncio.Lock()
is_initialized = False


async def ensure_initialized() -> None:
    global is_initialized
    if is_initialized:
        return

    async with init_lock:
        if is_initialized:
            return
        init_db()
        await setup_bot_commands(bot)
        is_initialized = True
        logging.info("Webhook runtime ishga tushdi.")


def ensure_setup_access(x_setup_token: str | None) -> None:
    if not WEBHOOK_SETUP_TOKEN:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Setup endpoint o'chirilgan.")
    if x_setup_token != WEBHOOK_SETUP_TOKEN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Setup token noto'g'ri.")


def validate_secret_token(x_telegram_bot_api_secret_token: str | None) -> None:
    if WEBHOOK_SECRET_TOKEN and x_telegram_bot_api_secret_token != WEBHOOK_SECRET_TOKEN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Secret token noto'g'ri.")


def resolve_webhook_url(request: Request) -> str:
    if WEBHOOK_URL:
        return WEBHOOK_URL
    return str(request.url_for("telegram_webhook"))


@asynccontextmanager
async def lifespan(_: FastAPI):
    await ensure_initialized()
    try:
        yield
    finally:
        await bot.session.close()
        try:
            await dp.storage.close()
        except Exception as error:
            logging.warning("FSM storage yopishda xatolik: %s", error)


app = FastAPI(title="Murojat Bot Webhook", lifespan=lifespan)


@app.get("/")
async def root() -> dict[str, object]:
    return {"ok": True, "mode": "webhook"}


@app.get("/api")
async def root_api() -> dict[str, object]:
    return await root()


@app.get(HEALTHZ_PATH)
@app.get(HEALTHZ_PATH_ALIAS)
async def healthz() -> dict[str, object]:
    await ensure_initialized()
    return {"ok": True}


@app.post(WEBHOOK_PATH)
async def telegram_webhook(
    request: Request,
    x_telegram_bot_api_secret_token: str | None = Header(default=None),
) -> dict[str, object]:
    validate_secret_token(x_telegram_bot_api_secret_token)
    await ensure_initialized()

    try:
        payload = await request.json()
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Yaroqsiz JSON payload: {error}",
        ) from error

    if not isinstance(payload, dict):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payload JSON object bo'lishi kerak.",
        )

    update = Update.model_validate(payload, context={"bot": bot})
    await dp.feed_update(bot, update)
    return {"ok": True}


@app.post(SETUP_WEBHOOK_PATH)
@app.post(SETUP_WEBHOOK_PATH_ALIAS)
async def setup_webhook(
    request: Request,
    x_setup_token: str | None = Header(default=None),
) -> dict[str, object]:
    ensure_setup_access(x_setup_token)
    await ensure_initialized()

    webhook_url = resolve_webhook_url(request)
    await bot.set_webhook(
        url=webhook_url,
        secret_token=WEBHOOK_SECRET_TOKEN or None,
        allowed_updates=dp.resolve_used_update_types(),
        drop_pending_updates=False,
    )
    info = await bot.get_webhook_info()
    return {
        "ok": True,
        "webhook_url": webhook_url,
        "telegram_url": info.url,
        "pending_update_count": info.pending_update_count,
    }


@app.delete(SETUP_WEBHOOK_PATH)
@app.delete(SETUP_WEBHOOK_PATH_ALIAS)
async def delete_webhook(x_setup_token: str | None = Header(default=None)) -> dict[str, object]:
    ensure_setup_access(x_setup_token)
    await ensure_initialized()
    await bot.delete_webhook(drop_pending_updates=False)
    return {"ok": True}


if WEBHOOK_PATH_ALIAS:
    app.add_api_route(WEBHOOK_PATH_ALIAS, telegram_webhook, methods=["POST"])
