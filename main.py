import datetime
import random

import telebot
from telebot.types import Message, ReplyKeyboardRemove as RM, ReplyKeyboardMarkup as RKM, InlineKeyboardButton as IB, InlineKeyboardMarkup as IKM,CallbackQuery as Cq
import s_taper
from s_taper.consts import *
import time

temp = {}
powers={'воздух🍃':(100,17),'Вода🌊':(90,22),'Земля 🌍':(150,16)}
users={
    'userid':INT+KEY,
    'username':TEXT,
    'power':TEXT,
    'hp':INT,
    'damage':INT,
    'levl':INT,
    'xp':INT
}
eats={
    'userid':INT+KEY,
    'food':TEXT
}
heals=s_taper.Taper('eats','rpg_game.db').create_table(eats)
user=s_taper.Taper('users','rpg_game.db').create_table(users)
bot=telebot.TeleBot('7344957153:AAHt6VMzyrnps70n_0mvmHgKeXheq-EmZcI')
class Enemy:
    enemies = {
        'Вурдалак': (80, 20),
        'Призрак': (85, 15),
        'Минотавр': (100, 15),
        'Медуза': (75, 25),
        'Bop': (60, 20),
        'Феникс': (130, 30),
        'Дракон': (150, 40),
        'Пьяный дед': (90, 25),
        'голодная свинья': (400, 20)
        }

    def __init__(self, hero_lvl):
        self.name = random.choice(list(self.enemies))
        self.hp=self.enemies[self.name][0] + (5 * (hero_lvl-1))  # зависимость от уровня героя
        self.damage = self.enemies[self.name][1] + (5* (hero_lvl - 1)) # зависимость от уровня героя

def fight(msg: Message):
    bot.send_message(msg.chat.id, 'Ты отправился за пределы деревни в поисках врагов...')
    time.sleep(3)
    bot.send_message(msg.chat.id, 'Kажется враги уже близко...')
    time.sleep(1)
    new_enemy(msg)
def new_enemy (msg: Message):
    player = user.read('userid', msg.chat.id)
    enemy=Enemy(player[5])
    kb = RKM(True, True)
    kb.row("Сразиться", "Сбежать")
    kb.row("Вернуться в город")
    txt = f'Tы встретил врага: {enemy.name}, xn: {enemy.hp}, урон: {enemy.damage}. \nчто будешь делать?'
    bot.send_message(msg.chat.id, txt, reply_markup=kb)
    bot.register_next_step_handler(msg, fight_handler, enemy)
def fight_handler(msg:Message,enemy:Enemy):
    if msg.text=='Сразиться':
        attack(msg,enemy)
    elif msg.text=='Сбежать':
        run=random.randint(1,5)
        if run in range(2,3):
            bot.send_message(msg.chat.id,'Вы сбежали')
            time.sleep(3)
            new_enemy(msg)
        else:
            bot.send_message(msg.chat.id,'вам неудалось сбежать, вас догнали')
            attack(msg,enemy)
    elif  msg.text=='Вернуться в город':
        time.sleep(3)
        bot.send_message(msg.chat.id,'Вы вернулись в город')
        time.sleep(3)
        menu(msg)
def attack(msg:Message,enemy:Enemy):
    att=player_attack(msg,enemy)
    if att is True:
        att=enemy_attack(msg,enemy)
        if att is True:
            attack(msg,enemy)
    else:
        player=user.read('userid',msg.chat.id)
        time.sleep(2)
        xp=random.randint(20,30)
        bot.send_message(msg.chat.id,f'За бой вы получили {xp} опыта')
        player[6]+=xp
        user.write(player)
        xp_check(msg)
        bot.send_message(msg.chat.id,'вы отпрвляетесь дальше')
        new_enemy(msg)
        return
def player_attack(msg:Message,enemy:Enemy):
        time.sleep(2)
        player=user.read('userid',msg.chat.id)
        enemy.hp-=player[4]
        if enemy.hp<=0:
            bot.send_message(msg.chat.id,'вы победили')
            return False
        else:
            bot.send_message(msg.chat.id,f'{enemy.name}, hp {round(enemy.hp,1)}')
            return True
def enemy_attack(msg:Message,enemy:Enemy):
    time.sleep(2)
    player = user.read('userid', msg.chat.id)
    player[3]-=enemy.damage
    user.write(player)
    if player[3]<=0:
        player[3]=1
        user.write(player)
        bot.send_message(msg.chat.id,'вы почти погибли')
        time.sleep(2)
        menu(msg)
        return
    else:
        bot.send_message(msg.chat.id,f'{player[1]}, hp {round(player[3],1)}')
        return True

def xp_check(m: Message):
    player = user.read('user_id', m.chat.id)
    if player[6] >= 100 + ((player[5]-1) *50):
        player[6] -= 100 + ((player[5]- 1) * 50)
        player[3] = powers[player[2]][0] + ((player[5] - 1) * 15)
        player[5] += 1
        player[4] += 5
        player[3] += 15
        user.write(player)
        t = f"Стиxия: {player[2]}\nHикнейм: {player[1]}\n" \
            f"здоровье: {player[3]}\n" \
            f"урон: {player[4]}\n" \
            f"уровень: {player[5]}\noпыт: {player[6]}"
        bot.send_message(m.chat.id, f'Поздравляю с повышением уровня!!! Вот твои характеристики:\n' + t)
        time.sleep(2)
        return
    return
