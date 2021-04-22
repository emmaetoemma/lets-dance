from flask import Flask, request
import logging
import json
import os

from buttons import *
from apis import get_schools_by_address


app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

sessionStorage = {}


@app.route('/post', methods=['POST'])
def main():
    logging.info(f'Request: {request.json!r}')
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }
    handle_dialog(response, request.json)
    logging.info(f'Response: {response!r}')
    return json.dumps(response)


def stop_dialog(user_id, res):
    del sessionStorage[user_id]
    res['response']['text'] = 'Ну и ладно!'
    res['response']['end_session'] = True


def handle_dialog(res, req):
    user_id = req['session']['user_id']
    if req['session']['new'] or user_id not in sessionStorage:
        res['response']['text'] = 'Привет! Хочешь пройти тест на темперамент?'
        sessionStorage[user_id] = {
            'wedding_dance': None,
            'step': 0,
            'color': None
        }

        # Кнопки подсказки внизу
        res['response']['buttons'] = step_0_buttons
        return
    # else лишний, ведь в ифе ретурн
    if sessionStorage[user_id]['step'] == 0:
        if 'да' in req['request']['nlu']['tokens']:
            res['response']['text'] = 'В ближайшую субботу у вас есть выбор куда пойти, что вы предпочтёте? ' \
                                      'Пляжную вечеринку, ужин вдвоём, торжественный гала ужин или диджей пати в клубе?'
            res['response']['buttons'] = step_1_buttons
            sessionStorage[user_id]['step'] += 1  # не забываем перевести алгоритм на следующий шаг
        elif 'нет' in req['request']['nlu']['tokens']:
            stop_dialog(user_id, res)
        else:
            res['response']['text'] = 'Не поняла ответа! Так да или нет?'
            res['response']['buttons'] = step_0_buttons
    elif sessionStorage[user_id]['step'] == 1:
        answer = first_task(req)
        if answer is not None:
            # Если всё ок и был дан верный ответ
            sessionStorage[user_id]['step'] += 1
            res['response']['text'] = 'Сколько вам лет?'
        else:
            res['response']['text'] = 'Не поняла ответа! Так что вы предпочтёте? ' \
                                      'Пляжную вечеринку, ужин вдвоём, торжественный гала ужин или диджей пати в клубе?'
            res['response']['buttons'] = step_1_buttons
    elif sessionStorage[user_id]['step'] == 2:
        answer = second_task(req)
        if answer is not None:
            sessionStorage[user_id]['step'] += 1  # не забываем перевести алгоритм на следующий шаг
            res['response']['text'] = 'К просмотру есть 4 фильма, какой вы выберете? ' \
                                      'Грязные танцы с Партиком Суэйзи, Давайте потанцуем с Ричардом Гиром, ' \
                                      'Запах женщины с Аль Пачино или Супер Майкл иксиксэль с Ченингом Татумом.'
            res['response']['buttons'] = step_3_buttons
        else:
             res['response']['text'] = 'Не поняла ответа! Скажите сколько вам полных лет?'
    elif sessionStorage[user_id]['step'] == 3:
        answer = third_task(req)
        if answer is not None:
            sessionStorage[user_id]['step'] += 1  # не забываем перевести алгоритм на следующий шаг
            res['response']['text'] = 'Оцените свой танцевальный уровень по шкале от 1 до 5. 1 - я не умею танцевать, ' \
                                      '5 - я король танцпола.'
            res['response']['buttons'] = step_4_buttons
        else:
            res['response']['text'] = 'Не поняла ответа! Выберете один из этих фильмов: ' \
                                      'Грязные танцы с Партиком Суэйзи, Давайте потанцуем с Ричардом Гиром, ' \
                                      'Запах женщины с Аль Пачино или Супер Майкл иксиксэль с Ченингом Татумом.'
            res['response']['buttons'] = step_3_buttons
    elif sessionStorage[user_id]['step'] == 4:
        answer = fourth_task(req)
        if answer is not None:
            sessionStorage[user_id]['step'] += 1  # не забываем перевести алгоритм на следующий шаг
            res['response']['text'] = 'Какой танец из трёх вы выбрали бы для своего свадебного танца? ' \
                                      'Медленный вальс, аргентинское танго, сальса.'
            res['response']['buttons'] = step_5_buttons
        else:
            res['response']['text'] = 'Не поняла ответа! Оцените свой танцевальный уровень по шкале от 1 до 5.'
            res['response']['buttons'] = step_4_buttons
    elif sessionStorage[user_id]['step'] == 5:
        answer = fifth_task(req)
        if answer is not None:
            sessionStorage[user_id]['step'] += 1 # не забываем перевести алгоритм на следующий шаг
            res['response']['text'] = 'Какой цвет из представленных, вам больше всего нравится? Фиолетовый, красный, ' \
                                      'синий, оранжевый, зелёный, жёлтый, пудровый, бирюзовый.'
            res['response']['buttons'] = step_6_buttons
        else:
            res['response']['text'] = 'Не поняла ответа! Какой танец из трёх вы выбрали бы для своего свадебного танца? ' \
                                      'Медленный вальс, аргентинское танго, сальса.'
            res['response']['buttons'] = step_5_buttons
    elif sessionStorage[user_id]['step'] == 6:
        answer = sixth_task(req)
        if answer is not None:
            sessionStorage[user_id]['color'] = answer
            sessionStorage[user_id]['step'] += 1 # не забываем перевести алгоритм на следующий шаг
            # подставка текста про танец, определенный цветом и вопросом про адрес
            choose_color_phrase(user_id, res)
            res['response']['buttons'] = step_7_buttons
        else:
            res['response']['text'] = 'Не поняла ответа! Какой цвет из представленных, вам больше всего нравится? ' \
                                      'Фиолетовый, красный, синий, оранжевый, зелёный, жёлтый, пудровый, бирюзовый.'
            res['response']['buttons'] = step_6_buttons
    elif sessionStorage[user_id]['step']  == 7:
        if 'да' in req['request']['nlu']['tokens']:
            sessionStorage[user_id]['step'] += 1  # не забываем перевести алгоритм на следующий шаг
            res['response']['text'] = 'Хорошо. Подскажите, пожалуйста, свой адрес.'
        elif 'нет' in req['request']['nlu']['tokens']:
            stop_dialog(user_id, res)
        else:
            res['response']['text'] = 'Не поняла ответа! Так да или нет?'
            res['response']['buttons'] = step_7_buttons
    elif sessionStorage[user_id]['step'] == 8:
        schools = get_schools_by_address(get_address(req))
        if schools is not None:
            text = 'Я подобрала вам несколько школ поблизости. Взгляните:'
            counter = 1
            for school in schools:
                text += '\n%s. Школа "%s" по адресу %s' % (counter, school['name'], school['address'])
                counter += 1
            text += '\n\nНадеюсь, мне удалось помочь вам в поиске школы танцев! Удачи!'
            res['response']['text'] = text
            res['response']['end_session'] = True
            del sessionStorage[user_id]
        else:
            res['response']['text'] = 'Что-то не могу найти ваш адрес или школ поблизости. Попробуйте повторить свой адрес.'


