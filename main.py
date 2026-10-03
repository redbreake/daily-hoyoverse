import asyncio
import json
import os
import sys
import urllib.request
import genshin

# Obtener variables de entorno (Secrets de GitHub)
COOKIE = os.getenv("HOYOLAB_COOKIE")
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")

if not COOKIE:
    print("❌ Error: No se encontró la variable de entorno 'HOYOLAB_COOKIE'.")
    print("👉 Asegúrate de agregar el Secret 'HOYOLAB_COOKIE' en Settings > Secrets and variables > Actions.")
    sys.exit(1)


async def main():
    client = genshin.Client()
    client.set_cookies(COOKIE)

    # Lista de juegos a reclamar
    games = [
        ("Genshin Impact", genshin.Game.GENSHIN),
        ("Zenless Zone Zero", genshin.Game.ZZZ),
    ]

    results = []

    for name, game in games:
        client.game = game
        try:
            reward = await client.claim_daily_reward()
            msg = f"✅ **{name}**: Reclamado con éxito -> **{reward.amount}x {reward.name}**"
            print(msg)
            results.append(msg)
        except genshin.AlreadyClaimed:
            msg = f"ℹ️ **{name}**: Ya reclamado hoy."
            print(msg)
            results.append(msg)
        except genshin.GeetestError:
            msg = f"⚠️ **{name}**: HoYoLAB solicitó verificación Geetest/Captcha."
            print(msg)
            results.append(msg)
        except genshin.InvalidCookies:
            msg = f"❌ **{name}**: Cookies inválidas o expiradas."
            print(msg)
            results.append(msg)
        except Exception as e:
            msg = f"❌ **{name}**: Error al reclamar ({e})"
            print(msg)
            results.append(msg)

    # Notificar a Discord si se configuró el webhook
    if DISCORD_WEBHOOK and results:
        payload = {
            "embeds": [
                {
                    "title": "🎁 HoYoLAB Daily Check-in",
                    "description": "\n".join(results),
                    "color": 5814783,
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
            print("📢 Notificación enviada a Discord correctamente.")
        except Exception as e:
            print(f"⚠️ No se pudo enviar el mensaje a Discord: {e}")


if __name__ == "__main__":
    asyncio.run(main())
