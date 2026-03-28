import asyncio
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.exceptions import TelegramForbiddenError, TelegramRetryAfter
from services.user_service import UserService
from services.order_service import OrderService
from keyboards.reply import get_main_menu_keyboard, get_confirmation_keyboard
from data.config import CONFIG
from data.constants import AdminKeys
from sqlalchemy.ext.asyncio import AsyncSession
from utils.localization import I18N

router = Router()

class BroadcastState(StatesGroup):
    waiting_for_message = State()
    waiting_for_confirmation = State()

@router.message(F.from_user.id.in_(CONFIG.admin_ids), F.text.in_(I18N.get_all("admin_btn_stats")))
async def show_statistics(message: Message, session: AsyncSession, _):
    order_service = OrderService(session)
    users, orders, sales = await order_service.get_stats()
    await message.answer(_("admin_stats").format(
        users=users,
        orders=orders,
        sales=f"{sales:,}"
    ))

@router.message(F.from_user.id.in_(CONFIG.admin_ids), F.text.in_(I18N.get_all("admin_btn_broadcast")))
async def start_broadcast(message: Message, state: FSMContext, _):
    await state.set_state(BroadcastState.waiting_for_message)
    await message.answer(_("admin_broadcast_prompt"))

@router.message(BroadcastState.waiting_for_message)
async def preview_broadcast(message: Message, state: FSMContext, session: AsyncSession, _, lang):
    user_service = UserService(session)
    users = await user_service.get_all()
    
    await state.update_data(broadcast_message_id=message.message_id)
    await state.set_state(BroadcastState.waiting_for_confirmation)
    
    await message.answer(_("admin_broadcast_preview"))
    await message.send_copy(message.chat.id)
    await message.answer(
        _("admin_broadcast_confirm").format(total=len(users)),
        reply_markup=get_confirmation_keyboard(lang)
    )

@router.message(BroadcastState.waiting_for_confirmation, F.text.in_(I18N.get_all("admin_btn_no")))
async def cancel_broadcast(message: Message, state: FSMContext, _, lang):
    await state.clear()
    is_admin = message.from_user.id == CONFIG.ADMIN_ID
    await message.answer(_("admin_broadcast_cancelled"), reply_markup=get_main_menu_keyboard(lang, is_admin))

@router.message(BroadcastState.waiting_for_confirmation, F.text.in_(I18N.get_all("admin_btn_yes")))
async def perform_broadcast(message: Message, state: FSMContext, session: AsyncSession, _, lang):
    data = await state.get_data()
    msg_id = data.get("broadcast_message_id")
    user_service = UserService(session)
    users = await user_service.get_all()
    
    success_count = 0
    blocked_count = 0
    error_count = 0
    
    await message.answer(_("admin_broadcast_started").format(total=len(users)))
    
    for user in users:
        try:
            await message.bot.copy_message(
                chat_id=user.telegram_id,
                from_chat_id=message.chat.id,
                message_id=msg_id
            )
            success_count += 1
            await asyncio.sleep(0.05) # Basic rate limit
        except TelegramForbiddenError:
            blocked_count += 1
            await user_service.update_status(user.telegram_id, False)
        except TelegramRetryAfter as e:
            await asyncio.sleep(e.retry_after)
            # Retry once after sleep
            try:
                await message.bot.copy_message(user.telegram_id, message.chat.id, msg_id)
                success_count += 1
            except Exception:
                error_count += 1
        except Exception:
            error_count += 1
            
    is_admin = message.from_user.id == CONFIG.ADMIN_ID
    await message.answer(
        _("admin_broadcast_summary").format(
            total=len(users),
            success=success_count,
            blocked=blocked_count,
            error=error_count
        ),
        reply_markup=get_main_menu_keyboard(lang, is_admin)
    )
    await state.clear()
