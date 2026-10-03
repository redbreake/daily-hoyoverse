import asyncio
import json
import os
import sys
import urllib.request
import genshin

# Obtener variables de entorno (Secrets de GitHub)
COOKIE_1 = os.getenv("HOYOLAB_COOKIE", "").strip()
COOKIE_2 = os.getenv("HOYOLAB_COOKIE_2", "").strip() or os.getenv("HOYOLAB_COOKIE_HSR", "").strip()
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK", "").strip()

if not COOKIE_1 and not COOKIE_2:
    print("❌ Error: No se encontraron cookies en los Secrets.")
    print("👉 Configura 'HOYOLAB_COOKIE' en Settings > Secrets and variables > Actions.")
    sys.exit(1)


async def claim_for_account(account_name: str, cookie: str, games: list) -> tuple[list[str], bool]:
    if not cookie:
        return [], False

    client = genshin.Client()
    try:
        client.set_cookies(cookie)
    except Exception as e:
        print(f"❌ [{account_name}] Error al configurar las cookies: {e}")
        return [f"❌ **{account_name}**: Error de cookies ({e})"], True

    results = []
    has_errors = False

    print(f"\n--- Ejecutando check-in para: {account_name} ---")

    for name, game in games:
        try:
            reward = await client.claim_daily_reward(game=game)
            msg = f"✅ **{name}** ({account_name}): Reclamado -> **{reward.amount}x {reward.name}**"
            print(msg)
            results.append(msg)
        except genshin.AlreadyClaimed:
            msg = f"ℹ️ **{name}** ({account_name}): Ya reclamado hoy."
            print(msg)
            results.append(msg)
        except genshin.GeetestError:
            msg = f"⚠️ **{name}** ({account_name}): HoYoLAB solicitó verificación Geetest (Captcha)."
            print(msg)
            results.append(msg)
            has_errors = True
        except genshin.InvalidCookies:
            msg = f"❌ **{name}** ({account_name}): Cookies inválidas o expiradas."
            print(msg)
            results.append(msg)
            has_errors = True
        except Exception as e:
            msg = f"❌ **{name}** ({account_name}): Error al reclamar ({e})"
            print(msg)
            results.append(msg)
            has_errors = True

    return results, has_errors


async def main():
    all_results = []
    overall_errors = False

    # Cuenta 1: Genshin Impact y Zenless Zone Zero
    if COOKIE_1:
        games_acc1 = [
            ("Genshin Impact", genshin.Game.GENSHIN),
            ("Zenless Zone Zero", genshin.Game.ZZZ),
        ]
        res1, err1 = await claim_for_account("Cuenta Principal", COOKIE_1, games_acc1)
        all_results.extend(res1)
        if err1:
            overall_errors = True

    # Cuenta 2: Honkai: Star Rail
    if COOKIE_2:
        games_acc2 = [
            ("Honkai: Star Rail", genshin.Game.STARRAIL),
        ]
        res2, err2 = await claim_for_account("Cuenta Star Rail", COOKIE_2, games_acc2)
        all_results.extend(res2)
        if err2:
            overall_errors = True

    # Notificar a Discord si se configuró el webhook
    if DISCORD_WEBHOOK and all_results:
        payload = {
            "embeds": [
                {
                    "title": "🎁 HoYoLAB Daily Check-in",
                    "description": "\n".join(all_results),
                    "color": 15158332 if overall_errors else 3066993,
                }
            ]
        }
        req = urllib.request.Request(
            DISCORD_WEBHOOK,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
        )
        try:
            urllib.request.urlopen(req)
            print("📢 Notificación enviada a Discord.")
        except Exception as e:
            print(f"⚠️ Error al enviar webhook a Discord: {e}")

    if overall_errors:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
