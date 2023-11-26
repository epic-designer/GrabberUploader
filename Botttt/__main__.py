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
client = MongoClient('mongodb+srv://HaremDBBot:ThisIsPasswordForHaremDB@haremdb.swzjngj.mongodb.net/?retryWrites=true&w=majority')
db = client['Character_catcher']
collection = db['anime_characters_lol']




# List of sudo users
sudo_users = ['1526461061', '2016056536', '5031338594','5075466544','6427372613','1967847517','1424231015','6661715318','6141343858','5343780916','6149191605', '6765826972', '5715764478', '5690711835', '2143949358', '1238234357', '2143949358', '6200551928', '5919319153', '5333885064', '1567333776', '6257904396', '6217632586', '5382772852'
]

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
        rarity_map = {1: "⚪ Common", 2: "🟣 Rare", 3: "🟡 Legendary", 4: "🟢 Medium", 69: "🎄Special"}
        try:
            rarity = rarity_map[int(args[3])]
        except KeyError:
            update.message.reply_text('Invalid rarity. Please use 1, 2, 3, or 4.')
            return

        # Generate ID
        id = str(get_next_sequence_number('character_id')).zfill(2)

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
            chat_id='-1002064277119',
            photo=args[0],
            caption=f'<b>Character Name:</b> {character_name}\n<b>Anime Name:</b> {anime}\n<b>Rarity:</b> {rarity}\n<b>ID:</b> {id}\nAdded by <a href="tg://user?id={update.effective_user.id}">{update.effective_user.first_name}</a>',
            parse_mode='HTML'
        )

        # Save message_id to character
        character['message_id'] = message.message_id
        collection.insert_one(character)

        update.message.reply_text('DONE.. CHEACK IN @kela_lelo')
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
            context.bot.delete_message(chat_id='-1002064277119', message_id=character['message_id'])
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


def update(update: Update, context: CallbackContext) -> None:
    # Check if user is a sudo user
    if str(update.effective_user.id) not in sudo_users:
        update.message.reply_text('You do not have permission to use this command.')
        return

    try:
        # Extract arguments
        args = context.args
        if len(args) != 3:
            update.message.reply_text('Incorrect format. Please use: /update id field new_value')
            return

        # Get character by ID
        character = collection.find_one({'id': args[0]})
        if not character:
            update.message.reply_text('Character not found.')
            return

        # Check if field is valid
        valid_fields = ['img_url', 'name', 'anime', 'rarity']
        if args[1] not in valid_fields:
            update.message.reply_text(f'Invalid field. Please use one of the following: {", ".join(valid_fields)}')
            return

        # Update field
        if args[1] in ['name', 'anime']:
            new_value = args[2].replace('-', ' ').title()
        elif args[1] == 'rarity':
            rarity_map = {1: "⚪ Common", 2: "🟣 Rare", 3: "🟡 Legendary", 4: "🟢 Medium", 69: "🎄Special"}
            try:
                new_value = rarity_map[int(args[2])]
            except KeyError:
                update.message.reply_text('Invalid rarity. Please use 1, 2, 3, or 4.')
                return
        else:
            new_value = args[2]

        collection.find_one_and_update({'id': args[0]}, {'$set': {args[1]: new_value}})

        # If the image URL is updated, delete the old message and send a new one
        if args[1] == 'img_url':
            context.bot.delete_message(chat_id='-1002064277119', message_id=character['message_id'])
            message = context.bot.send_photo(
                chat_id='-1001915956222',
                photo=new_value,
                caption=f'<b>Character Name:</b> {character["name"]}\n<b>Anime Name:</b> {character["anime"]}\n<b>Rarity:</b> {character["rarity"]}\n<b>ID:</b> {character["id"]}\nUpdated by <a href="tg://user?id={update.effective_user.id}">{update.effective_user.first_name}</a>',
                parse_mode='HTML'
            )
            character['message_id'] = message.message_id
            collection.find_one_and_update({'id': args[0]}, {'$set': {'message_id': message.message_id}})
        else:
            # Update message in channel
            context.bot.edit_message_caption(
                chat_id='-1002064277119',
                message_id=character['message_id'],
                caption=f'<b>Character Name:</b> {character["name"]}\n<b>Anime Name:</b> {character["anime"]}\n<b>Rarity:</b> {character["rarity"]}\n<b>ID:</b> {character["id"]}\nUpdated by <a href="tg://user?id={update.effective_user.id}">{update.effective_user.first_name}</a>',
                parse_mode='HTML'
            )

        update.message.reply_text('Character updated successfully.')
    except Exception as e:
        update.message.reply_text(f'Unsuccessfully updated. Error: {str(e)}')







def main() -> None:
    
    
    dispatcher.add_handler(CommandHandler('upload', upload, run_async=True))
    
    dispatcher.add_handler(CommandHandler('delete', delete, run_async=True))
    
    dispatcher.add_handler(CommandHandler('animee', anime, run_async=True))
    dispatcher.add_handler(CommandHandler('total', total, run_async=True))
    dispatcher.add_handler(CommandHandler('update', update, run_async=True))
    
     
    
    updater.start_polling(
            timeout=15,
            read_latency=4,
            drop_pending_updates=True,
            
    )
    
    updater.idle()
    
if __name__ == '__main__':
    
    main()
    
