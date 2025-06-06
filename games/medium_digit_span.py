import random
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.util import sleep

categories = {
    "numbers": ["one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"],
    "letters": ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"],
    "animals": ["dog", "cat", "lion", "tiger", "elephant", "monkey", "panda", "giraffe", "zebra", "bear"],
    "colors": ["red", "blue", "green", "yellow", "purple", "orange", "pink", "brown", "black", "white"]
}

@inlineCallbacks
def get_user_response(session, audio_processor):
    for _ in range(20):  # max 10s
        audio_processor.loop()
        if audio_processor.new_words:
            heard = audio_processor.give_me_words()[-1][0].lower()
            return heard
        yield sleep(0.5)
    return ""


@inlineCallbacks
def play_digit_span_game(session, audio_processor):
    yield session.call("rie.dialogue.say", text="Let's play a memory game!")
    yield session.call("rie.dialogue.say", text="Please choose a category by saying: numbers, letters, animals, or colors.")

    # Category
    category = None
    while category not in categories:
        user_response = yield get_user_response(session, audio_processor)
        if user_response in categories:
            category = user_response
        else:
            yield session.call("rie.dialogue.say", text="I didn't catch that. Please say numbers, letters, animals, or colors.")

    yield session.call("rie.dialogue.say", text=f"You chose: {category}. Try to remember the words I say.")
    items = categories[category]
    sequence = []
    score = 0

    # Play game
    while score < 10:
        sequence.append(random.randint(0, 9))  
        word_sequence = [items[i] for i in sequence]
        print(word_sequence)

        yield session.call("rie.dialogue.say", text=f"Listen carefully: {' '.join(word_sequence)}")
        yield session.call("rie.dialogue.say", text="Now repeat the words one by one with a pause between each word.")

        for i, expected_word in enumerate(word_sequence):
            print(f"Expected word: {expected_word}")
            spoken = yield get_user_response(session, audio_processor)
            print(f"Spoken word: {spoken}")
            if spoken != expected_word.lower():
                yield session.call("rie.dialogue.say", text=f"Oops, that was incorrect. I expected {expected_word}.")
                yield session.call("rie.dialogue.say", text=f"Your final score is {score}.")
                return score

        score += 1
    
    return score