def first_task(req):
    for token in req['request']['nlu']['tokens']:
        if token.lower() in ['вечеринка', 'вечеринку']:
            return 'Пляжная вечеринка'
        elif token.lower() in ['вдвоём', 'вдвоем']:
            return 'Ужин вдвоём'
        elif token.lower() in ['торжественный', 'торжественый']:
            return 'Торжественный гала ужин'
        elif token.lower() == 'диджей':
            return 'Диджей пати в клубе'


def second_task(req):
    for entity in req['request']['nlu']['entities']:
        if entity['type'] == 'YANDEX.NUMBER':
            return entity['value']


def third_task(req):
    for token in req['request']['nlu']['tokens']:
        if token.lower() == 'грязные':
            return 'Грязные танцы'
        elif token.lower() == 'давайте':
            return 'Давайте потанцуем'
        elif token.lower() == 'запах':
            return 'Запах женщины'
        elif token.lower() == 'майкл':
            return 'Супер Майкл иксиксэль'


def fourth_task(req):
    for entity in req['request']['nlu']['entities']:
        if entity['type'] == 'YANDEX.NUMBER':
            return entity['value']


def fifth_task(req):
    for token in req['request']['nlu']['tokens']:
        if token.lower() == 'вальс':
            return 'Медленный вальс'
        elif token.lower() == 'танго':
            return 'Аргентинское танго'
        elif token.lower() in ['сальса', 'сальсу']:
            return 'Сальса'


