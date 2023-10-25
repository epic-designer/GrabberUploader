import telegram.ext as tg
import pyrogram Client 
WORKERS = (
        8 # Number of subthreads to use. Set as number of threads your processor uses
)
TOKEN = "6420751168:AAEtf-OyEYLLTZM2c4LrhIroXPfvsW7KlM8"
API_ID = 24427150
API_HASH = "9fcc60263a946ef550d11406667404fa"

pbot = Client("nothing", api_id=API_ID, api_hash=API_HASH, bot_token=TOKEN)

updater = tg.Updater(
    token=TOKEN,
    workers=WORKERS,
    request_kwargs={"read_timeout": 10, "connect_timeout": 10},
    use_context=True,
)

dispatcher = updater.dispatcher

