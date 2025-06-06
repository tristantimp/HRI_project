from twisted.internet.defer import inlineCallbacks
import openai
from autobahn.twisted.util import sleep


used_words = []

def generate_next_word(last_letter):
    prompt = (
        f"""
        You are playing a word chain game (Shiritori) with a user. 
        Your last word ended in '{last_letter}'. 
        Come up with a new English word that starts with '{last_letter}' 
        and has a slightly more difficult last letter to start a new word with than before. 
        Do not use a word that has already been used: {used_words}. 
        Respond with only the new word, no explanation.
        """
    )

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip().lower()

@inlineCallbacks
def play_word_chain_game(session, audio_processor):
    score = 0
    last_letter = ""
    gpt_word = "start"
    used_words.append(gpt_word)

    yield session.call("rie.dialogue.say_animated", text=f"Let's play word chain! We'll take turns saying words.")
    yield session.call("rie.dialogue.say_animated", text=f"Say 'stop' or 'quit' if you want to stop the game.")
    yield session.call("rie.dialogue.say_animated", text = f"Each new word must start with the last letter of the previous word. Ready? My word is '{gpt_word}'. Your turn!")

    playing = True
    while playing:
        heard_word = None
        for _ in range(20):  # max 10s
            audio_processor.loop()
            if audio_processor.new_words:
                heard_word = audio_processor.give_me_words()[-1][0].lower()
                break
            yield sleep(0.5)

        if not heard_word:
            yield session.call("rie.dialogue.say_animated", text="Time's up! Looks like I win this round but you did great!")
            break

        if heard_word in ["stop", "quit"]:
            yield session.call("rie.dialogue.say_animated", text="Okay, stopping the game.")
            break

        # Validate
        if heard_word in used_words:
            yield session.call("rie.dialogue.say_animated", text="This word hasd already been said. Looks like I win this round but you did great!")
            break

        if not heard_word.startswith(last_letter):
            yield session.call("rie.dialogue.say_animated", text=f"That word doesn't start with '{last_letter}'. Looks like I win this round but you did great!")
            break

        used_words.append(heard_word)
        score += 1

        # Max score
        if score == 10:
            yield session.call("rie.dialogue.say_animated", text="You are too good at this game. I give up. You win!")
            break

        # Generate next word
        last_letter = heard_word[-1]
        gpt_word = generate_next_word(last_letter)

        if not gpt_word or gpt_word in used_words:
            yield session.call("rie.dialogue.say_animated", text="I'm out of words. You win!")
            break

        used_words.append(gpt_word)
        last_letter = gpt_word[-1]
        yield session.call("rie.dialogue.say_animated", text=f"My word is '{gpt_word}'. Your turn!")

    return score