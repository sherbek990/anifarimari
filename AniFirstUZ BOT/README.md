# 🎬 Telegram Anime Bot

Production-ready Telegram bot for browsing, watching and downloading anime,
with a full admin panel, mandatory channel subscription, VIP system, and
channel auto-posting. Built with **Aiogram 3.x**, **SQLAlchemy 2.0 (async)**,
and SQLite (swap to PostgreSQL with one env variable).

## 1. Project structure

```
bot/
├── handlers/
│   ├── users/        # search, anime card, episodes, subscription, VIP
│   └── admin/        # admin panel: CRUD, broadcast, stats, settings
├── keyboards/         # reply & inline keyboards
├── database/          # SQLAlchemy models, engine, repository (requests.py)
├── middlewares/        # user-registration + anti-flood
├── filters/            # IsAdmin custom filter
├── services/            # subscription check, broadcast sender
├── utils/                # states (FSM), text formatting helpers
├── config.py
├── loader.py
├── main.py
└── requirements.txt
```

## 2. Requirements

- Python 3.11+
- A Telegram bot token from [@BotFather](https://t.me/BotFather)

## 3. Installation

```bash
# 1. Clone / copy the project, then enter the folder
cd bot

# 2. Create a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env
# then edit .env and fill in BOT_TOKEN and ADMIN_IDS
```

### .env variables

| Variable | Description |
|---|---|
| `BOT_TOKEN` | Token from @BotFather |
| `ADMIN_IDS` | Comma-separated Telegram IDs that always have admin rights |
| `DATABASE_URL` | `sqlite+aiosqlite:///bot.db` by default. For PostgreSQL use `postgresql+asyncpg://user:pass@host/dbname` |
| `EPISODES_PER_PAGE` | How many episode buttons to show per page (default 20) |

## 4. Running the bot

```bash
python main.py
```

On first run, all database tables are created automatically (SQLite file
`bot.db` appears in the project root).

## 5. Getting started as an admin

1. Add your Telegram numeric ID to `ADMIN_IDS` in `.env` (use a bot like
   [@userinfobot](https://t.me/userinfobot) to find your ID).
2. Send `/admin` to your bot to open the admin panel.
3. **➕ Anime qo'shish** — add an anime (poster, name, genre, episode count,
   dubber, language, unique code, optional channel link).
4. **🎬 Episode qo'shish** — enter the anime's code, then upload episodes
   (number + video) one after another.
5. **⚙️ Sozlamalar → ➕ Kanal qo'shish** — add mandatory-subscription
   channels. **The bot must be an admin in that channel** so it can check
   membership and (for private channels) read invite links.
6. **👑 VIP boshqarish** — grant VIP status to users; VIP users skip the
   mandatory subscription check.
7. **📨 Kanalga post** — auto-generate and publish a formatted anime post to
   any configured channel.
8. **📢 Reklama yuborish** — broadcast text/photo/video to all users.
9. **📊 Statistika** — view total users, anime, searches, views, VIP count.

## 6. How users interact with the bot

- Send any text — the bot searches by anime **name** (partial match) or
  exact **code**.
- The anime card shows poster, title, episode count, genre, dubber,
  language, code, search/view counters, and reaction buttons
  (❤️ 🔥 👍 💯).
- **💎 Tomosha qilish 💎** opens a paginated episode picker (5 buttons per
  row, auto-paginated above 20 episodes); tapping a number sends that
  episode's video.
- **📥 Yuklash** opens the same episode picker for downloading.
- If mandatory subscription is enabled and the user hasn't joined the
  required channels, they're blocked and shown channel + verify buttons
  until they join (or become VIP).

## 7. Migrating to PostgreSQL

1. `pip install asyncpg` (already in requirements.txt).
2. Set `DATABASE_URL=postgresql+asyncpg://user:password@host:5432/dbname`
   in `.env`.
3. Run `python main.py` — tables are created automatically via SQLAlchemy
   metadata; no manual migration needed for a fresh database.

## 8. Notes on scaling

- All DB access goes through `database/requests.py`, so swapping ORMs or
  adding caching later only touches one file.
- `middlewares/throttling.py` provides simple per-user rate limiting;
  swap in Redis-backed storage (`aiogram`'s `RedisStorage`) for multi-worker
  deployments instead of `MemoryStorage` in `loader.py`.
- Broadcasts run with a small delay per message to respect Telegram's
  flood limits and automatically mark users who blocked the bot.
