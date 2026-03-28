from aiogram import Router, F
from aiogram.types import Message
from data.config import CONFIG

router = Router()

@router.message(F.from_user.id.in_(CONFIG.admin_ids), F.photo)
async def get_photo_id(message: Message):
    file_id = message.photo[-1].file_id
    await message.answer(f"Ushbu rasmning `file_id` si:\n\n`{file_id}`", parse_mode="MarkdownV2")
