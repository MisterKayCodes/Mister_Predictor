from aiogram import BaseMiddleware
from aiogram.types import Message
from typing import Callable, Dict, Any, Awaitable
from config.settings import settings


class AdminCheckMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        if event.text and event.text.startswith("Admin:"):
            admin_ids = settings.admin_id_list
            if admin_ids and event.from_user.id not in admin_ids:
                await event.answer("You don't have admin access.")
                return
        return await handler(event, data)