def new_player(msg:Message):
    result=user.read_all()
    for b in result:
        if b [0]==msg.chat.id:
            return False
    return True
@bot.message_handler(['start'])
def start(msg: Message):
   if new_player(msg):
       temp[msg.chat.id] = {}
       reg_1(msg)
   else:
       menu(msg)
def reg_1(msg: Message):  # тут мы приветствуем игрока и спрашиваем имя
    text = ("Привет, %s. В этой игре ты отринешь свою сущность и станешь настоящим магом 🧙‍♂️. Мир на пороге "
           "уничтожения: народ огня 🔥 развязал войну, и именно ты станешь тем, кто поможет им в ней или будет"
           "противостоять им⚔️!\nЯ верю в тебя!\n\nНазови своё имя, новобранец:")
    bot.send_message(msg.chat.id, text % msg.from_user.first_name)
    bot.register_next_step_handler(msg, reg_2)
def reg_2(msg: Message):  # спрашиваем стихию
   temp[msg.chat.id]['username']=msg.text
   kb=RKM(resize_keyboard=True,one_time_keyboard=True)
   kb.row('Огонь 🔥','Вода🌊')
   kb.row('Земля 🌍',"воздух🍃")
   bot.send_message(msg.chat.id,'выбери стихию',reply_markup=kb)
   bot.register_next_step_handler(msg, reg_3)
def reg_3(msg: Message):
   if msg.text == "Огонь 🔥":
       bot.send_message(msg.chat.id, "Магия Огня под запретом в городе!")
       reg_2(msg)
       return
   # Сохраняем стихию
   temp[msg.chat.id]["power"] = msg.text
   hp,dmg=powers[msg.text]
   user.write([msg.chat.id, temp[msg.chat.id]["username"], temp[msg.chat.id]["power"], hp, dmg, 1, 0])
   # heals.write([msg.chat.id, {}])
   print("Пользователь добавлен в базу данных")
   bot.send_message(msg.chat.id,"Инициализация")
   time.sleep(2)
   menu(msg)
def reg_4(msg:Message):
    if msg.text == 'тренероваться':
        workout(msg)
    if msg.text == 'испытать ловкость':
        block(msg)
    if msg.text == 'сражаться':
        fight(msg)


def reg_5(msg:Message):
    if msg.text=='восстановить hp':
        eat(msg)
    if msg.text == 'передохнуть':
        sleep(msg)

@bot.message_handler(['menu'])
def menu(msg: Message):
    try:
        print(temp[msg.chat.id])
    except KeyError:
        temp[msg.chat.id]={}
    txt=('Что будешь делать?\n'
         '/square-идём в деревню\n'
         '/home-идём домой восстановить силы\n'
         '/stats-посмотреть статистику')
    bot.send_message(msg.chat.id,txt, reply_markup=RM())

# @bot.message_handler(['fight'])
# def fight(msg:Message):
@bot.message_handler(['add_heal'])
def add_heal(msg:Message):
    _,food=heals.read('userid',msg.chat.id)
    food['проиг с морковкой']=[10,12],
    heals.write([msg.chat.id,food])
    bot.send_message(msg.chat.id,'герой получил припасы')

def eat(msg: Message):
    kb = IKM()
    _, food = heals.read("userid", msg.chat.id)
    if food == {}:
        bot.send_message(msg.chat.id, 'Кушать нечего, воспользуйся командой /add_heal чтобы пополнить '
                                      'свои запасы)', reply_markup=RM())
        menu(msg)
        return
    for key in food:
        if food[key][0] > 0:
            kb.row(IB(f"{key} {food[key][1]} hp. - {food[key][0]} шт.", callback_data=f"food_{key}_{food[key][1]}"))
    bot.send_message(msg.chat.id, "Выбери что будешь есть:", reply_markup=kb)
def eating(msg, ft, hp):
    _, food = heals.read("user_id", msg.chat.id)
    player = user.read("user_id", msg.chat.id)
    # Отнимаем еду
    if food[ft][0] == 1:
        del food[ft]
    else:
        food[ft][0] -= 1
    heals.write([msg.chat.id, food])

    # Добавляем ХП
    player[3] += int(hp)
    user.write(player)
    print("Игрок поел")

