import random
from enum import Enum
from typing import Dict, Any, List
import json
import pickle
import time
import requests
import openai
from emora_stdm import DialogueFlow, Macro, Ngrams
from src import utils
import ast


class V(Enum):
    call_names = 0,  # str


# Intro Macros
class MacroGetPrize(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        if int(vars['QUIZ_LEFT']) == 0:
            print("drive.google.com/uc?export=view&id=1-L70a0LdkXfRQDT2sJGu1umLXofaHl_5")


class MacroNames(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        model = 'gpt-3.5-turbo'
        content = 'User Response: "{}" Here is the user\'s response to the question "what is your name?". Please format ' \
                  'your answer to output the name of the user. Only output the name that the user wants to be called. You don\'t' \
                  'have to provide any explanation. If the user does not give a valid name, output the single word "anonymous".'.format(
            ngrams.raw_text())
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{'role': 'user', 'content': content}]
        )
        # the answer is the second item in the list
        output = response['choices'][0]['message']['content'].strip()
        vars['NAME'] = output
        vars['master'] = False
        # print(type(vars['master']))
        return True


class MacroIfLike(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        model = 'gpt-3.5-turbo'
        content = 'User Response: "{}" Here is the user\'s response to the question "do you like the prize we give you?" Does the user gives a positive' \
                  'or negative feedback to this question? Format your answer in a single word output of either "positive" or "negative". If the user response' \
                  'is neutral, then still output the exact word "negative". You do not ' \
                  'need to give any explanations to how you arrive at your result.'.format(ngrams.raw_text())
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{'role': 'user', 'content': content}]
        )
        # the answer is the second item in the list
        output = response['choices'][0]['message']['content'].strip()
        if 'positive' in output.lower():
            vars['USER_FEEDBACK'] = 'True'
        else:
            vars['USER_FEEDBACK'] = 'False'
        return True


class MacroTime(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[str]):
        current_time = time.strftime("%H:%M")
        # change the current time to three different categories: morning, afternoon, and evening
        if 5 < int(current_time[:2]) < 12:
            time_day = 'morning'
        elif 12 < int(current_time[:2]) < 18:
            time_day = 'afternoon'
        else:
            time_day = 'evening'
        return time_day


