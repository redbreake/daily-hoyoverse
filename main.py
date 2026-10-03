import asyncio
import json
import os
import sys
import urllib.request
import genshin

# Obtener variables de entorno (Secrets de GitHub)
COOKIE = os.getenv("HOYOLAB_COOKIE", "").strip()
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK", "").strip()

if not COOKIE:
    print("❌ Error: No se encontró la variable de entorno 'HOYOLAB_COOKIE'.")
    print("👉 Agrega el Secret 'HOYOLAB_COOKIE' en Settings > Secrets and variables > Actions.")
    sys.exit(1)

# Verificar si las cookies contienen los identificadores necesarios
has_v2 = ("ltuid_v2" in COOKIE or "account_id_v2" in COOKIE or "ltmid_v2" in COOKIE) and ("ltoken_v2" in COOKIE or "cookie_token_v2" in COOKIE)
has_v1 = ("ltuid" in COOKIE or "account_id" in COOKIE) and ("ltoken" in COOKIE or "cookie_token" in COOKIE)

if not (has_v2 or has_v1):
    print("⚠️ ADVERTENCIA: La cookie ingresada parece incompleta.")
    print("👉 'document.cookie' en la consola no incluye cookies HttpOnly como 'ltoken_v2' o 'ltuid_v2'.")
    print("👉 Debes copiar las cookies desde F12 -> Application/Almacenamiento -> Cookies, o desde F12 -> Network (Cabecera Cookie).")


async def main():
    client = genshin.Client()
    try:
        client.set_cookies(COOKIE)
    except Exception as e:
        print(f"❌ Error al configurar las cookies: {e}")
        sys.exit(1)

    games = [
        ("Genshin Impact", genshin.Game.GENSHIN),
        ("Zenless Zone Zero", genshin.Game.ZZZ),
    ]

    results = []
    has_errors = False

    for name, game in games:
        try:
            reward = await client.claim_daily_reward(game=game)
            msg = f"✅ **{name}**: Reclamado con éxito -> **{reward.amount}x {reward.name}**"
            print(msg)
            results.append(msg)
        except genshin.AlreadyClaimed:
            msg = f"ℹ️ **{name}**: Ya reclamado hoy."
            print(msg)
            results.append(msg)
        except genshin.GeetestError:
            msg = f"⚠️ **{name}**: HoYoLAB solicitó verificación Geetest (Captcha)."
            print(msg)
            results.append(msg)
            has_errors = True
        except genshin.InvalidCookies:
            msg = f"❌ **{name}**: Cookies inválidas o expiradas."
            print(msg)
            results.append(msg)
            has_errors = True
        except Exception as e:
            msg = f"❌ **{name}**: Error al reclamar ({e})"
            print(msg)
            results.append(msg)
            has_errors = True

    # Notificar a Discord si se configuró webhook
    if DISCORD_WEBHOOK and results:
        payload = {
            "embeds": [
                {
                    "title": "🎁 HoYoLAB Daily Check-in",
                    "description": "\n".join(results),
                    "color": 15158332 if has_errors else 3066993,
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

    if has_errors:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
