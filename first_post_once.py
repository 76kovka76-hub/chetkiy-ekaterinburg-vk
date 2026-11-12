"""Publish one real welcome post and record it to prevent duplicate messages."""
import logging
from datetime import datetime, timezone
from main import GROUP_ID, history_load, history_save, format_message, post_vk, slot

TEST_KEY = "welcome_ekaterinburg_first_2026"
DRAFT = {
    "publish": True,
    "sentence": "🤝 Братва, давайте знакомиться — кто из какого района Екатеринбурга, пишите в комменты!",
    "hashtags": ["#ЕкатеринбургНаСвязи", "#ЕкатеринбургЗнакомимся", "#ЕкатеринбургНашЧат"],
}


def main():
    now = datetime.now(timezone.utc)
    time_slot = slot(now)
    history = history_load()
    if any(p.get("game_key") == TEST_KEY for p in history["posts"]):
        logging.info("Приветственный пост уже отправлен. Повторов не будет.")
        return
    if any(p.get("slot") == time_slot for p in history["posts"]):
        logging.info("Этот 48-минутный слот уже занят. Повторная публикация отменена.")
        return
    if sum(str(p.get("slot", "")).startswith(time_slot[:10]) for p in history["posts"]) >= 30:
        logging.info("Достигнут суточный предел постов.")
        return
    text = format_message(DRAFT, history)
    if not text:
        raise RuntimeError("Тестовый текст не прошёл проверку формата или хэштегов")
    post_id = post_vk(text, "first-ekb-welcome-once-2026")
    history["posts"].append({
        "slot": time_slot,
        "post_id": post_id,
        "kind": "game",
        "game_key": TEST_KEY,
        "title": "Приветственный пост и знакомство",
        "text": DRAFT["sentence"],
        "published_at": now.isoformat()
    })
    history["used_tags"].extend(DRAFT["hashtags"])
    history_save(history)
    logging.info("ПОСТ ОТПРАВЛЕН В ВК: https://vk.com/wall-%s_%s", GROUP_ID, post_id)


if __name__ == "__main__":
    main()