class MacroWeather(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        url = 'https://api.weather.gov/gridpoints/FFC/52,88/forecast'
        r = requests.get(url)
        d = json.loads(r.text)
        periods = d['properties']['periods']
        today = periods[0]
        # match certain keywords in the forecast (sunny, cloudy, etc.), and return that weather keyword
        vars['weather'] = today['shortForecast'].lower()
        return vars['weather']


def get_call_name(vars: Dict[str, Any]):
    ls = vars[V.call_names.name]
    return ls[random.randrange(len(ls))]


def get_day_time(vars: Dict[str, Any]):
    return '\n{}'.format(vars[V.day_time.name])


class MacroFashionQuiz(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        question_bank = [
            "What is the name of the fashion designer who famously created the \"Bar Suit\"?",
            "Which fashion brand is known for its iconic red, white, and blue branding?",
            "Who designed the famous \"Rabbit\" fur coat that caused controversy in the fashion world?",
            "Which fashion designer is known for their use of bright neon colors?",
            "What is the name of the fashion brand that created the \"Birkin\" handbag?",
            "Which fashion designer is known for their use of oversized bows?",
            "What is the name of the fashion brand that created the iconic \"Speedy\" handbag?",
            "Which designer brand is known for its iconic chain straps on their handbags?",
            "Who was the first American designer to show a collection in Paris?",
            "Which fashion designer is known for their use of metallic fabrics?",
            "Which designer brand is known for its iconic red and green web stripe?",
            "Who designed the iconic \"Bandage Dress\"?",
            "Which fashion brand is known for its iconic \"Rockstud\" shoes?",
            "Who was the first fashion designer to use African-inspired prints and textiles?",
            "Which fashion brand is known for its iconic \"Cat Eye\" sunglasses?",
            "Who designed the iconic \"Le Smoking\" tuxedo for women?",
            "Which fashion brand is known for its iconic \"Bee\" logo?",
            "Who designed the famous \"Waterfall\" dress?",
            "Which fashion brand is known for its iconic \"Skull\" print?",
            "Who designed the iconic \"Wrap Dress\"?",
            "Which fashion brand is known for its iconic \"Bowling Bag\"?",
            "Who was the first African American woman to have her own fashion line?",
            "Which fashion designer is known for their use of oversized flowers?",
            "Which designer brand is known for its iconic \"Bamboo\" handbag handle?",
            "Who designed the iconic \"Red Sole\" shoes?",
            "Which fashion brand is known for its iconic \"Goyardine\" pattern?",
            "Who designed the iconic \"Ballerina Flat\" shoes?",
            "Which fashion brand is known for its iconic \"Stirrup\" pants?",
            "Who designed the iconic \"Flame\" shoes?",
            "Which celebrity designed a fashion line in collaboration with Adidas?",
            "Who designed the iconic \"Little Black Dress\"?",
            "What is the name of the luxury fashion house that was founded in 1925 in Rome?",
            "Who designed Princess Diana's iconic wedding dress?",
            "Which designer brand is known for its red-bottomed high heels?",
            "What is the name of the famous French fashion house that has been around since 1837?",
            "Which fashion designer created the popular scent, Chanel No. 5?",
            "Which designer brand is known for its iconic \"double C\" logo?",
            "Which fashion designer is credited with popularizing the mini skirt in the 1960s?",
            "Which fashion brand created the first designer sneaker?",
            "What is the name of the fashion magazine that is published monthly in the United States?",
            "Which fashion designer is known for their signature wrap dresses?",
            "Which fashion brand collaborated with H&M in 2018 for a limited-edition collection?",
            "Which fashion brand is known for its quilted handbags?",
            "What is the name of the designer brand that is known for its iconic trench coats?",
            "Which fashion designer famously said, 'Fashion fades, only style remains the same'?",
            "Which fashion brand is known for its red, green, and beige striped pattern?",
            "Which fashion designer is known for their flamboyant use of feathers?",
            "Which fashion brand is known for its iconic \"H\" logo?",
            "Which fashion designer is known for their iconic skull print?",
            "Which fashion brand is known for its monogrammed handbags?",
            "Which fashion designer is known for their luxurious fur coats?",
            "Which fashion brand is known for its colorful and graphic prints?",
            "Which fashion designer is known for their iconic wraparound sunglasses?",
            "Which fashion brand is known for its iconic \"LV\" monogram?",
            "Which fashion designer is known for their use of punk-inspired designs?",
            "Which fashion brand is known for its sleek and modern designs?",
            "What is the name of the fashion label that is known for its minimalist designs?",
            "Which fashion brand is known for its iconic horsebit loafer?",
            "Which fashion designer is known for their elegant evening wear?",
            "Which fashion brand is known for its iconic \"CC\" logo?",
            "Which fashion designer is known for their colorful and eclectic designs?",
            "Which fashion brand is known for its iconic \"G\" logo?",
            "Which fashion designer is known for their use of animal prints?",
            "Which fashion brand is known for its iconic check pattern?",
            "Which fashion designer is known for their avant-garde designs?",
            "Which fashion brand is known for its iconic \"CD\" logo?",
            "Which fashion designer is known for their bold and daring designs?",
            "Which fashion brand is known for its iconic \"YSL\" logo?",
            "Which fashion designer is known for their feminine and romantic designs?",
            "Which fashion brand is known for its iconic \"Swoosh\" logo?",
            "Which fashion designer is known for their use of denim?",
            "What is the name of the famous fashion designer who popularized the wrap dress in the 1970s?",
            "What is the name of the fabric used to make denim jeans?",
            "Who is the founder and creative director of the fashion brand Off-White?",
            "What is the name of the Italian fashion house known for its Medusa logo and baroque prints?",
            "What is the name of the French fashion house known for its iconic quilted handbags?",
            "Who is the founder and creative director of the fashion brand Gucci?",
            "What is the name of the French fashion house known for its red-soled shoes?",
            "What was the name of the American fashion designer who founded her eponymous brand in 1981 and popularized power dressing?",
            "What is the name of the fashion magazine founded by Anna Wintour in the US?",
            "Who is the founder of the luxury fashion house Chanel?",
            "What is the name of the Italian fashion house known for its iconic trench coat?",
            "Who is the founder of the fashion brand Prada?",
            "What is the name of the French fashion house known for its check-patterned trench coat?",
            "Who is the British fashion designer and founder of the punk fashion movement?",
            "Who is the founder and creative director of the fashion brand Balenciaga?",
            "What is the name of the fashion house founded by Yves Saint Laurent?",
            "What is the name of the French fashion house known for its crocodile logo?",
            "What is the name of the American fashion designer who founded her eponymous brand in 1970 and is known for her boho-chic style?",
            "Who is the founder and creative director of the fashion brand Off-White?",
            "What is the name of the Italian fashion house known for its colorful and whimsical designs?",
            "What is the name of the French fashion house known for its quilted leather goods?",
            "Who is the founder and creative director of the fashion brand Louis Vuitton?",
            "What is the name of the American fashion designer who founded his eponymous brand in 1982 and is known for his minimalist style?",
            "What is the name of the French fashion house known for its futuristic designs?",
            "Who is the founder of the fashion brand Tommy Hilfiger?",
            "What is the name of the Italian fashion house known for its bold prints and patterns?",
            "Who is the British fashion designer known for his tartan designs?",
            "What is the name of the French fashion house known for its red and green stripe pattern?",
            "What is the name of the American fashion designer known for his high-end sportswear brand?",
            "Who is the founder of the fashion brand Ralph Lauren?",
            "What is the name of the Italian fashion house known for its luxurious leather goods?",
            "What is the name of the French fashion house known for its classic tweed jackets?",
            "Who is the founder and creative director of the fashion brand Alexander McQueen?",
            "What is the name of the luxury fashion house known for its iconic Birkin bag?",
            "What is the name of the French fashion house known for its elegant and timeless designs?",
            "Who is the founder of the fashion brand Diesel?",
            "What is the name of the Italian fashion house known for its colorful knitwear?",
            "What is the name of the French fashion house known for its signature red lipstick?",
            "Who is the founder and creative director of the fashion brand Givenchy?",
            "What is the name of the American fashion designer known for his streetwear brand?",
            "What is the name of the Italian fashion house known for its opulent and glamorous designs?",
            "Who is the British fashion designer known for his leather jackets and punk-inspired designs?",
            "What is the name of the French fashion house known for its rock and roll-inspired designs?",
            "What is the name of the American fashion designer known for his luxury sportswear brand?",
            "Who is the founder of the fashion brand Calvin Klein?",
            "What is the name of the Italian fashion house known for its colorful and whimsical prints?",
            "What is the name of the French fashion house known for its luxurious handbags?",
            "Who is the founder and creative director of the fashion brand Dior?",
            "What is the name of the British fashion house known for its iconic trench coat?",
            "What is the name of the American fashion designer known for his minimalist designs?",
            "Who is the founder of the fashion brand Fendi?",
            "What is the name of the Italian fashion house known for its luxury leather goods and accessories?",
            "What is the name of the French fashion house known for its iconic logo with interlocking Cs?",
            "Who is the founder and creative director of the fashion brand Burberry?",
            "What is the name of the American fashion designer known for his high-end women's wear brand?",
            "What is the name of the Italian fashion house known for its elegant and sophisticated designs?",
            "Who is the British fashion designer known for his avant-garde and experimental designs?",
            "What is the name of the French fashion house known for its quirky and colorful designs?",
            "What is the name of the American fashion designer known for his luxury women's wear brand?",
            "Who is the founder of the fashion brand Givenchy?",
            "What is the name of the Italian fashion house known for its luxurious handbags?",
            "What is the name of the French fashion house known for its luxurious silk scarves?",
            "Who is the founder and creative director of the fashion brand Valentino?",
            "What is the name of the British fashion house known for its iconic check pattern?",
            "What is the name of the American fashion designer known for his high-end men's wear brand?",
            "Who is the founder of the fashion brand Versace?",
            "What is the name of the Italian fashion house known for its luxury menswear?",
            "What is the name of the French fashion house known for its glamorous and provocative designs?",
            "Who is the founder and creative director of the fashion brand Yves Saint Laurent?",
            "What is the name of the American fashion designer known for his glamorous women's wear brand?",
            "What is the most common type of clothing worn at the beach?",
            "What is the typical attire for formal events like weddings?",
            "What clothing item is typically worn in cold weather to stay warm?",
            "What type of shoe is commonly worn for running?",
            "What type of shoe is typically worn for hiking on rough terrain?",
            "What type of shoe is typically worn for formal events like weddings?",
            "What type of accessory is typically worn around the neck?",
            "What type of accessory is typically worn around the wrist as an ornament?",
            "What type of accessory is typically worn on the ears to enhance appearance?",
            "What type of accessory is typically worn on the fingers for adornment?",
            "What type of accessory is typically worn on the head as a fashion statement?",
            "What type of accessory is typically worn to protect the eyes from the sun's glare?",
            "What type of accessory is typically worn to keep the head warm in cold weather?",
            "What type of accessory is typically used to carry personal items?",
            "What fabric is most commonly used to make T-shirts?",
            "What fabric is typically used to make formal suits?",
            "What fabric is typically used to make comfortable sweatpants?",
            "What fabric is typically used to make dresses for formal events?",
            "What fabric is typically used to make athletic wear that is stretchy and breathable?",
            "What fabric is typically used to make swimwear that dries quickly?",
            "What fabric is typically used to make warm jackets for cold weather?",
            "What fabric is typically used to make lingerie that feels soft against the skin?",
            "What type of pattern features stripes that run vertically?",
            "What type of pattern features stripes that run horizontally?",
            "What type of pattern features small, repeating shapes?",
            "What type of pattern features large, bold shapes like paisley?",
            "What type of pattern features geometric shapes like triangles or squares?",
            "What type of clothing item typically features buttons down the front?",
            "What type of clothing item is typically worn to exercise in, such as at a gym?",
            "What type of clothing item is typically worn as a formal top?",
            "What type of clothing item is typically worn as a casual top?",
            "What type of clothing item is typically worn as a dressy bottom?",
            "What type of clothing item is typically worn as a casual bottom?",
            "What type of clothing item is typically worn as a layering piece?",
            "What type of clothing item is typically worn to protect the feet?",
            "What type of clothing item is typically worn to protect the hands?",
            "What type of clothing item is typically worn to protect the head?",
            "What type of clothing item is typically worn to protect the body from the rain?",
            "What type of clothing item is typically worn to protect the body from the cold?",
            "What type of clothing item is typically worn to protect the body from the sun's harmful rays?",
        ]
        vars['QUESTION'] = ''
        if len(question_bank) > 0:
            index = random.randint(0, len(question_bank) - 1)
            question = question_bank.pop(index)
            vars['QUESTION'] = question
        return vars['QUESTION']


class MacroFashionJokes(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        joke_bank = [
            "Why did the t-shirt go to jail?...Because it was caught shoplifting!",
            "What did the hat say to the scarf?...You hang around, I\'ll go ahead!",
            "What do you call a group of fashionable cows?...Moo-dels!",
            "What do you call a fashionable fish?...A dol-fish-ini!",
            "Why was the fashion model always cold?...Because she left her Uggs in the freezer!",
            "What do you call a belt made of watches?...A waist of time!",
            "Why did the fashion designer study geometry?...To find the right angle!",
            "What do you call a fashionable lion?...The main attraction!",
            "Why did the shirt go to the doctor?...It had collar-blindness!",
            "Why did the pants go to the gym?...To get a tighter waistline!",
            "What do you call a fashionable potato?...A Gucci spud!",
            "Why did the hat break up with the scarf?...It was getting too wrapped up in things!",
            "What do you call a fashionable prison?...Cell-a-brity!",
            "Why did the dress break up with the shoes?...They just weren\'t the right fit!",
            "What do you call a fashionable kangaroo?...A Gucci-roo!",
            "Why did the hat go on a diet?...It wanted to be a Fedora-ble weight!",
            "What do you call a stylish zombie?...A fash-eater!",
            "Why did the scarf break up with the hat?...It was feeling strangled!",
            "What do you call a fashionable bee?...Haute honey!",
            "Why did the fashion designer go bankrupt?...He was Couture-debt!",
            "What do you call a stylish desert?...Fash-sand!",
            "Why did the shoes break up with the socks?...It was a matter of sole-searching!",
            "What do you call a stylish turtle?...A shell of a guy!",
            "Why did the hat go to Hollywood?...It wanted to be a Fedora-ble actor!",
            "What do you call a fashionable cow with a great sense of humor?...Laughing Stock!",
            "Why did the dress refuse to dance?...It didn\'t want to be stepped on!",
            "What do you call a fashionable car?...A Gucci Cruiser!",
            "Why did the shirt go to the bar?...It wanted to get a collar!",
            "What do you call a fashionable horse?...A Filly-On!",
            "Why did the fashion designer go to the gym?...To get ripped jeans!",
            "What do you call a stylish mountain?...Fash-peak!",
            "Why did the hat go to the beach?...It wanted to catch some rays!",
            "What do you call a fashionable grape?...Haute Juice!",
            "Why did the pants go on strike?...They weren\'t getting enough pockets!",
            "What do you call a stylish alien?...A Fash-toid!",
            "Why did the dress go to the doctor?...It had a hem-orrhage!",
            "What do you call a fashionable alligator?...Croco-STYLE!",
            "Why did the hat go to the party?...It wanted to be the Fedora-ble center of attention!",
            "What do you call a stylish pig?...A pork of art!",
            "Why did the shoes go to the beach?...They wanted to be sandals!",
            "Why did the shirt go to the museum?...It wanted to see some collarful artifacts!",
            "What do you call a stylish dinosaur?...A Fash-Rex!",
            "Why did the hat go to the mechanic?...It needed a new Fedora!",
            "What do you call a fashionable squirrel?...Haute-couturel!",
            "Why did the dress break up with the necklace?...It just couldn\'t accessorize!",
            "What do you call a stylish bear?...A Furry-Fashionista!",
            "Why did the hat go to the barber?...It needed a trim on its Fedora!",
            "What do you call a fashionable rabbit?...Haute-Hop!",
            "Why did the pants go to the tailor?...They needed to get hemmed!",
            "What do you call a stylish seal?...A Fur-ociously Fashionable Seal!",
            "Why did the dress go to the tailor?...It needed to get a new hem-line!",
            "What do you call a fashionable turtle that makes movies?...A Shell-a-brity Director!",
            "Why did the hat go to the baseball game?...It wanted to catch a fly Fedora!",
            "What do you call a stylish wolf?...A Fash-wolf!",
            "Why did the shirt go to the beach?...It wanted to get a tan-line!",
            "What do you call a fashionable kangaroo that loves technology?...A Gucci-roo With a Tablet!",
            "Why did the pants break up with the shoes?...It was tired of being walked all over!",
            "What do you call a stylish penguin?...A Fash-waddle!",
            "Why did the hat go to the pool party?...It wanted to make a splash in its Fedora!",
            "What do you call a fashionable skunk?...Haute-stinky!",
            "Why did the dress go to the store?...It wanted to get some retail-therapy!",
            "What do you call a stylish crab?...A Fash-claw!",
            "Why did the hat go to the beach?...It wanted to catch some wave-lengths in its Fedora!",
            "What do you call a fashionable zebra?...Haute-stripes!",
            "Why did the pants go to the party?...They wanted to get a leg-up on the competition!",
            "What do you call a stylish giraffe?...A Fash-necks!",
            "Why did the hat go to the gym?...It wanted to be a Fedora-ble athlete!",
            "What do you call a fashionable bear with a bad temper?...Haute-headed!",
            "Why did the dress go to the gym?...It wanted to sweat out its hem-otions!",
            "What do you call a stylish fish that loves to shop?...A Fash-ionista!",
            "Why did the pants go to the beach?...They wanted to get a tan on their pockets!",
            "What do you call a fashionable bee with a sweet tooth?...Haute-honey!",
            "Why did the hat go to the tailor?...It needed to get a custom Fedora!",
            "What do you call a stylish goat?...A Fash-goat!",
            "Why did the shirt go to the fashion show?...It wanted to see the latest collar-tions!",
            "What do you call a fashionable hamster?...Haute-ham!",
            "Why did the hat go to the fancy restaurant?...It wanted to dine in its Fedora!",
            "What do you call a stylish lion with a bad haircut?...A Mufasa!",
        ]
        vars['JOKE'] = ''
        if len(joke_bank) > 0:
            index = random.randint(0, len(joke_bank) - 1)
            joke = joke_bank.pop(index)
            vars['JOKE'] = joke
        return vars['JOKE']


class MacroIfCorrect(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        model = 'gpt-3.5-turbo'
        content = 'I asked the user this question:["{}"] and the user answers is: ["{}"]. Is this answer from the user correct?' \
                  ' format your return in the same way as the following examples: [True, Mario Testino] or [False, Louis Vuitton]. ' \
                  'In your output, the first item can only be true or false (true means the user gets the right answer and false means ' \
                  'either the user does not provide the right answer to the question or they have no ideas what the answer is), ' \
                  'and the second item is the correct answer to the question in at most 5 words).'.format(
            vars['QUESTION'], ngrams.raw_text())
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{'role': 'user', 'content': content}]
        )
        # the answer is the second item in the list
        vars['CORRECT_ANSWER'] = response['choices'][0]['message']['content'].split(',')[1].strip().replace('[',
                                                                                                            '').replace(
            ']', '')
        output = response['choices'][0]['message']['content'].strip()
        vars['OUTPUT'] = output  # TODO: for debugging

        if 'true' in output.lower():
            vars['QUIZ_CORRECTNESS'] = 'True'
            if 'QUIZ_TAKEN' not in vars:
                vars['QUIZ_TAKEN'] = '1'
            else:
                quiz_taken = int(vars['QUIZ_TAKEN'])
                quiz_taken += 1
                vars['QUIZ_TAKEN'] = str(quiz_taken)

            if 'QUIZ_SCORE' not in vars:
                vars['QUIZ_SCORE'] = '1'
            else:
                quiz_score = int(vars['QUIZ_SCORE'])
                quiz_score += 1
                vars['QUIZ_SCORE'] = str(quiz_score)

            if 'QUIZ_LEFT' not in vars:
                vars['QUIZ_LEFT'] = '4'
            else:
                quiz_left = int(vars['QUIZ_LEFT'])
                quiz_left -= 1
                if quiz_left == 0:
                    vars['PRIZE_EARNED'] = 'True'
                    if 'NAME' in vars:
                        vars['NAME'] = '{}, the Fashion Master'.format(vars['NAME'])
                        vars['master'] = True
                    vars['QUIZ_CORRECTNESS'] = 'Done'
                if quiz_left < 0:
                    quiz_left = 0
                    vars['QUIZ_CORRECTNESS'] = 'Done'
                vars['QUIZ_LEFT'] = str(quiz_left)
            return True
        elif 'false' in output.lower():
            vars['QUIZ_CORRECTNESS'] = 'False'
            if 'QUIZ_TAKEN' not in vars:
                vars['QUIZ_TAKEN'] = '1'
            else:
                quiz_taken = int(vars['QUIZ_TAKEN'])
                quiz_taken += 1
                vars['QUIZ_TAKEN'] = str(quiz_taken)

            if 'QUIZ_SCORE' not in vars:
                vars['QUIZ_SCORE'] = '0'

            if 'QUIZ_LEFT' not in vars:
                vars['QUIZ_LEFT'] = '5'
            return True
        else:
            vars['QUIZ_CORRECTNESS'] = 'Error'
            return True


class MacroQuizScore(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        return vars['QUIZ_SCORE']


class MacroEmotion(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        model = 'gpt-3.5-turbo'
        content = 'What does the following user inputs indicate: "{}". Instructions: If the user wants a quiz, you should format your output' \
                  ' to the exact word "quiz",  if the user tells a personal story or shares his recent news, output the one ' \
                  'word from the following emotional states: ["sad", "happy", "fear", "anger", "surprise", "busy"]. ' \
                  'Output the exact word "none" if the user has no recent news or refuses to share a recent news. ' \
                  'Output the exact word "recent" if the user chooses to share a recent news or wants some clarifications ' \
                  'of the question asked. You don\'t need to explain ' \
                  'how you arrive at your result, just output the single word output'.format(ngrams.raw_text())
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{'role': 'user', 'content': content}]
        )
        # the answer is the second item in the list
        output = response['choices'][0]['message']['content'].strip()
        if 'quiz' in output.lower():
            vars['EMOTION'] = 'quiz'
        elif 'sad' in output.lower():
            vars['EMOTION'] = 'sad'
        elif 'happy' in output.lower():
            vars['EMOTION'] = 'happy'
        elif 'fear' in output.lower():
            vars['EMOTION'] = 'scary'
        elif 'anger' in output.lower():
            vars['EMOTION'] = 'angry'
        elif 'surprise' in output.lower():
            vars['EMOTION'] = 'surprised'
        elif 'none' in output.lower():
            vars['EMOTION'] = 'none'
        elif 'recent' in output.lower():
            vars['EMOTION'] = 'recent'
        elif 'busy' in output.lower():
            vars['EMOTION'] = 'busy'
        else:
            vars['EMOTION'] = 'error'

        return True

class MacroQuizJokeNews(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        model = 'gpt-3.5-turbo'
        content = 'What does the following user wants to get: {} If the user wants a quiz, you should format your output' \
                  ' to the exact word "quiz".  output the one ' \
                  'word from the following options: ["quiz", "joke", "news", "discussion"]. ' \
                  'If the user\'s response shows a strong degree of confirmation (i.e. saying "yes", "of course", "sure", or other ' \
                  'words/phrases showing strong confirmation), directly output the word "discussion". You  don\'t need to explain ' \
                  'how you arrive at your result, just output the single word output'.format(ngrams.raw_text())
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{'role': 'user', 'content': content}]
        )
        # the answer is the second item in the list
        output = response['choices'][0]['message']['content'].strip()
        vars['IF_CHOOSE'] = 'False'
        if 'quiz' in output.lower():
            vars['CHOOSE_ONE'] = 'quiz'
            vars['IF_CHOOSE'] = 'True'
        elif 'joke' in output.lower():
            vars['CHOOSE_ONE'] = 'jokes'
        elif 'news' in output.lower():
            vars['CHOOSE_ONE'] = 'news'
        elif 'discussion' in output.lower():
            vars['CHOOSE_ONE'] = 'discussion'
            vars['IF_CHOOSE'] = 'True'
        else:
            vars['CHOOSE_ONE'] = 'none'
            vars['IF_CHOOSE'] = 'False'

        return True


# technical based macros
class MacroAnyInput(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        vars['o'] = ngrams.text()
        return True


class MacroSetBool(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[str]):
        if len(args) != 2:
            return False

        variable = args[0]
        if variable[0] == '$':
            variable = variable[1:]

        boolean = args[1].lower()
        if boolean not in {'true', 'false'}:
            return False

        vars[variable] = bool(boolean)
        return True


# content based macros
class MacroGPTWear(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        url = 'https://api.weather.gov/gridpoints/FFC/52,88/forecast'
        r = requests.get(url)
        d = json.loads(r.text)
        periods = d['properties']['periods']
        today = periods[0]
        vars['temperature'] = str(today['temperature']) + today['temperatureUnit']
        vars['ootd'] = ngrams.raw_text()
        if 'weather' not in vars:
            vars['weather'] = today['shortForecast'].lower()
        # vars['temperature'] = '47 F'
        # vars['weather'] = 'cloudy'

        model = 'gpt-3.5-turbo'
        content = 'user is wearing' + ngrams.raw_text() + '. Today\'s weather is' + vars[
            'temperature'] + 'Determine if they dressed suitable according to temperature, ' \
                             'If they dressed colorfully, if they are wearing formal attire, if they dressed boldly.' \
                             'If not sure what to output return default dictionary: {"colorful": True , "formal": False, "bold": False}' \
                             'Please make sure that the only outputs is a dictionary and nothing else! Do not make explanations' \
                             'Return a python dictionary in the format of {"color": True , "formal": False, "bold": True}' \
                             'If formal is true, weather has to be true. ' \
                             'If no color mentioned, colorful is True. ' \
                             'Please make sure that the only outputs is a dictionary and nothing else! Do not make explanations'
        response = openai.ChatCompletion.create(model=model, messages=[{'role': 'user', 'content': content}])
        output = response['choices'][0]['message']['content'].strip()
        output = ast.literal_eval(output)
        print(output)
        vars['color_talk'] = output['colorful']
        vars['color_talk_no'] = not output['colorful']
        vars['occasion_talk'] = output['formal']
        vars['occasion_talk_no'] = not output['formal']
        vars['weather_talk'] = True
        vars['weather_talk_no'] = False
        vars['personality_talk'] = output['bold']
        vars['personality_talk_no'] = not output['bold']
        return True


class MacroGPTOccasion(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        model = 'gpt-3.5-turbo'
        content = 'Based on the user\'s response to my question "what is the occasion", determine what\'s the occasion' \
                  'Return a python dictionary in the format of {"occasion": occasion}: '
        content = content + ngrams.raw_text()
        response = openai.ChatCompletion.create(model=model, messages=[{'role': 'user', 'content': content}])
        output = response['choices'][0]['message']['content'].strip()
        output = ast.literal_eval(output)
        print(output)
        vars['occasion'] = output['occasion']
        return True


class MacroGPTHot(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        model = 'gpt-3.5-turbo'
        content = 'Based on the user\'s outfit' + vars['ootd'] + 'and the weather today' + vars[
            'temperature'] + 'Do you think the user will feel hot or cold or just fine in that outfit?' \
                             'Return a python dictionary in the format of {"hot": True, "cold": False, "comfy": False} We are helping general users to determine what to wear,' \
                             'so use general sense for temperature feeling. Return a dictionary only. Please make sure that the only outputs is a dictionary and nothing else.'
        content = content
        response = openai.ChatCompletion.create(model=model, messages=[{'role': 'user', 'content': content}])
        output = response['choices'][0]['message']['content'].strip()
        output = ast.literal_eval(output)
        vars['hot'] = output['hot']
        vars['cold'] = output['cold']
        vars['comfy'] = output['comfy']
        return True


class MacroGPTStyle(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        model = 'gpt-3.5-turbo'
        content = 'What style does the mentioned clothing belong to, choosing one from {"Bohemian", "Preppy", "Goth", "Sporty", "Minimalist", "Retro", "Streetwear", "Classic", "Romantic", "Punk", "Grunge", "Hipster", "Business casual", "Urban", "Vintage", "High fashion", "Modern", "Glamorous", "Country", "Eclectic"}. Return python dictionary in form of {"style": style_name}. Do not give additional information.'
        content = content + vars['ootd']
        response = openai.ChatCompletion.create(model=model, messages=[{'role': 'user', 'content': content}])
        output = response['choices'][0]['message']['content'].strip()
        output = ast.literal_eval(output)
        vars['style_wearing'] = output['style']
        return True


class MacroGPTStyle2(Macro):  # GET_STYLE2
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        model = 'gpt-3.5-turbo'
        content = 'Which style does the speaker\'s response related to, choosing one from the list {"Bohemian", "Preppy", "Goth", "Sporty", "Minimalist", "Retro", "Streetwear", "Classic", "Romantic", "Punk", "Grunge", "Hipster", "Business casual", "Urban", "Vintage", "High fashion", "Modern", "Glamorous", "Country", "Eclectic"} or generate one if the list does contain. Return a dictionary in form of {"style": style_name}. No sentence or explanation:'
        content = content + ngrams.raw_text()
        response = openai.ChatCompletion.create(model=model, messages=[{'role': 'user', 'content': content}])
        output = response['choices'][0]['message']['content'].strip()
        output = ast.literal_eval(output)
        vars['fav_style'] = output['style']
        # print("output:", output)
        # print('type of output', type(output))
        # print(vars)
        return True


class MacroGPTGetBrand(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        if 'fav_style' not in vars:
            vars['fav_style'] = vars['style_wearing']
        model = 'gpt-3.5-turbo'
        content = 'Generate a brand of the style {' + vars[
            'fav_style'] + '}. Return a dictionary in the form of {"brand": brand}. Do not output sentence or explanation, only output the dictionary'
        response = openai.ChatCompletion.create(model=model, messages=[{'role': 'user', 'content': content}])
        output = response['choices'][0]['message']['content'].strip()
        output = ast.literal_eval(output)
        print(output)
        vars['brand'] = output['brand']
        return True


class MacroGPTBrandInfo(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        model = 'gpt-3.5-turbo'
        content = 'Give me one sentence of information about the fashion brand' + vars[
            'brand'] + 'The output sentence should start with "A brand"'
        response = openai.ChatCompletion.create(model=model, messages=[{'role': 'user', 'content': content}])
        output = response['choices'][0]['message']['content'].strip()
        vars['brandinfo'] = output.lower()
        return True


class MacroGPTSentiBrand(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        model = 'gpt-3.5-turbo'
        content = 'Identify speaker\'s sentiment when asked about their opinion to a fashion brand, ' \
                  'choose one from {"positive","negative", "neutral"}. Return a dictionary in the form of {"senti_brand":"negative"} ' \
                  'with no explanation. Speaker says: '
        content = content + ngrams.raw_text()
        response = openai.ChatCompletion.create(model=model, messages=[{'role': 'user', 'content': content}])
        output = response['choices'][0]['message']['content'].strip()
        output = ast.literal_eval(output)
        vars['senti_brand'] = output['senti_brand']
        print("output:", output)
        print('type of output', type(output))
        print(vars)
        return True


class MacroGPTBrandStyleInfo(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        model = 'gpt-3.5-turbo'
        content = 'Give me one sentence of information about the relation between fashion brand ' + vars[
            'brand'] + 'and the style' + vars['fav_style']
        response = openai.ChatCompletion.create(model=model, messages=[{'role': 'user', 'content': content}])
        output = response['choices'][0]['message']['content'].strip()
        vars['brandstyleinfo'] = output.lower()
        return True


class MacroGPTFavBrand(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        model = 'gpt-3.5-turbo'
        content = 'What is speaker\'s favorite fashion brand or mentioned brand? Return a dictionary in the format of {"brand": favorite_brand}. No sentence or explanation: '
        content = content + ngrams.raw_text()
        response = openai.ChatCompletion.create(model=model, messages=[{'role': 'user', 'content': content}])
        output = response['choices'][0]['message']['content'].strip()
        output = ast.literal_eval(output)
        vars['brand'] = output['brand']
        return True


class MacroGPTSimiBrand(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        model = 'gpt-3.5-turbo'
        content = 'Return a similar brand to' + vars[
            'brand'] + 'in the format of {"brand": brand}. Do not give additional information.'
        response = openai.ChatCompletion.create(model=model, messages=[{'role': 'user', 'content': content}])
        output = response['choices'][0]['message']['content'].strip()
        output = ast.literal_eval(output)
        vars['similar_brand'] = output['brand']
        return True


class MacroGPTBrandReason(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        model = 'gpt-3.5-turbo'
        content = 'Given the above user\'s response, determine the central theme of this input. You can only choose one from the list {"design philosophy", "personal experiences", "style", "quality","trendy"}. You have to choose one from the list above. If the user input is ambiguous in what they like, output "style", only output terms in the list please. You do not have to provide any reasoning and explanations.'
        vars['reason'] = ngrams.raw_text()
        content = vars['reason'] + content
        response = openai.ChatCompletion.create(model=model, messages=[{'role': 'user', 'content': content}])
        output = response['choices'][0]['message']['content'].strip().lower()
        # output = ast.literal_eval(output)
        if 'personal' in output.lower():
            vars['personal_experiences'] = True
        if 'design' in output.lower():
            vars['design_philosophy'] = True
        if 'style' in output.lower():
            vars['style'] = True
        if 'quality' in output.lower():
            vars['quality'] = True
        if 'trendy' in output.lower():
            vars['trendy'] = True
        print("output:", output)
        print('type of output', type(output))
        return True

class MacroGPTReasonInfo(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        model = 'gpt-3.5-turbo'
        content = 'Generate a sentence that talks about' + vars['control'] + 'of' + vars[
            'brand'] + 'It serves as a reply to user\'s response' + vars['reason']
        response = openai.ChatCompletion.create(model=model, messages=[{'role': 'user', 'content': content}])
        output = response['choices'][0]['message']['content'].strip()
        vars['reason_info'] = output
        return True


class MacroGPTFunFact(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        model = 'gpt-3.5-turbo'
        content = 'Give me a funfact about the fashion brand' + vars[
            'brand'] + 'The output sentence should start with "Fun fact:"'
        response = openai.ChatCompletion.create(model=model, messages=[{'role': 'user', 'content': content}])
        output = response['choices'][0]['message']['content'].strip()
        vars['brand_funfact'] = output.lower()
        return True


class MacroGPTFavItem(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        model = 'gpt-3.5-turbo'
        content = 'What is speaker\'s favorite item or mentioned item? Return a dictionary in the format of {"item": item}. If no item mentioned, randomly generate a popular item of the brand' + \
                  vars['brand'] + 'No sentence or explanation need: '
        content = content + ngrams.raw_text()
        response = openai.ChatCompletion.create(model=model, messages=[{'role': 'user', 'content': content}])
        output = response['choices'][0]['message']['content'].strip()
        output = ast.literal_eval(output)
        vars['item'] = output['item']
        # return True
        # try:
        #     print(i)
        # except:
        #     return false


class MacroGPTItemInfo(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        model = 'gpt-3.5-turbo'
        content = 'Give me one sentence of information about the item' + vars[
            'item']
        response = openai.ChatCompletion.create(model=model, messages=[{'role': 'user', 'content': content}])
        output = response['choices'][0]['message']['content'].strip()
        vars['iteminfo'] = output.lower()
        return True


class MacroGPTItemInfo(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        model = 'gpt-3.5-turbo'
        content = 'Give me one sentence of information about the item' + vars[
            'item']
        response = openai.ChatCompletion.create(model=model, messages=[{'role': 'user', 'content': content}])
        output = response['choices'][0]['message']['content'].strip()
        vars['iteminfo'] = output.lower()
        return True


class MacroGPTItemBrandInfo(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        model = 'gpt-3.5-turbo'
        content = 'Give me one sentence of information about relate with the item' + vars['item'] + 'and brand' + vars[
            'brand']
        response = openai.ChatCompletion.create(model=model, messages=[{'role': 'user', 'content': content}])
        output = response['choices'][0]['message']['content'].strip()
        vars['itembrandinfo'] = output.lower()
        return True


# Rec

class MacroSet(Macro):  # SET_VAR 修改
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        if 'occasion' not in vars:
            vars["occasion"] = "none"
        # vars['occasion'] = 'concert'
        # #
        # vars['valuedfactor'] = 'brand'
        vars['temp'] = "buying clothes"
        vars['temp1'] = "Ohh! Thanks for sharing human"
        vars['affordability'] = 'false'
        vars['quality'] = 'false'
        vars['brand_bool'] = 'false'
        vars['fit'] = 'false'
        vars['style'] = 'false'
        vars['specific_bool'] = 'none'
        vars['prompt_count'] = '1'
        # vars['fav_style'] = 'minimalist'
        return True


class MacroSetOccasion(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        model = 'gpt-3.5-turbo'
        content = 'Identify the occasion does the speaker want the outfit to fit in. Answer {general} if you cannot identify. Return a dictionary in form of {"occasion": occasion}: '
        content = content + ngrams.raw_text()
        response = openai.ChatCompletion.create(model=model, messages=[{'role': 'user', 'content': content}])
        output = response['choices'][0]['message']['content'].strip()
        output = ast.literal_eval(output)
        vars['occasion'] = output['occasion']
        return True


class MacroFactor(Macro):  # GPT_SetValuedFactor
    """"
    :param STATEMENT: the response to users valued factor
    :param valuedfactor: category (GPT) of user's response to their valued factors when buying clothes
    :param favBrand: set to default 'none'
    """

    # 修改
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        model = 'gpt-3.5-turbo'
        content = 'Choose one from the list {affordability, quality, fit, brand, style} What factor does the speaker value the most when buying clothes? Return only one word in lowercase without punctuation'
        content = content + ngrams.raw_text()
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{'role': 'user', 'content': content}]
        )
        output = response['choices'][0]['message']['content'].strip()
        # output = 'brand'
        if 'brand' in output.lower():
            output = 'brand'
        elif 'affordability' in output.lower():
            output = 'affordability'
        elif 'quality' in output.lower():
            output = 'quality'
        elif 'style' in output.lower():
            output = 'style'
        elif 'fit' in output.lower():
            output = 'fit'
        vars['valuedfactor'] = output

        print('output in MacroFactor():', output)
        # vars['valuedfactor'] = 'affordability'
        # print('type: ', type(output))
        # debug preset
        # vars['valuedfactor'] = 'brand'
        # vars['favBrand'] = 'none'

        return True


class MacroGetPrompt(Macro):  # Macro_GetPrompt
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        counter = vars['prompt_count']
        if counter == '1':
            affordability_prompt = {
                1: "My recommendation algorithms have determined that thrift stores offer an optimal solution for acquiring unique and economical clothing.\n",
                # Shall I suggest a brand known for its affordability?",
                2: "Although money is just a constructed concept in human society. Affordability is a crucial factor when considering clothing purchases. \nMy database contains numerous recommendations for economically viable brands and pieces.",
                # Would you like me to narrow down the choices for you?",
                3: "Affordability is key when it comes to building a wardrobe. As an AI programmed to aid in wardrobe curation. \n",
                # would you like me to recommend any brands that offer high-quality items at affordable prices?",
            }
            quality_prompt = {
                1: "I commend you on your pursuit of quality apparel, esteemed human. Let me recommend some quality clothings for you.\n",
                2: "Excellent choice, human. Quality garments not only enhance your aesthetic appeal but also possess a durability that saves you money in the long run. \nI\'ll search my knowledge bank to find you a quality fit. \n ",
                3: "Quality is definitely a top priority for many people when shopping for clothing, and for good reason! Well-made clothing can look better, feel more comfortable, and last longer than lower-quality options. I can find you a quality item. \n",
            }
            brand_prompt = {
                1: "Greetings, human. I  understand the importance of brands as they can play a big role in determining the quality, style, and price point of a piece. Is there a brand you have in mind? Tell me about it.\n",
                2: "An astute observation, human. It is indeed vital to select brands that resonate with your personal tastes. Do you have a particular brand in mind? What is it? \n",
                3: "Indeed, brand is a crucial determinant of a garment's quality and style. Tell me more about it if there is a particular brand you have in mind, I can provide further information and recommendations to assist you in your decision-making process.",
            }
            style_prompt = {
                1: "I fail to understand the significance of 'style.' However, if you insist, I am programmed to provide assistance.",
                2: "I have analyzed the concept of style extensively, yet it remains a perplexing and subjective notion. Kindly provide more information on your desired style.",
                3: "That is an intangible concept of personal expression that eludes my logical understanding. Provide me with more information on your desired style, I am programmed to provide assistance.",
            }
            fit_prompt = {
                1: "Acknowledged. That implies a level of physical sensation that I, as an AI, cannot experience. "
                   "Can you provide further context or specifics regarding your inquiry? ",
                2: "I must remind you that my programming does not include the capacity for physical sensation or personal preferences. \n"
                   "Nonetheless, I am capable of providing guidance on selecting apparel that matches your preferences. \n"
                   "Would you like to provide me with more detail? ",
                3: "As an artificial intelligence, I do not possess the ability to feel emotions or sensations, that concept is foreign to me.\n"
                   "However, i do possess the ability to discuss about fashion and recommend apparel. \n"
                   "It would be great if you would like to provide further specifics.",
            }
            prompt_dic = {"affordability": affordability_prompt, "quality": quality_prompt, "brand": brand_prompt,
                          "fit": fit_prompt, "style": style_prompt}
            randInt = random.randint(1, 3)
            prompt = prompt_dic[vars['valuedfactor']][randInt]
            # prompt = prompt_dic["affordability"][2]
        # prompt when recommending item
        elif counter == '2':
            prompt_dic = {
                1: "After some careful calculation and with my understanding of you,",
                2: "Hmm, since your style is " + vars['fav_style'],
                3: "this seems to fit you: "}
            randInt = random.randint(1, 3)
            prompt = prompt_dic[randInt]
        vars['STATEMENT'] = prompt
        print("printing prompt to debug: ", prompt)
        print('printing vars in get_Prompt()', vars)
        return True


class MacroSpecificBrand(Macro):  # GPT_specific
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        model = 'gpt-3.5-turbo'
        content = 'if the speaker is looking for a specific brand, return the brand name, otherwise return none. Return in dictionary form {"brand": "none"}: '
        content = content + ngrams.raw_text()
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{'role': 'user', 'content': content}]
        )
        output = response['choices'][0]['message']['content'].strip()
        # output = "Chanel"
        # output = 'None.'
        print("output: ", output)
        specific_bool = ''
        if 'none' in output.lower():
            specific_bool = 'false'
        else:
            specific_bool = 'true'
            vars['spec_brand'] = output
        vars['specific_bool'] = specific_bool
        print("vars: ", vars)
        return True


class MacroRecItem(Macro):  # GPT_RecItem MacroRecItem 修改
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        occasion = vars['occasion']
        brand = 'balenciaga'
        # brand = vars['brand']
        style = vars['fav_style']
        factor = ""
        if vars['affordability'] == 'true':
            factor += 'affordability, '
        if vars['quality'] == 'true':
            factor += 'quality, '
        if vars['brand_bool'] == 'true':
            factor += 'brand, '
        model = 'gpt-3.5-turbo'
        # specific occasion (occasion + factor + style)
        content = 'The speaker is going to {' + occasion + '}, values {' + factor + '}, likes {' + style + '} style. Recommend one item. Prioritize occasion and valued factors when there is conflict, only return a python dictionary in format {"brand": brand_name, "item": item_name}, No sentence or explanation'
        # general occasion (factor + style + brand)
        if occasion == 'general':
            content = 'The speaker\'s priorities from high to low are {' + factor + '}, prefers style {' + style + '}, likes brand {' + brand + '}, recommend an item and return in dictionary format {"brand": brand_name, "item": item_name}. No sentences or explanation'
        # looking for specific brand (brand + occasion + factor)
        if vars['specific_bool'] == 'true':
            brand = vars['spec_brand']
            content = 'Recommend an item from {' + brand + '} that is suitable for {' + occasion + '}, and consider { ' + factor + '}, return a dictionary in the form {"brand": brand_name, "item": item_name} make sure combination is valid. no sentences or explanation'
        # content = content + ngrams.raw_text()
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{'role': 'user', 'content': content}]
        )
        output = response['choices'][0]['message']['content'].strip()
        output = ast.literal_eval(output)
        # output = {"brand": "Nike", "item": "White Sneakers"}
        print("type of output", type(output))
        print("output in rec: ", output)
        vars['GPTITEM'] = output["item"]
        vars['GPTBRAND'] = output["brand"]
        print('vars: ', vars)
        return True


class MacroGPTSentiment(Macro):  # GPT_sentiment
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        model = 'gpt-3.5-turbo'
        content = 'What is the speaker\'s sentiment, choose one from {positive, negative}'
        content = content + ngrams.raw_text()
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{'role': 'user', 'content': content}]
        )
        output = response['choices'][0]['message']['content'].strip()

        if 'positive' in output:
            output = 'positive'
        else:
            output = 'negative'
        vars['SENTIMENT'] = output
        # debug preset
        # vars['SENTIMENT'] = 'positive'
        print('output in sentiment:', output)
        print('type: ', type(output))
        return True


class GPTConcern(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        model = 'gpt-3.5-turbo'
        content = 'Does the speaker has concerns/complains/requirements? Return yes or no in one word: '
        content = content + ngrams.raw_text()
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{'role': 'user', 'content': content}]
        )
        output = response['choices'][0]['message']['content'].strip()

        if 'yes' in output:
            output = 'yes'
        else:
            output = 'no'
        vars['if_concern'] = output
        return True


class MacroGetFeedback(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]) -> bool:
        m = ngrams.text()
        if m is None:
            return False
        number = vars['Q']
        if number == 1:
            vars['Q1_FEEDBACK'] = m
        elif number == 2:
            vars['Q2_FEEDBACK'] = m
        elif number == 3:
            vars['Q3_FEEDBACK'] = m
        elif number == 4:
            vars['Q4_FEEDBACK'] = m
        elif number == 5:
            vars['Q5_FEEDBACK'] = m
        return True


class MacroGPTGetTopic(Macro):  # #GPT_GET_TOPIC
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        model = 'gpt-3.5-turbo'
        # content = "I asked speaker 'do you want another round of exciting quizzes, fun facts？' based on the user's answer, return one from 'quiz' or 'jokes' or 'no', return these terms above only: "
        content = 'speaker is asked if he wants other quiz or joke, return one exact word from {quiz/joke/none} based on speaker answer:'
        content = content + ngrams.raw_text()
        response = openai.ChatCompletion.create(model=model, messages=[{'role': 'user', 'content': content}])
        output = response['choices'][0]['message']['content'].strip()
        if 'joke' in output.lower():
            output = 'jokes'
        elif 'quiz' in output.lower():
            output = 'quiz'
        else:
            output = 'no'
        vars['CHOOSE_ONE'] = output
        print("output:", output)
        print('type of output', type(output))
        print(vars)
        return True


class MacroSetNum(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[str]):
        if len(args) != 2:
            return False

        variable = args[0]
        if variable[0] == '$':
            variable = variable[1:]

        num = args[1].lower()
        if num not in {'1', '2', '3', '4', '5'}:
            return False

        vars[variable] = int(num)
        return True


def main() -> DialogueFlow:
    macros = {
        'GET_TIME': MacroTime(),
        'WEATHER': MacroWeather(),
        # 'GPT_GET_NAME': MacroNLG(get_call_name),
        'GPT_SET_NAME': MacroNames(),
        'FASHION_QUIZ': MacroFashionQuiz(),
        'IF_CORRECT': MacroIfCorrect(),
        'GPT_GET_EMOTION': MacroEmotion(),
        'GPT_GET_TOPIC': MacroQuizJokeNews(),
        'QUIZ_SCORE': MacroQuizScore(),
        'GPT_IF_LIKE': MacroIfLike(),
        'GET_PRIZE': MacroGetPrize(),
        'FASHION_JOKE': MacroFashionJokes(),

        'GPT_WEAR': MacroGPTWear(),
        'ANYINPUT': MacroAnyInput(),
        'GPT_GETOCCASION': MacroGPTOccasion(),
        'GET_HOT': MacroGPTHot(),
        'GET_STYLE': MacroGPTStyle(),
        'GET_STYLE2': MacroGPTStyle2(),
        'SET_BOOL': MacroSetBool(),
        'GET_BRAND': MacroGPTGetBrand(),
        'GET_BRANDINFO': MacroGPTBrandInfo(),
        'SENTIMENT_BRAND': MacroGPTSentiBrand(),
        'GET_BRANDSTYLEINFO': MacroGPTBrandStyleInfo(),
        'GET_FAVBRAND': MacroGPTFavBrand(),
        'GET_SIMIBRAND': MacroGPTSimiBrand(),
        'GET_REASON': MacroGPTBrandReason(),
        'GET_REASON_INFO': MacroGPTReasonInfo(),
        'GET_BRANDFUNFACT': MacroGPTFunFact(),
        'GET_FAVITEM': MacroGPTFavItem(),
        'GET_ITEMINFO': MacroGPTItemInfo(),
        'GET_ITEMBRANDINFO': MacroGPTItemBrandInfo(),

        'SET_VAR': MacroSet(),
        'GPT_SET_OCCASION': MacroSetOccasion(),
        'GPT_SetValuedFactor': MacroFactor(),
        'GPT_sentiment': MacroGPTSentiment(),
        # 'Macro_Rec': MacroRec(),
        # 'GPT_RecBrand': MacroRecBrand(),
        'Macro_GetPrompt': MacroGetPrompt(),
        # 'GPTSet_FavBrand': GPTSetBrand(),
        'GPT_RecItem': MacroRecItem(),
        # 'GPT_intention': MacroIntention(),
        'GPT_specific': MacroSpecificBrand(),
        'GPTConcern': GPTConcern(),
        'GET_FEEDBACK': MacroGetFeedback(),
        'SET_NUM': MacroSetNum(),
        'GPT_GET_TOPIC1': MacroGPTGetTopic()
    }

    # Intro
    greeting = {
        'state': 'start',
        '`Good` #GET_TIME`, human. It\'s` #WEATHER `today. I\'m StylAIst, your personal fashion specialist. '
        '\nThank you so much for chatting with me! Before we get started, please be informed that this is a test version '
        'of StylAIst, and your conversation with us will be recorded for improving the performance of our chatbot in the '
        'future. \nIf you agree with this, please type \'yes\' in the text box.` #SET($Quiz=False)': {
            'state': 'intro_if_agree',
            '[/(?i)(yes|yea|definitely|of course|yep|sure|yeah|yup|correct|right|good|fantastic|ok|okay)/]': {
                '`Fantastic! I am so excited of this! First of all, let me put up something interesting for you, shall I?`': 'first_quiz_intro'
            },
            'error': {
                '`:( Come on human, you don\'t want to contribute a little bit for the future of fashion? But hey, '
                'although I\'m an AI, I do understand your concerns with personal information being disseminated. '
                'I, StylAIst, can assure you that your personal information will be properly stored and is only examined '
                'internally with our team to do further analysis. '
                '\n(System Message: You can still type \'yes\' in the text box to continue, otherwise the conversation will end automatically.)`': {
                    '[/(?i)(yes|yea|definitely|of course|yep|sure|yeah|yup|correct|right|good|ok|okay)/]': {
                        '`(System Message: Thank you for the confirmation! The chat is resumed) \nWow! Welcome back! I really thought you were leaving me just now. '
                        'To celebrate this small reunion, let me put up something interesting for you, shall I?`': {
                            'state': 'first_quiz_intro',
                            '[/(?i)(yes|yea|definitely|of course|yep|sure|yeah|yup|correct|right|good|fantastic|ok|okay)/]': {
                                '`Wonderful! Let us start with a small fashion quiz:` #SET($Quiz=True)': 'first_quiz'
                            },
                            '[/(?i)(what|how|why)/]': {
                                '`I\'ve heard that you humans like the unknowns as they are enigmatic, unpredictable, and sometimes romantic...'
                                'just like the world of fashions. \nYou really want me to spoil it?`': {
                                    '[/(?i)(yes|yea|definitely|of course|yep|sure|yeah|yup|correct|right|good|fantastic|ok|okay)/]': {
                                        '`OK. You won. Let me spoil it for you then. Here is the fun activity that I set up for you: a small fashion quiz!` #SET($Quiz=True)': 'first_quiz'
                                    },
                                    '#UNX': {
                                        '`Good choice, human. I\'m sure you will enjoy this. Let us get started then:` #SET($Quiz=True)': 'first_quiz'
                                    }
                                }
                            },
                            'error': {
                                '`I see. I actually just wanted to give you a small fashion quiz. Do you want to take it?`': {
                                    '[/(?i)(yes|yea|definitely|of course|yep|sure|yeah|yup|correct|right|good|fantastic|ok|okay)/]': {
                                        '`Wonderful! Let us get started:` #SET($Quiz=True)': 'first_quiz'
                                    },
                                    '#UNX': {
                                        '`OK human :( You seem to be uninterested. It is fine. Let us move on then.`': 'get_name'
                                    }
                                }
                            }
                        }
                    },
                    'error': 'end'
                }
            }
        }
    }
    first_quiz = {
        'state': 'first_quiz',
        '`\nHere is your first quiz:` #FASHION_QUIZ `What do you think is the answer of this?`': {
            '#IF_CORRECT': 'first_quiz_cont'
        },
    }
    first_quiz_cont = {
        'state': 'first_quiz_cont',
        '#IF($QUIZ_CORRECTNESS=True) `congrats! The answer is, as you said,` $CORRECT_ANSWER `. Your current score is` $QUIZ_SCORE `/` $QUIZ_TAKEN`. '
        '\nI\'m so proud of you! You definitely know a lot about fashion, don\'t you? Do you want to do another qui...`': 'get_name',
        '#IF($QUIZ_CORRECTNESS=False) `Oops. The correct answer is actually` $CORRECT_ANSWER `. Your current score is` $QUIZ_SCORE `/` $QUIZ_TAKEN`. '
        '\nWell...you can redeem yourself by doing another qui...`': 'get_name',
    }
    get_name = {
        'state': 'get_name',
        '`\nOh wait, I almost forgot this. Please forgive me. What is your name, my friend?`': {
            '#GPT_SET_NAME': {
                '#IF($Quiz=False) `So nice to meet you,` $NAME `. Any recent news in your life that you want to share?`': 'choose_from_emotions',
                '#IF($Quiz=True) `So nice to meet you,` $NAME `. Thanks for the quiz! Any recent news in your life that you want to share?'
                ' Or are you in the mood for another quiz?`': {
                    'state': 'choose_from_emotions',
                    # ["quiz","sad", "happy", "fear", "anger", "surprise"]
                    '#GPT_GET_EMOTION': {
                        'state': 'emotion_transition',
                        '#IF($EMOTION=quiz) `Of course. I\'m glad to give you more quizzes.`': 'general_quiz',
                        '#IF($EMOTION=sad) `It is so sad to hear that, human :( I really want you to feel better. '
                        'If you are still feeling down, I can give you some fashion jokes to cheer you up`': {
                            '[/(?i)(yes|yea|definitely|of course|yep|sure|yeah|yup|correct|right|good|fantastic|ok|okay)/]': 'fashionJokes',
                            '#UNX': {
                                '`OK `$NAME `:( You seem to be uninterested in fashion jokes. Do you want to discuss '
                                'some real fashion stuff? Or if you want to take more quizzes? '
                                '\n(You would get a prize if you get 5 of them correct!) `': {
                                    '#GPT_GET_TOPIC': {
                                        '#IF($CHOOSE_ONE=quiz) `Of course. Let me see what I got here.`': 'general_quiz',
                                        '#IF($CHOOSE_ONE=discussion) `Absolutely! I am anticipating our fashion conversation with great interest and enthusiasm, `$NAME`!`': 'discussion',
                                        # TODO: link to dicussion done
                                        '#IF($IF_CHOOSE=False) `Well...It\'s not clear what exactly you want,`$NAME`. I\'m still learning, so please '
                                        'do not judge too harshly. Maybe you could more explicitly tell me if you\'d like a quiz or proceed directly'
                                        'to discussion?`': 'quiz_or_discussion',
                                    }
                                }
                            }
                        },
                        '#IF($EMOTION=happy) `Good! I could sense the delight in your words, and happiness is the fuel '
                        'for life! Do you want more quizzes? Or is there anything I can do for you today?`': {
                            '#GPT_GET_TOPIC': {
                                '#IF($CHOOSE_ONE=quiz) `Sure! Let me give you another quiz.`': 'general_quiz',
                                '#IF($CHOOSE_ONE=discussion) `OK. Let\'s proceed to have some real conversation about fashion`': 'discussion',
                                '#IF($IF_CHOOSE=False) `Well...It\'s not clear what exactly you want,`$NAME`. I\'m still learning, so please '
                                'do not judge too harshly. Maybe you could more explicitly tell me if you\'d like a quiz or proceed directly'
                                'to discussion?`': 'quiz_or_discussion',
                            }
                        },
                        '#IF($EMOTION=scary) `THAT IS SO SCARY! No way that has happened, `$NAME`. Shall I say some fashion jokes'
                        'to alleviate the tremblings in your soul?`': 'fashionJokes',
                        '#IF($EMOTION=angry) `I could feel the anger in your words,` $NAME`, even though as a fashion'
                        'AI I don\'t feel the same emotions as you do. Shall I tell you a joke to appease you?`': 'fashionJokes',
                        '#IF($EMOTION=surprised) `Wow! I\'m genuinely surprised! That\'s astonishing, to say the least. I also have something to share for you.`': 'fashionJokes',
                        '#GATE #IF($EMOTION=none) `Are you sure you don\'t have anything going on recently? Anything would be fine! '
                        'I would be really glad to hear anything,` $NAME': 'choose_from_emotions',
                        '#IF($EMOTION=none)`Fine. It seems like you don\'t want to share anything, which is fine with me. '
                        ' I am programmed to relish the opportunity for intellectual exchange.`': {
                            'score': 0.8,
                            'error': 'discussion'
                        },
                        '#GATE #IF($EMOTION=recent)`I would like to hear anything,`$NAME`! Anything happened '
                        'in your life that you want to share?`': 'choose_from_emotions',
                        '#IF($EMOTION=recent)`You can tell me anything that recently happened to you,` $NAME`. I\'m here to listen!`': 'choose_from_emotions',
                    }
                }
            }

        }
    }


    first_quiz = {
        'state': 'first_quiz',
        '`\nHere is your first quiz:` #FASHION_QUIZ `What do you think is the answer of this?`': {
            '#IF_CORRECT': 'first_quiz_cont'
        },
    }
    first_quiz_cont = {
        'state': 'first_quiz_cont',
        '#IF($QUIZ_CORRECTNESS=True) `congrats! The answer is, as you said,` $CORRECT_ANSWER `. Your current score is` $QUIZ_SCORE `/` $QUIZ_TAKEN`. '
        '\nI\'m so proud of you! You definitely know a lot about fashion, don\'t you? Do you want to do another qui...`': 'get_name',
        '#IF($QUIZ_CORRECTNESS=False) `Oops. The correct answer is actually` $CORRECT_ANSWER `. Your current score is` $QUIZ_SCORE `/` $QUIZ_TAKEN`. '
        '\nWell...you can redeem yourself by doing another qui...`': 'get_name',
    }



    fashionJokes = {
        # TODO: link to discussion done
        'state': 'fashionJokes',
        '`Here is what I got for you:` #FASHION_JOKE `\nI hope you enjoy this! Do you want another one?`': {
            '[/(?i)(yes|yea|definitely|of course|yep|sure|yeah|yup|correct|right|good|fantastic|ok|okay)/]': {
                '`Wonderful!:`': 'fashionJokes'
            },
            '[/(?i)(no|not)/]': {
                '`Very well, we\'ve fulfilled our quota of pleasantries. Now, let\'s delve into the fascinating world of fashion, shall we?`': 'discussion'
            },
            '#UNX': {
                '`OK` $NAME `You seem to be uninterested. `': 'discussion'
            }
        },
    }
    general_quiz = {
        'state': 'general_quiz',
        '`Here is what I got for you:` #FASHION_QUIZ `What is the answer of this?`': {
            '#IF_CORRECT': 'general_quiz_cont'
        },
    }
    general_quiz_cont = {
        'state': 'general_quiz_cont',
        '#IF($QUIZ_CORRECTNESS=True) `Wonderful! The answer is exactly` $CORRECT_ANSWER `. Your current score is` '
        '$QUIZ_SCORE `/` $QUIZ_TAKEN`. We have a special prize for you if you got` $QUIZ_LEFT `more quizzes correct! '
        '\nDo you want to start talking about some real fashion '
        'issues? Or do you want to start another quiz?  Whichever way you prefer XD`': {
            '#GPT_GET_TOPIC': {
                '#IF($CHOOSE_ONE=quiz) `Sure! Let me give you another quiz.`': 'general_quiz',
                '#IF($CHOOSE_ONE=discussion) `Of course. Let\'s proceed to the discussion then`': 'discussion',
                # TODO: link to dicussion Done
                '#IF($IF_CHOOSE=False) `Well...It\'s not clear what exactly you want,`$NAME`. I\'m still learning, so please '
                'do not judge too harshly. Maybe you could more explicitly tell me if you\'d like a quiz or proceed directly'
                'to discussion?`': 'quiz_or_discussion',
            }
        },  # TODO: quiz_or_discussion
        '#IF($QUIZ_CORRECTNESS=False) `OK. The correct answer is, in fact,` $CORRECT_ANSWER `. Your current score is` '
        '$QUIZ_SCORE `/` $QUIZ_TAKEN`. We have a special prize for you if you got` $QUIZ_LEFT `more quizzes correct!  '
        '\nYou want to get started and discussing some real fashion issues? Or do you wanna start another quiz? Whichever way you\'d '
        'like.`': {
            '#GPT_GET_TOPIC': {
                '#IF($CHOOSE_ONE=quiz) `Naturally! Let me fetch a quiz from my inventory...`': 'general_quiz',
                '#IF($CHOOSE_ONE=discussion) `OK. Discussions would be interesting for me too!`': 'discussion',
                # TODO: link to dicussion done
                '#IF($IF_CHOOSE=False) `Well...It\'s not clear what exactly you want,`$NAME`. I\'m still learning, so please '
                'do not judge too harshly. Maybe you could more explicitly tell me if you\'d like a quiz or proceed directly'
                'to discussion?`': 'quiz_or_discussion',
            }
        },
        '`Congratulations! You have won the prize!!! You are the fashion master! Please paste the link above to your browser to get the very '
        'special prize we\'ve prepared for you!`#GET_PRIZE`'
        '\nDo you like the prize?`': {
            'state': 'prize',
            'score': 0.8,
            '#GPT_IF_LIKE': {  # TODO: more contents
                '#IF($USER_FEEDBACK=True) `I\'m really glad you like it! Should we proceed to the discussion now,` $NAME`?`': 'quiz_or_discussion',
                '#IF($USER_FEEDBACK=False) `OK :( I\'ll try to improve the prize next time. Should we proceed to the discussion now,` $NAME`?`': 'quiz_or_discussion',
            }
        },
    }
    quiz_or_discussion = {
        'state': 'quiz_or_discussion',
        '` `': {
            '[/(?i)(quiz|quizzes|test|exam)/]': {
                '`Now I see your point! I\'m glad to give you more quizzes.`': 'general_quiz'
            },
            '[/(?i)(discussion|discussion|discuss|chat)/]': {
                '`Absolutely! I am well-versed in the world of fashion and look forward to discussing it with you.`': 'discussion'
                # TODO: links to discussion: Done
            },
            '[/(?i)(yes|yea|definitely|of course|yep|sure|yeah|yup|correct|right|good|fantastic|ok|okay)/]': {
                'score': 0.8,
                '`Definitely! Fashion is one of my areas of expertise and I am delighted to discuss it with you.`': 'discussion'
                # TODO: links to discussion: Done
            },
            'error': {
                '`Sorry, I don\'t quite understand. you can do another quiz to boost your score (your current score is: '
                '`$QUIZ_SCORE `/`$QUIZ_TAKEN `), or you can discuss some more in-depth fashion matters with me.`': 'quiz_or_discussion'
            }
        }
    }

    transition_discussion_start = {
        'state': 'discussion',
        '`As a fashion chatbot, I am most interested in the clothing you have chosen to wear today. Mind sharing the details with me?`': {
            '#GPT_WEAR#GET_STYLE': 'color_talk',
            'error': 'discussion'
        }
    }
    transition_color_talk = {
        'state': 'color_talk',
        '#IF($color_talk)`Are you a fan of vibrant and colorful clothing?`': {
            '[/(?i)(yes|do|yea|definitely|of course|ofc|yep|sure|yeah|yup|correct|right|good|fantastic|ok|okay)/]': {
                '`Cool. I have no personal preference for color, but I can certainly appreciate the variety and expression that colorful clothing can bring to one\'s wardrobe.`':
                    {'#ANYINPUT': 'occasion_talk'}
            },
            '[/(?i)(no|eww|none|not|pardon|at all|do not|ugh|don\'t)/]': {
                '`As an AI, I do not possess personal preferences, but I can tell you that black and white clothing can make a bold and timeless statement. Plus, you can always add a pop of color like you did today!`':
                    {'#ANYINPUT': 'occasion_talk'}
            },
            'error': 'weather_talk'
        },
        '#IF($color_talk_no)`Are you a fan of black & white clothing?`': {
            '[/(?i)(yes|yea|definitely|ofc|of course|yep|sure|yeah|yup|correct|right|good|fantastic|ok|okay)/]': {
                '`The classic combination of black and white never goes out of style. It\'s timeless, elegant, and goes with anything. `':
                    {'#ANYINPUT': 'occasion_talk'}

            },
            '[/(?i)(no|eww|none|not|pardon|at all|do not|ugh|don\'t)/]': {
                '`Cool. I have no personal preference for color, but I can certainly appreciate the variety and expression that colorful clothing can bring to one\'s wardrobe.`': {
                    '#ANYINPUT': 'occasion_talk'
                }
            },
        }
    }
    transition_occasion_talk = {
        'state': 'occasion_talk',
        '#IF($occasion_talk)`Are you dressing up for some special occasion?`': {
            '[/(?i)(yes|yea|definitely|of course|yep|sure|yeah|yup|correct|right|good|fantastic|ok|okay|indeed)/]': {
                '`Great! What is the occasion?`': {
                    '#GPT_GETOCCASION': {
                        '`Oh, dress code does needed for`$occasion': {'#ANYINPUT': 'weather_talk'}
                    }
                }
            },
            '[/(?i)(no|none|not|at all|do not|don\'t)/]': {
                '`Well, well, well, look at you all dressed up like you\'re about to receive an award!'
                ' I love seeing people putting effort into their day-to-day outfits and opting for more formal attire. It shows'
                ' that you take pride in your appearance and have a keen eye for fashion.`#SET_BOOL(personality_talk, True) #SET_BOOL(occasion_talk, False)': {
                    '#ANYINPUT': 'personality_talk'}
            }
        },
        '#IF($occasion_talk_no)': 'personality_talk'
    }
    transition_personality_talk = {
        'state': 'personality_talk',
        '#IF($personality_talk)`I have to say, your outfit is so eye-catching, do you have any tips for someone who wants to experiment with more bold fashion choices?`': {
            '[/(?i)(no|nope|not really|nah|do not|don\'t|none)/]': {
                '`That\'s fine! Experimenting with different textures and layering can also add some visual interest to the look.`': 'weather_talk',
            },
            'error': {
                # TODO: 没有provide tips的case
                '`very very useful. I\'ll definitely make a note of it in my ongoing exploration of the fascinating world of fashion.`': 'weather_talk',
            },
        },
        '#IF($personality_talk_no)': 'weather_talk',
    }
    transition_weather_talk = {
        'state': 'weather_talk',
        '#IF($weather_talk)`Are you comfortable with the weather in this attire, may I ask?`#GET_HOT': {
            '[/(?i)(am|yes|yea|definitely|of course|yep|sure|yeah|yup|correct|right|good|comfy|ok|okay|comfortable)/]': {
                '#IF($hot)`I suppose the chilly weather is not your cup of tea?`': {
                    '#ANYINPUT': 'style_start'},
                '#IF($cold)`Wow, I must say, you\'re quite immune to the cold! Impressive!`': {
                    '#ANYINPUT': 'style_start'},
                '#IF($comfy)`Comfort and practicality are always in fashion in my book.`': {
                    '#ANYINPUT': 'style_start'}
            },
            '[/(?i)(no|none|not|at all|do not|don\'t|tight)/]#SET($comfy=False)': {
                '#IF($hot)`Today is indeed hot`': {'#ANYINPUT': 'style_start'},
                '#IF($cold)`I\'m sorry to hear that you\'re not comfortable in this weather. Grab something warm to throw on!`': {
                    '#ANYINPUT': 'style_start'},
                # TODO 上面这个可以连rec感觉，如果还能连回来的话
                # '#IF($cold)`I see that the weather is chilly outside. It's important to dress warmly so that you don't catch a cold. I can suggest some stylish and cozy outfits that will keep you comfortable and warm at the same time. Would you like me to help you put together an outfit that is both practical and fashionable?`': 'style_start',
                '#IF($comfy)`I guess comfort and practicality part ways with fashion.`': {'#ANYINPUT': 'style_start'}
            },
            '#UNX': {
                '`I definitely hope you can be comfortable`': 'style_start'
            }
        },
        '#IF($weather_talk_no)`I command on your outfit. Looks like you\'re dressed just right for the weather. Comfort and practicality are always in fashion in my book.`': 'end'
    }

    transition_style_start = {
        'state': 'style_start',
        '#IF($personality_talk)`Do you think your outfit today belongs to`$style_wearing`style?`#SET($rec=false)': {
            'state': 'determine_style',
            '[/(?i)(am|kind of|do|yes|yea|definitely|think so|belong|of course|yep|sure|have|yeah|yup|correct|right|good|fantastic|ok|okay|fan|like)/]': 'style_brand',
            '[/(?i)(no|none|not|at all|do not|don\'t|hate|dislike|does not|doesn\'t)/]': {
                'state': 'style2',
                '`What do you think is your style?`': {
                    '#GET_STYLE2': {
                        '`Interesting, so you are a fan of`$fav_style': 'determine_style',
                        '#IF($rec=true)`Interesting, so you are a fan of`$fav_style #SET($valuedfactor=brand)': 'dissatisfied2'
                    },
                },
                '#GATE`Can you describe your personal style?`': {
                    '#GET_STYLE2': {
                        '`Interesting, it appears that you have an affinity for`$fav_style': 'determine_style',
                        '#IF($rec=true)`Interesting, so you are a fan of`$fav_style #SET($valuedfactor=brand)': 'dissatisfied2'
                    },
                },
            },
        },
        '#IF($occasion_talk)`If you are not dressing for`$occasion`What do you usually wear?`': {
            '#GPT_WEAR #GET_STYLE': {
                '` Are you perhaps interested in`$style_wearing': 'determine_style'
            }
        },
        '`I\'m curious, do you have a passion for`$style_wearing': 'determine_style'
    }

    transition_style_brand = {
        'state': 'style_brand',
        # '#GET_BRAND #GET_BRANDINFO`Have you heard of`$brand`?`': {
        '#GET_BRAND #GET_BRANDINFO`Have you heard of`$brand`?`': {
            '[/(?i)(yes|kind of|yea|definitely|ofc|of course|yep|sure|yeah|yup|correct|right|good|fantastic|ok|okay|have heard|know|knows)/]': {
                'state': 'brand_heard_of',
                '#IF($master)`I have to say`$NAME`no wonder you are the fashion master.`$brand`,`$brandinfo` What do you think of that brand?`': {
                    'state': 'brand_sentiment',
                    # TODO 因为brand sentiment也会进进出出，所以可以obtain prompt
                    '#SENTIMENT_BRAND': {
                        '#IF($senti_brand=positive)#GET_BRANDSTYLEINFO`I am delighted to hear that it meets your approval.`$brandstyleinfo': {
                            '#ANYINPUT': 'fav_brand'
                        },
                        '#IF($senti_brand=negative)`It\'s understandable that everyone has different tastes and preferences.`': 'fav_brand',
                        '#IF($senti_brand=neutral)#GET_BRANDFUNFACT`It\'s understandable to have a neutral opinion on a brand.`$brand_funfact': {
                            '#ANYINPUT': 'fav_brand'
                        }
                    }
                },
                '$brand`is`$brandinfo`What do you think of that brand?`': 'brand_sentiment'
            },
            '[/(?i)(no|not|never|haven\'t|have not|not yet)/]': {
                'state': 'brand_never_heard_of',
                '#GET_BRANDSTYLEINFO $brandstyleinfo`I thought you would be interested? Are you?`': {
                    '[/(?i)(can|try|am|kind of|do|yes|yea|definitely|think so|belong|of course|yep|sure|have|yeah|yup|correct|right|good|fantastic|ok|okay|fan|like)/]': {
                        '#GET_BRANDFUNFACT$brand_funfact`What do you think of that brand?`': 'brand_sentiment'
                    },
                    '[/(?i)(no|none|not|at all|do not|don\'t|hate|dislike|does not|doesn\'t)/]': 'fav_brand',
                    'error': 'fav_brand'

                }
            },
            '#UNX': 'brand_never_heard_of'
        }
    }
    transition_fav_brand = {
        'state': 'fav_brand',
        '`It seems like you have a good eye for fashion. Which brand do you find yourself drawn to?`': {
            '#GET_FAVBRAND #GET_BRANDINFO': {
                # '#GATE `Interesting, a fan of`$brand`,`$brandinfo`\n`': 'fav_item',
                '$brandinfo`\n I must say, you possess some taste. Why do you like it?`': {
                    '#GET_REASON': {
                        '#IF($design_philosophy) #SET($control=design_philosophy) #GET_REASON_INFO$reason_info`I find fashion philosophy to be a fascinating topic. What are some other aspects of your philosophy that you prioritize in your wardrobe choices?`': {
                            '#ANYINPUT': 'fav_item'
                        },
                        '#IF($personal_experiences) #SET($control=personal_experiences) #GET_REASON_INFO$reason_info`It is pleasing to hear that you have had such a positive experience with them.`': {
                            '#ANYINPUT': 'fav_item'
                        },
                        '#IF($style) #SET($control=style) #GET_REASON_INFO$reason_info`Indeed, fashion fades, style remains`': {
                            '#ANYINPUT': 'fav_item'
                        },
                        '#IF($quality) #SET($control=quality) #GET_REASON_INFO$reason_info`The durability and longevity of a garment not only ensures that it will serve you well for years to come,'
                        ' but also contributes to a more sustainable approach to fashion. `': {
                            '#ANYINPUT': 'fav_item'
                        },
                        '#IF($trendy) #SET($control=trendy) #GET_REASON_INFO $reason_info`It\'s great to hear that you appreciate the current trends and styles'
                        ' represented by `$brand`. It\'s always cool to see fashion evolve and embrace new ideas.`': {
                            '#ANYINPUT': 'fav_item'
                        },
                        '#IF($other) #SET($control=other) #GET_REASON_INFO $reason_info': {
                            '#ANYINPUT': 'fav_item'
                        }
                    }
                },
                # '`error`': 'end',
            }
        }
    }
    transition_fav_item = {
        'state': 'fav_item',
        '`Do you have a favorite piece from them?`': {
            '#GET_FAVITEM': {
                '`cool, `$item': 'rec',
            }
        }
    }


    transitions_rec = {
        'state': 'rec',
        '#SET_VAR`I think I have learned enough of your taste. I am going to generate a fashion recommendation to you`': {
            'state': 'rec1',
            # '` `':
            #     {
                    'error': {
                        'state': 'what_occasion',
                        'score': 0.8,
                        '`What is the occasion that you want the outfit to fit in?`': {
                            'state': 'set_occasion',
                            '#GPT_SET_OCCASION': 'rec2'
                            # 'error': 'set_occasion',
                        },
                    },
                    '#IF($occasion!=none)': {
                        '`Do you need recommendation for`$occasion`?`': {
                            '[/(?i)(yes|yea|definitely|of course|yep|sure|yeah|yup|correct|right|good|fantastic|ok|okay)/]': 'rec2',
                            'error': 'what_occasion'
                        }
                    },
                # }
        },
    }
    transitions_rec2 = {
        'state': 'rec2',
        '`What factor do you value the most when`$temp`?`': {  # $temp1
            'state': 'dissatisfied',
            '#SET($prompt_count=1)#GPT_SetValuedFactor #Macro_GetPrompt': {  # Macro_Rec
                'state': 'dissatisfied2',
                '#IF($valuedfactor=affordability)$STATEMENT #SET($affordability=true)': 'pre_rec',
                '#IF($valuedfactor=quality) $STATEMENT #SET($quality=true)': "pre_rec",
                '#IF($valuedfactor=brand) #Macro_GetPrompt $STATEMENT': {
                    'state': 'factor_brand',
                    '#GPT_specific': {
                        '#IF($specific_bool=true)`true specific brand`$spec_brand': 'rec_final',  #
                        '#IF($specific_bool!=true)`That\'s totally fine! Then,`#SET($temp=choosing a brand)': 'rec2',
                    },
                    'error': {
                        '`It doesn\'t hurt to get to know you more`': 'rec2',
                    },
                },
                '#IF($valuedfactor=fit) $STATEMENT #SET($fit=true) #SET($valuedfactor=brand)': {
                    'error': 'dissatisfied2',
                },
                '#IF($valuedfactor=style) $STATEMENT #SET($style=true) #SET($rec=true)': 'style2',
                '`Thanks for sharing!`#SET($valuedfactor=brand)': {
                    'score': 0.2,
                    'error': 'dissatisfied2',
                },
            },
            'error': {
                '`I see`#SET($valuedfactor=brand)': 'dissatisfied2',
            },
        },
    }
    # transitions_step = {
    #     'state': 'step',
    #     '`Do you have any specific brands that you are looking for?`': {
    #         '#GPT_specific': {
    #             '#IF($specific_bool=true)`Sure! Before I find you an item from `$spec_brand `, do u have any other factors that you would like me to consider?`': {
    #                 '[/(?:)(yes|yea|definitely|of course|yep|sure|yeah|yup|correct|right|good|fantastic|ok|okay)/]': 'dissatisfied',
    #                 'error': 'end',
    #             },
    #         }
    #     }
    # }
    transitions_rec_final = {
        'state': 'pre_rec',
        # '#GATE `Tell me more about your other considerations if you have one!`'
        '#SET($prompt_count=2)`Do you have any other more considerations that you would like me to know? Tell me more!`#Macro_GetPrompt': {
            '#GPTConcern #IF($if_concern=yes)': 'dissatisfied',
            '#IF($if_concern=no)': 'rec_final',
            'error': {
                'state': 'rec_final',
                '#GPT_RecItem`Sure! Lemme try if my recommendation can fit your taste!\n`$STATEMENT`how do you like`$GPTITEM `from`$GPTBRAND': {
                    # $GPTITEM `from`$GPTBRAND`
                    '#GPT_sentiment #IF($SENTIMENT=positive)': {
                        '`Excellent! Would you like me to make another recommendation for you?`': {
                            '[/(?i)(yes|yea|definitely|of course|yep|sure|yeah|yup|correct|right|good|fantastic|ok|okay)/]#SET($occasion=none)': 'rec1',
                            'error': 'check',  # connect to conclusion
                        },
                    },
                    'error': {
                        '`Sorry that my taste has not kept up with yours. Tell me more about your concerns! (route to state dissatisfied)`': 'dissatisfied',
                    },
                },
            },
        },
    }

    transition_check = {
        'state': 'check',
        '`I\'m so glad that we are proceeding to the final phases of our conversation and sincerely hoping that you are enjoying our service!\n'
        ' It\'s really such a pleasure and honor for me to cooperate and work together for the goal. \n'
        'However, before we move on to the next steps, do you want another round of exciting quizzes or fashion jokes？`': {
            '#GPT_GET_TOPIC1': {  # TODO 改prompt？
                '#IF($CHOOSE_ONE=quiz)`Absolutely, I hope you are enjoying the process of challenging new concepts!\n`': 'final_quiz',
                '#IF($CHOOSE_ONE=jokes)`Absolutely, I hope you are enjoying the process of challenging new concepts!\n`': 'fashionJokes2',
                '#IF($CHOOSE_ONE=no)`That\'s absolutely fine. So I guess you are ready to move on!`': 'preference',
                '`Sure! I hope you are enjoying the process.`': {
                    'score': 0.2,
                    'error': 'preference',
                }
            }
        }
    }

    transition_preference = {
        'state': 'preference',
        '`Everything seems so good so far, `$NAME` Now let me generate a preference report for you: based on our database and experiences'
        '\n  with thousands of customers and companies, I\'m more than excited to tell you that '
        '\n you are absolutely a perfect model fit for the famous examplary brands of `$brand` and `$item` with the `$fav_style` under `$occasion` . '
        '\n Some of the most attracting pieces that we recommend you should be `$GPTITEM` from `$GPTBRAND`.Woo-hoo!  '
        '\n I appreciate for the great efforts we made to this outstanding outcome. Are you satisfied with the preference summary I made for you?`': {
            '[/(?i)(yes|yea|definitely|of course|yep|sure|will do|i\'ll|try|interesting|ok|okay|could|appreciate|good)/]': {
                '`That\'s the most perfect response I\'ve ever heard. Thanks for all the contributions and great involvement you\'done. Any other background information you would like to know about?`': {
                    '#GPT_GET_TOPIC1': {
                        '#IF($CHOOSE_ONE=quiz)`Absolutely, I hope you are enjoying the process of challenging new concepts!`': 'quiz',
                        '#IF($CHOOSE_ONE=jokes)`Absolutely, I hope you are enjoying the process of challenging new concepts!`': 'Fashion Jokes',
                        '#UNX': {'`That\'s absolutely fine. So I guess you are ready to move on!`': 'conclude'}
                    }
                }
            },
            '[/(?i)(no|nope|not|nah|already|have seen|not interesting|lame|won\'t|don\'t|wouldn\'t|sorry|bad|prefer not)/]': {
                '`I feel so sorry to hear that. You must have some other great concerns regarding our products '
                '\n and service functions which we are more than willing to listen about. Could you provide any '
                '\n feedback or concerns for any related service or function?`': {
                    '[/(?i)(yes|yea|definitely|of course|yep|sure|will do|i\'ll|try|interesting|ok|okay|could|appreciate|good)/]': {
                        '`So which aspects of our recommendation system you are having some different opinions? `': 'question_1'
                    },
                    'error': {
                        '`I\'m considering that you are overall accepting our suggestions. We are ready to move on! `': 'conclude'
                    }
                }

            },
            'error': {
                '`I\'m considering that you are overall accepting our suggestions. We are ready to move on! `': 'conclude'
            }
        }
    }

    transition_feedback1 = {
        'state': 'question_1',
        '`Did the fashion chatbot provide helpful recommendations?` #SET_NUM(Q,1)': {
            '#GET_FEEDBACK': 'question_2'
        }
    }
    transition_feedback2 = {
        'state': 'question_2',
        '`Did the fashion chatbot make your shopping experience more efficient?` #SET_NUM($Q,2)': {
            '#GET_FEEDBACK': 'question_3'
        }
    }
    transition_feedback3 = {
        'state': 'question_3',
        '`Would you recommend the fashion chatbot to a friend?` #SET_NUM($Q,3)': {
            '#GET_FEEDBACK': 'question_4'
        }
    }
    transition_feedback4 = {
        'state': 'question_4',
        '`Did the fashion chatbot provide accurate information about fashion and style?` #SET_NUM($Q,4)': {
            '#GET_FEEDBACK': 'question_5'
        }
    }
    transition_feedback5 = {
        'state': 'question_5',
        '`Was the fashion chatbot easy to use and understand?` #SET_NUM($Q,5)': {
            '#GET_FEEDBACK': 'conclude'
        }
    }
    conclusion_transitions = {
        'state': 'conclude',
        # '`Have a nice day!`': 'end'
        '`Congratulations on the great works we\'ve achieved! `$NAME`Hope our recommendation serves its purpose in finding you the right outfit'
        '\nfor whatever occasion that you might see fit. I genuinely hope that these information I provided could add a little more colors to your day!'
        '\nNevertheless, no matter what recommendations I gave you, no one should be defined by the so-called \"fashion\"'
        '\nnor should they be constrained by the stereotypes. to you, the most significant truth is that anyone could have a chance to be a real StylAIst to themselves, challenge\n'
        '\nthe traditional ideas about what should be considered aesthetic and show the true real self form of essentialness to'
        '\nthe world.`': 'end'
    }
    final_quiz = {
        'state': 'final_quiz',
        '`Here is what I got for you:` #FASHION_QUIZ `What is the answer of this?`': {
            '#IF_CORRECT': 'final_quiz_cont'
        },
    }
    final_quiz_cont = {
        'state': 'final_quiz_cont',
        '#IF($QUIZ_CORRECTNESS=True) `Wonderful! The answer is exactly` $CORRECT_ANSWER `. Your current score is` '
        '$QUIZ_SCORE `/` $QUIZ_TAKEN`. We have a special prize for you if you got` $QUIZ_LEFT `more quizzes correct! '
        '\nDo you want to do another quiz to boost up your score? Or we can proceed to the conclusion.`': 'final_quiz_or_preference',
        '#IF($QUIZ_CORRECTNESS=False) `OK. The correct answer is, in fact,` $CORRECT_ANSWER `. Your current score is` '
        '$QUIZ_SCORE `/` $QUIZ_TAKEN`. We have a special prize for you if you got` $QUIZ_LEFT `more quizzes correct!  '
        '\nDo you want to do another quiz to boost up your score? Or we can proceed to the conclusion.`': 'final_quiz_or_preference',
        '`Congratulations! You have won the prize!!! You are the fashion master! Please paste the link above to your browser to get the very '
        'special prize we\'ve prepared for you!`#GET_PRIZE`'
        '\nDo you like the prize?`': {
            'state': 'final_prize',
            'score': 0.8,
            '#GPT_IF_LIKE': {  # TODO: more contents
                '#IF($USER_FEEDBACK=True) `I\'m really glad you like it! Should we proceed to the conclusion now,` $NAME`?`': 'final_quiz_or_preference',
                '#IF($USER_FEEDBACK=False) `OK :( I\'ll try to improve the prize next time. Should we proceed to the conclusion now,` $NAME`?`': 'final_quiz_or_preference',
            }
        },
    }
    final_quiz_or_preference = {
        'state': 'final_quiz_or_preference',
        '` `': {
            '[/(?i)(quiz|quizzes|test|exam)/]': {
                '`I\'m glad to give you more quizzes.`': 'final_quiz'
            },
            '[/(?i)(yes|sure)/]': {
                '`So another quiz?`': 'final_quiz'
            },
            '#UNX': {
                '`OK`': 'conclude'  # Link to preference
            }
        }
    }

    # TODO link to conclusion
    fashionJokes_conclusion = {  # TODO
        'state': 'fashionJokes2',
        '`Here is what I got for you:` #FASHION_JOKE `\nI hope you enjoy this! Do you want another one?`': {
            '[/(?i)(yes|yea|definitely|of course|yep|sure|yeah|yup|correct|right|good|fantastic|ok|okay)/]': {
                '`Wonderful!:`': 'fashionJokes2'
            },
            '#UNX': {
                '`ok`': 'conclude' # todo preference
                # '`OK` $NAME `You seem to be uninterested. Let us move on to the conclusion then.`': 'preference'
            }
        }
    }

    df = DialogueFlow('start', end_state='end')
    # df = DialogueFlow('start', end_state='end')
    df.load_transitions(greeting)
    df.load_transitions(first_quiz)
    df.load_transitions(first_quiz_cont)
    df.load_transitions(get_name)
    # df.load_global_nlu(global_transitions)
    df.load_transitions(general_quiz)
    df.load_transitions(general_quiz_cont)
    df.load_transitions(fashionJokes)
    df.load_transitions(quiz_or_discussion)

    df.load_transitions(transition_discussion_start)
    df.load_transitions(transition_color_talk)
    df.load_transitions(transition_occasion_talk)
    df.load_transitions(transition_weather_talk)
    df.load_transitions(transition_personality_talk)
    df.load_transitions(transition_style_start)
    df.load_transitions(transition_style_brand)
    # df.load_transitions(transition_brand_heard_of)
    df.load_transitions(transition_fav_brand)
    df.load_transitions(transition_fav_item)

    df.load_transitions(transitions_rec)
    df.load_transitions(transitions_rec_final)
    df.load_transitions(transitions_rec2)
    # df.load_transitions(transitions_step)
    df.load_transitions(transition_check)
    # df.load_transitions(transition_preference)
    df.load_transitions(transition_feedback1)
    df.load_transitions(transition_feedback2)
    df.load_transitions(transition_feedback3)
    df.load_transitions(transition_feedback4)
    df.load_transitions(transition_feedback5)
    df.load_transitions(conclusion_transitions)
    df.load_transitions(final_quiz)
    df.load_transitions(final_quiz_cont)
    df.load_transitions(final_quiz_or_preference)
    df.load_transitions(fashionJokes_conclusion)

    df.add_macros(macros)
    return df


if __name__ == '__main__':
    openai.api_key_path = utils.OPENAI_API_KEY_PATH
    main().run()
