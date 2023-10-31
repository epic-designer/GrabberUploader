import importlib
from itertools import groupby
from telegram import InputMediaPhoto
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultPhoto, InputTextMessageContent, InputMediaPhoto
from telegram import InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import InlineQueryHandler,CallbackQueryHandler, ChosenInlineResultHandler
from pymongo import MongoClient, ReturnDocument
import urllib.request
import random
from datetime import datetime, timedelta
from threading import Lock
import time
from Botttt import dispatcher,updater

from Botttt.modules import ALL_MODULES
client = MongoClient('mongodb+srv://shuyaashivu:9fcc60263a946ef550d11406667404fa@cluster0.ikub9lo.mongodb.net/?retryWrites=true&w=majority')
db = client['Character_catcher']
collection = db['anime_characters_lol']




# List of sudo users
sudo_users = ['6404226395', '6185531116', '5298587903', '5798995982', '5150644651', '5813998595', '5813403535', '6393627898', '5952787198', '6614280216','6248411931','5216262234','1608353423', '5030730429']


# Create a dictionary of locks
locks = {}
# Counter for messages in each group
message_counters = {}
spam_counters = {}
# Last sent character in each group
last_characters = {}

# Characters that have been sent in each group
sent_characters = {}

# Keep track of the user who guessed correctly first in each group
first_correct_guesses = {}

IMPORTED = {}
MIGRATEABLE = []
HELPABLE = {}
STATS = []
USER_INFO = []
DATA_IMPORT = []
DATA_EXPORT = []
CHAT_SETTINGS = {}
USER_SETTINGS = {}

for module_name in ALL_MODULES:
    imported_module = importlib.import_module("Botttt.modules." + module_name)
    


def get_next_sequence_number(sequence_name):
    # Get a handle to the sequence collection
    sequence_collection = db.sequences

    # Use find_one_and_update to atomically increment the sequence number
    sequence_document = sequence_collection.find_one_and_update(
        {'_id': sequence_name}, 
        {'$inc': {'sequence_value': 1}}, 
        return_document=ReturnDocument.AFTER
    )

    # If this sequence doesn't exist yet, create it
    if not sequence_document:
        sequence_collection.insert_one({'_id': sequence_name, 'sequence_value': 0})
        return 0

    return sequence_document['sequence_value']

def upload(update: Update, context: CallbackContext) -> None:
    # Check if user is a sudo user
    if str(update.effective_user.id) not in sudo_users:
        update.message.reply_text('You do not have permission to use this command.')
        return

    try:
        # Extract arguments
        args = context.args
        if len(args) != 4:
            update.message.reply_text('Incorrect format. Please use: /upload img_url Character-Name Anime-Name Rarity')
            return

        # Replace '-' with ' ' in character name and convert to title case
        character_name = args[1].replace('-', ' ').title()
        anime = args[2].replace('-', ' ').title()

        # Check if image URL is valid
        try:
            urllib.request.urlopen(args[0])
        except:
            update.message.reply_text('Invalid image URL.')
            return

        # Check if rarity is valid
        rarity_map = {1: "⚪ Common", 2: "🟣 Rare", 3: "🟡 Legendary", 4: "🟢 Medium"}
        try:
            rarity = rarity_map[int(args[3])]
        except KeyError:
            update.message.reply_text('Invalid rarity. Please use 1, 2, 3, or 4.')
            return

        # Generate ID
        id = str(get_next_sequence_number('character_id')).zfill(4)

        # Insert new character
        character = {
            'img_url': args[0],
            'name': character_name,
            'anime': anime,
            'rarity': rarity,
            'id': id
        }
        
        # Send message to channel
        message = context.bot.send_photo(
            chat_id='-1002084608099',
            photo=args[0],
            caption=f'<b>Character Name:</b> {character_name}\n<b>Anime Name:</b> {anime}\n<b>Rarity:</b> {rarity}\n<b>ID:</b> {id}\nAdded by <a href="tg://user?id={update.effective_user.id}">{update.effective_user.first_name}</a>',
            parse_mode='HTML'
        )

        # Save message_id to character
        character['message_id'] = message.message_id
        collection.insert_one(character)

        update.message.reply_text('DONE.. CHEACK IN @characters_database')
    except Exception as e:
        update.message.reply_text(f'Unsuccessfully uploaded. Error: {str(e)}')

def delete(update: Update, context: CallbackContext) -> None:
    # Check if user is a sudo user
    if str(update.effective_user.id) not in sudo_users:
        update.message.reply_text('You do not have permission to use this command.')
        return

    try:
        # Extract arguments
        args = context.args
        if len(args) != 1:
            update.message.reply_text('Incorrect format. Please use: /delete ID')
            return

        # Delete character with given ID
        character = collection.find_one_and_delete({'id': args[0]})

        if character:
            # Delete message from channel
            context.bot.delete_message(chat_id='-1001915956222', message_id=character['message_id'])
            update.message.reply_text('Successfully deleted.')
        else:
            update.message.reply_text('No character found with given ID.')
    except Exception as e:
        update.message.reply_text('Failed to delete character.')


def anime(update: Update, context: CallbackContext) -> None:
    try:
        # Get all unique anime names
        anime_names = collection.distinct('anime')

        # Send message with anime names
        update.message.reply_text('\n'.join(anime_names))
    except Exception as e:
        update.message.reply_text('Failed to fetch anime names.')


def total(update: Update, context: CallbackContext) -> None:
    try:
        # Extract arguments
        args = context.args
        if len(args) != 1:
            update.message.reply_text('Incorrect format. Please use: /total Anime-Name')
            return

        # Replace '-' with ' ' in anime name
        anime_name = args[0].replace('-', ' ')

        # Get all characters of the given anime
        characters = collection.find({'anime': anime_name})

        # Create a list of character names and IDs
        character_list = [f'Character Name: {character["name"]}\nID: {character["id"]}' for character in characters]

        # Send message with character names and IDs
        update.message.reply_text('\n\n'.join(character_list))
    except Exception as e:
        update.message.reply_text('Failed to fetch characters.')













def main() -> None:
    
    
    dispatcher.add_handler(CommandHandler('upload', upload, run_async=True))
    
    dispatcher.add_handler(CommandHandler('delete', delete, run_async=True))
    
    dispatcher.add_handler(CommandHandler('animee', anime, run_async=True))
    dispatcher.add_handler(CommandHandler('total', total, run_async=True))
    
     
    
    updater.start_polling(
            timeout=15,
            read_latency=4,
            drop_pending_updates=True,
            
    )
    
    updater.idle()
    
if __name__ == '__main__':
    
    main()
    
