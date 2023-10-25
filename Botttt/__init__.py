import telegram.ext as tg
import logging 
from pyrogram import Client , errors
WORKERS = (
        8 # Number of subthreads to use. Set as number of threads your processor uses
)
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[logging.FileHandler("log.txt"), logging.StreamHandler()],
    level=logging.INFO,
)

logging.getLogger("apscheduler").setLevel(logging.ERROR)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("pyrate_limiter").setLevel(logging.ERROR)
LOGGER = logging.getLogger(__name__)

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

