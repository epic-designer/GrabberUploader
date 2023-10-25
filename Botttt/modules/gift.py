from pyrogram import Client, filters
from Botttt import pbot as app

@app.on_message(filters.command("gift"))
async def gift(client, message):
    # Check if the message is a reply to another message
    if not message.reply_to_message:
        await message.reply_text('Please reply to the user you want to gift the character to.')
        return

    # Extract the character ID from the command
    args = message.command
    if len(args) != 2:
        await message.reply_text('Incorrect format. Please use: /gift Character-ID')
        return

    character_id = args[1]

    # Get the user who is giving the gift
    giving_user_id = message.from_user.id

    # Get the user who is receiving the gift
    receiving_user_id = message.reply_to_message.from_user.id

    # Check if the giving user has the character in their collection
    giving_user = await user_collection.find_one({'id': giving_user_id})
    if not any(character['id'] == character_id for character in giving_user['characters']):
        await message.reply_text('You do not have this character in your collection.')
        return

    # Transfer the character from the giving user to the receiving user
    await user_collection.update_one({'id': giving_user_id}, {'$pull': {'characters': {'id': character_id}}})
    await user_collection.update_one({'id': receiving_user_id}, {'$push': {'characters': {'id': character_id}}})

    # Update total counts
    await group_user_totals_collection.update_one({'group_id': message.chat.id, 'user_id': giving_user_id}, {'$inc': {'total_count': -1}})
    await group_user_totals_collection.update_one({'group_id': message.chat.id, 'user_id': receiving_user_id}, {'$inc': {'total_count': 1}})
    
    await message.reply_text(f'Character {character_id} has been gifted from <a href="tg://user?id={giving_user_id}">{message.from_user.first_name}</a> to <a href="tg://user?id={receiving_user_id}">{message.reply_to_message.from_user.first_name}</a>.', parse_mode='HTML')