@bot.callback_query_handler(func=lambda call: True)
def callback(call: Cq):
    print(call.data)
    if call.data.startswith("food_"):
        a = call.data.split("_")
        eating(call.message, a[1], [2])
        kb = IKM()
        _,food=heals.read("user_id", call.message.chat.id)
        if food == {}:
            bot.send_message(call.message.chat.id,'кушать нечего, воспользуйся командой /add_heal чтоб пополнить запасы',reply_markup=kb)
            menu (call.message)
            return
        for key in food:
            kb.row(IB(f"{key} {food[key][1]} hp. - {food[key][0]} шт.", callback_data=f"food_{key}_{food[key][1]}"))
        bot.edit_message_reply_markup(call.message.chat.id,call.message.message_id,reply_markup=kb)
    if call.data.startswith("sleep_"):
        a = call.data.split("_")
        t = int(a[1])
        bot.send_message(call.message.chat.id, f"Ты лег отдыxать, кол-во секунд для сна: {t}.")
        time.sleep(t)
        sleeping(call.message, a[1])
        bot.delete_message (call.message.chat.id, call.message.message_id)
        menu(call.message)
    if call.data == '0':
        bot.delete_message (call.message.chat.id, call.message.message_id)
        menu (call.message)
    if call.data == "menu":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        menu(call.message)
    if call.data == "workout":
        player = user.read("userid", call.message.chat.id)
        player[4] += player[5] / 10
        player[4] = round(player[4], 2)
        user.write(player)
        bot.answer_callback_query(call.id, f"Ты тренируешься и твоя сила увеличивается!\n Тeпeрь ты наносишь {player[4]}", True)
@bot.message_handler(['home'])
def home(msg:Message):
    kb=RKM(True,True)
    kb.row('восстановить hp', 'передохнуть')
    bot.send_message(msg.chat.id,'чем хочешь заняться? ',reply_markup=kb)
    bot.register_next_step_handler(msg,reg_5)


@bot.message_handler(['square'])
def square(msg: Message):
    kb = RKM(True, True)
    kb.row('тренероваться', 'испытать ловкость','сражаться')
    bot.send_message(msg.chat.id, 'чем хочешь заняться? ', reply_markup=kb)
    bot.register_next_step_handler(msg, reg_4)


def sleep(msg:Message):
    player = user.read("userid",msg.chat.id)
    low = int(powers[player[2]][0] * player[5]) // 2 - player[3]
    high = int(powers[player[2]][0] * player[5]) - player[3]
    kb=IKM()
    if low>0:
        kb.row(IB(f"Вздремнуть — +{low}❤️", callback_data=f"sleep_{low}"))
    if high>0:
        kb.row(IB(f"Вздремнуть — +{high}❤️", callback_data=f"sleep_{high}"))
    if len(kb.keyboard)==0:
        kb.row(IB('Спать не хочется', callback_data='0'))
    bot.send_message(msg.chat.id, "Выбери, сколько будешь отдыхать:", reply_markup=kb)


def sleeping(msg:Message,hp):
    player=user.read('userid', msg.chat.id)
    player[3]+= int(hp)
    user.write(player)
    print('игрок поспал')


@bot.message_handler(['stats'])
def stats(msg:Message):
    player=user.read('userid',msg.chat.id)
    t = f"Стихия: {player[2]}\nНикнейм: {player[1]}\n" \
        f"Здоровье: {player[3]}❤️\n" \
        f"Урон: {player[4]}⚔️\n" \
        f"Уровень: {player[5]}\nОпыт: {player[6]}⚜️\n\n" \
        f"Еда:\n"
    _,food=heals.read('userid',msg.chat.id)
    for x in food:
        t+=f'{x} ❤️{food[x][1]}-{food[x][0]}штук\n'
    bot.send_message(msg.chat.id, t)
    time.sleep(3)
    menu(msg)
def workout(msg:Message):
    kb=IKM()
    kb.row(IB('тренероваться',callback_data='workout'))
    kb.row(IB('Назад',callback_data='menu'))
    bot.send_message(msg.chat.id,'нажми чтоб тренероваться',reply_markup=kb)
def block(msg:Message):
    try:
        print(temp[msg.chat.id]['win'])
    except KeyError:
        temp[msg.chat.id]['win']=0
    bot.send_message(msg.chat.id,'приготовься к атаке ',reply_markup=RM())
    time.sleep(3)
    side=["Слево","Справо","Снизу","Сверху"]
    random.shuffle(side)
    kb=RKM(True,False)
    kb.row(side[0],side[3])
    kb.row(side[1], side[2])
    right=random.choice(side)
    bot.send_message(msg.chat.id,f'защищайся удар {right}',reply_markup=kb)
    temp[msg.chat.id]['block_start']=datetime.datetime.now().timestamp()
    bot.register_next_step_handler(msg,block_handler,right)
def block_handler(msg:Message,side:str):
    final=datetime.datetime.now().timestamp()
    if final-temp[msg.chat.id]['block_start']>3 or side!=msg.text:
        bot.send_message(msg.chat.id, 'ваша рекция слишком медленная испытание провалено')
        time.sleep(5)
        menu(msg)
        return
    if temp[msg.chat.id]['win']<5:
        bot.send_message(msg.chat.id, 'ты отбил удар, продолжай')
        temp[msg.chat.id]['win']+=1
        block(msg)
        return
    else:
        temp[msg.chat.id]['win']=0
        player=user.read('userid',msg.chat.id)
        player[3]+=20
        user.write(player)
        bot.send_message(msg.chat.id,'ваше здоровье увеличино')
        time.sleep(2)
        menu(msg)
        return






























bot.infinity_polling()