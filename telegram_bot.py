#!/usr/bin/env python3
"""
Bot Telegram untuk kontrol pipeline Moovon Finance dari luar sesi Claude Code.

Command yang didukung:
  /status                  -> cek fase, topik, blocked, antrian
  /help                    -> daftar command
  "Data aman, lanjut render" -> jalankan step1+step2 dari produce_script yang
                                 tercatat di state.json (approval gate SOP)
  "mulai topik: <nama>"    -> catat topik baru ke antrian (riset tetap manual
                                 lewat Claude Code, tidak bisa otomatis)

Jalankan: .venv/bin/python telegram_bot.py
Berhenti: Ctrl+C
"""
import asyncio
import json
import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

load_dotenv()

ROOT        = Path(__file__).resolve().parent
STATE_PATH  = ROOT / "state.json"
BOT_TOKEN   = os.environ["TELEGRAM_BOT_TOKEN"]
OWNER_CHAT  = int(os.environ["TELEGRAM_CHAT_ID"])
APPROVAL    = "data aman, lanjut render"
PYTHON_BIN  = str(ROOT / ".venv" / "bin" / "python")


def _load_state() -> dict:
    return json.loads(STATE_PATH.read_text(encoding="utf-8"))


def _save_state(st: dict) -> None:
    STATE_PATH.write_text(json.dumps(st, ensure_ascii=False, indent=2), encoding="utf-8")


def owner_only(handler):
    async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_chat is None or update.effective_chat.id != OWNER_CHAT:
            return
        await handler(update, context)
    return wrapped


@owner_only
async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    st = _load_state()
    lines = [
        "*Status Pipeline Moovon Finance*",
        f"Topik saat ini: {st.get('current_topic') or '-'}",
        f"Fase: {st.get('phase')}",
        f"Terakhir jalan: {st.get('last_run') or '-'}",
    ]
    if st.get("blocked"):
        lines.append(f"\n⚠️ Blocked: {st['blocked']}")
    pending = st.get("pending_topics") or []
    if pending:
        lines.append(f"\n🕓 Antrian riset: {', '.join(pending)}")
    requested = st.get("requested_topics_telegram") or []
    if requested:
        items = ", ".join(f"{r['topic']} ({r['requested_at']})" for r in requested)
        lines.append(f"\n📝 Diminta via Telegram (belum diriset): {items}")
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


@owner_only
async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Perintah yang tersedia:\n\n"
        "/status — cek status pipeline\n\n"
        "\"Data aman, lanjut render\" — approve & mulai render video yang lagi "
        "nunggu (jalanin produce_script di state.json step1 lalu step2)\n\n"
        "\"mulai topik: <nama>\" — catat topik baru ke antrian. Riset & draft "
        "naskah tetap harus lewat sesi Claude Code (butuh riset web, tidak "
        "bisa otomatis dari bot)."
    )


async def _run_step(produce_script: str, step: str) -> tuple[bool, str]:
    proc = await asyncio.create_subprocess_exec(
        PYTHON_BIN, produce_script, step,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
        cwd=str(ROOT),
    )
    out = []
    async for raw in proc.stdout:
        out.append(raw.decode(errors="replace").rstrip())
    await proc.wait()
    tail = "\n".join(out[-15:]) or "(tidak ada output)"
    return proc.returncode == 0, tail


def parse_topic_command(text: str) -> str | None:
    """Ekstrak nama topik dari 'mulai topik: <nama>' / 'mulai topik <nama>'.
    None kalau teks bukan perintah ini; string kosong kalau perintahnya ada
    tapi tanpa nama topik."""
    low = text.lower()
    if low.startswith("mulai topik:"):
        return text[len("mulai topik:"):].strip()
    if low.startswith("mulai topik "):
        return text[len("mulai topik "):].strip()
    return None


@owner_only
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip()
    low  = text.lower()

    if low == APPROVAL:
        draft = ROOT / "assets" / "draft_script_moovon.md"
        if not draft.exists():
            await update.message.reply_text("Nggak ada draft aktif di assets/draft_script_moovon.md.")
            return

        await update.message.reply_text("🚀 Mulai render (`produce.py render`) — TTS + visual + compile...", parse_mode="Markdown")
        ok, tail = await _run_step("produce.py", "render")
        if not ok:
            await update.message.reply_text(f"❌ Render gagal:\n```\n{tail}\n```", parse_mode="Markdown")
            return

        await update.message.reply_text(
            f"✅ Render selesai!\n```\n{tail}\n```\n"
            "Review dulu videonya — upload tetap manual/terpisah setelah oke "
            "(`python produce.py upload <run_dir>` setelah metadata.json siap).",
            parse_mode="Markdown",
        )
        return

    topic = parse_topic_command(text)
    if topic is not None:
        if not topic:
            await update.message.reply_text("Formatnya: \"mulai topik: <nama topik>\"")
            return
        st = _load_state()
        queue = st.setdefault("requested_topics_telegram", [])
        queue.append({"topic": topic, "requested_at": datetime.now().strftime("%Y-%m-%d %H:%M")})
        _save_state(st)
        await update.message.reply_text(
            f"📝 Topik \"{topic}\" sudah dicatat.\n"
            "Riset & draft naskah tetap harus lewat sesi Claude Code (butuh riset web + "
            "guardrail SOP) — buka sesi baru dan bilang mau mulai topik ini."
        )
        return

    await update.message.reply_text("Perintah nggak dikenali. Ketik /help buat lihat command yang tersedia.")


def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    print("🤖 Bot Moovon Finance jalan... (Ctrl+C untuk stop)")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