def sixth_task(req):
    for token in req['request']['nlu']['tokens']:
        if token.lower() == 'фиолетовый':
            return 'Фиолетовый'
        elif token.lower() == 'красный':
            return 'Красный'
        elif token.lower() == 'синий':
            return 'Синий'
        elif token.lower() == 'оранжевый':
            return 'Оранжевый'
        elif token.lower() in ['зелёный', 'зеленый']:
            return 'Зелёный'
        elif token.lower() in ['жёлтый', 'желтый']:
            return 'Жёлтый'
        elif token.lower() == 'пудровый':
            return 'Пудровый'
        elif token.lower() == 'бирюзовый':
            return 'Бирюзовый'


def choose_color_phrase(user_id, res):
    if sessionStorage[user_id]['color'] == 'Фиолетовый':
        res['response']['text'] = 'Вы человек с ярким темпераментом. ' \
                                  'Вы всегда смотрите в будущее и абсолютно не злопамятны, ' \
                                  'хотя память у вас хорошая))) Вы инициативная и энергичная личность и легки на подъем! ' \
                                  'Но вам не интересны долгие и монотонные занятия - движение, вот ваше все! ' \
                                  'Я рекомендую вам остановить свой взгляд на танцах в стиле Caribbean STYLE: ' \
                                  'сальса, бачата, меренге и так же сюда попадает танец КИЗОМБА, это некая смесь танго и бачаты.'
    elif sessionStorage[user_id]['color'] == 'Красный':
        res['response']['text'] = 'Вы ярко выраженная личность. Ваше настроение может измениться в любую минуту. ' \
                                  'Энергичный, инициативный и импульсивный - вот вероятнее всего, ' \
                                  'что думают о вас ваши знакомые. Рядом с вами не бывает скучно, ' \
                                  'да и вы скучать не любите. И не смотря на то, ' \
                                  'что вы ярко переживаете любые события, вы скорее незлопамятны и очень отходчивы. ' \
                                  'С большим энтузиазмом беретесь за новые и интересные дела ' \
                                  'и с успехом доводите их до конца, главное чтобы работа не была долгой и монотонной. ' \
                                  'Как только на горизонте маячит монотонность - это конец любому вашему начинанию. ' \
                                  'Я рекомендую вам остановить свой взгляд на Аргентинском танго.'
    elif sessionStorage[user_id]['color'] == 'Синий':
        res['response']['text'] = 'Вы серьезный человек, возможно немного скрытный. ' \
                                  'Но не смотря на внешнюю сдержанность внутри есть огонь. ' \
                                  'Вы предпочитаете строить планы и раскладывать все по полочкам. ' \
                                  'Красоту любите во всем, что вас окружает. Вам нравятся романтические истории, ' \
                                  'но вы их немного боитесь, так как боитесь быть обиженными. ' \
                                  'И вы очень не любите несправедливость. Я рекомендую вам остановить свой взгляд на ' \
                                  'европейской программе бальных танцев и особое внимание обратить на ВАЛЬС.'
    elif sessionStorage[user_id]['color'] == 'Оранжевый':
        res['response']['text'] = 'Вы яркая и эмоциональная личность. Вашей любви к жизни можно только позавидовать. ' \
                                  'При всей своей внутренней скорости вы в то же время очень уравновешенный человек. ' \
                                  'С большой отдачей беретесь за работу, которая вам интересна. ' \
                                  'Вы неплохо приспосабливаетесь к новому окружению. ' \
                                  'Жизнь для вас это источник новых ощущений. Вам всегда хочется чего то нового. ' \
                                  'Общительный и открытый, вот как скорее всего вас описали бы знакомые. ' \
                                  'Я рекомендую вам остановить свой взгляд на ' \
                                  'европейской программе бальных танцев и особое внимание обратить на танец Квикстеп.'
    elif sessionStorage[user_id]['color'] == 'Зелёный':
        res['response']['text'] = 'Скорее всего вы не стремитесь проявлять свои чувства и эмоции на публике. ' \
                                  'Ваши решения качественные и взвешенные. Спокойный и уравновешенный человек, ' \
                                  'вот как бы вас описали ваши знакомые. В вашем характере есть настойчивость и даже упорство. ' \
                                  'При это вы достаточно дружелюбный человек. Если говорить про танцы, ' \
                                  'то вам может понравиться направление в стиле DANCE FITNESS - ZUMBA.'
    elif sessionStorage[user_id]['color'] == 'Жёлтый':
        res['response']['text'] = 'Вы крайне энергичный и легкий на подъем человек, который очень любит движение. ' \
                                  'Вам присуща быстрота реакции и даже возможно вы любите сопровождать свою речь жестикуляцией. ' \
                                  'Но абсолютно точно нельзя сказать, что вы неуравновешенный человек. ' \
                                  'Каждое дело за которое вы беретесь будет доведено до конца, если вызывает ваш интерес. ' \
                                  'Друзья бы про вас сказали, что вы общительный человек и легко приспосабливаетесь к новому окружению. ' \
                                  'Я рекомендую вам остановить свой взгляд на латиноамериканской программе ' \
                                  'бальных танцев и особое внимание обратить на САМБУ.'
    elif sessionStorage[user_id]['color'] == 'Пудровый':
        res['response']['text'] = 'Вы неспешны и любите размеренный образ жизни. Но это абсолютно не означает, ' \
                                  'что в вас нет огня. Скорее это того, ' \
                                  'что вы не спешите проявлять свои чувства на публику. Прагматичен и ответственен, ' \
                                  'вот как описали бы вас ваши знакомые. А еще вы обладаете достаточным упорством ' \
                                  '(конечно когда вам это лично нужно), чтобы достичь любой поставленной цели. ' \
                                  'Я рекомендую вам остановить свой взгляд на европейской программе бальных танцев и ' \
                                  'особое внимание обратить на ВЕНСКИЙ ВАЛЬС.'
    elif sessionStorage[user_id]['color'] == 'Бирюзовый':
        res['response']['text'] = 'Вы очень нежный и романтичный человек и скорее всего очень ранимый. ' \
                                  'Вы склонны к глубоким переживаниям чувств, ' \
                                  'но при этом всегда верите в светлое будущее. В начатых вами делах, чаще всего, ' \
                                  'проявляете себя как идеальный труженик и стараетесь доводить все до логического конца. ' \
                                  'В большинстве случаев Вы хорошо умеете держать себя в руках. ' \
                                  'Возможно в чем-то вам не всегда хватает решимости. ' \
                                  'Я рекомендую вам остановить свой взгляд на европейской программе бальных танцев и ' \
                                  'особое внимание обратить на ВЕНСКИЙ ВАЛЬС.'
    res['response']['text'] += '\n\nЯ могу помочь вам найти школу танцев неподалеку. Хотите воспользоваться моей помощью?'


def get_address(req):
    for entity in req['request']['nlu']['entities']:
        if entity['type'] == 'YANDEX.GEO':
            return ' '.join(entity['value'].values())


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", '127.0.0.1')
    app.run(host=host, port=port)
