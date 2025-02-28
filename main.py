import telebot
from db_logic import DB_Manager
from config import TOKEN, DATABASE
import os


bot = telebot.TeleBot(TOKEN)


db_manager = DB_Manager(DATABASE)


db_manager.create_tables()
db_manager.default_insert()


user_states = {}


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "Привет! Я твой бот-ежедневник. Используй команды для работы с задачами.\n\n"
        "Доступные команды:\n"
        "/addtask - добавить задачу\n"
        "/listtasks - показать все задачи\n"
        "/status - изменить статус задачи\n"
        "/deletetask - удалить задачу"
    )

@bot.message_handler(commands=['addtask'])
def add_task(message):
    user_id = message.from_user.id
    user_states[user_id] = {'state': 'waiting_for_task_name'}
    bot.send_message(message.chat.id, "Введите название задачи:")

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id, {}).get('state') == 'waiting_for_task_name')
def handle_task_name(message):
    user_id = message.from_user.id
    task_name = message.text.strip()
    
    if not task_name:
        bot.send_message(message.chat.id, "Название задачи не может быть пустым. Попробуйте снова.")
        return
    
    user_states[user_id] = {'state': 'waiting_for_task_description', 'task_name': task_name}
    bot.send_message(message.chat.id, "Введите описание задачи:")

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id, {}).get('state') == 'waiting_for_task_description')
def handle_task_description(message):
    user_id = message.from_user.id
    task_description = message.text.strip()
    
    if user_id not in user_states or 'task_name' not in user_states[user_id]:
        bot.send_message(message.chat.id, "Ошибка! Начните заново с /addtask.")
        return
    
    task_name = user_states[user_id]['task_name']
    status_id = db_manager.get_status_id('Ещё не начато')
    
    
    db_manager.insert_task((user_id, task_name, task_description, status_id))
    
    del user_states[user_id]
    bot.send_message(message.chat.id, f"Задача '{task_name}' была добавлена!")

@bot.message_handler(commands=['listtasks'])
def list_tasks(message):
    user_id = message.from_user.id
    tasks = db_manager.get_tasks(user_id)

    if not tasks:
        bot.send_message(message.chat.id, "У тебя нет задач.")
        return

    task_list = "\n".join([f"Задача: {task[2]}\nОписание: {task[3]}\nСтатус: {task[5]}" for task in tasks])
    bot.send_message(message.chat.id, f"Твои задачи:\n{task_list}")

@bot.message_handler(commands=['deletetask'])
def delete_task(message):
    user_id = message.from_user.id
    user_states[user_id] = {'state': 'waiting_for_task_to_delete'}
    bot.send_message(message.chat.id, "Введите название задачи, которую хотите удалить:")

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id, {}).get('state') == 'waiting_for_task_to_delete')
def handle_delete_task(message):
    user_id = message.from_user.id
    task_name = message.text.strip()
    
    task_id = db_manager.get_task_id(task_name, user_id)
    if task_id is None:
        bot.send_message(message.chat.id, "Задача не найдена.")
    else:
        db_manager.delete_task(user_id, task_id)
        bot.send_message(message.chat.id, f"Задача '{task_name}' удалена!")
    
    del user_states[user_id]

bot.polling(none_stop=True)