import random
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.util import sleep


categories = {
    "numbers": ["one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"],
    "letters": ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"],
    "animals": ["dog", "cat", "lion", "tiger", "elephant", "monkey", "panda", "giraffe", "zebra", "bear"],
    "colors": ["red", "blue", "green", "yellow", "purple", "orange", "pink", "brown", "black", "white"]
}

category_cards = {
    "numbers": 1,
    "letters": 2,
    "animals": 3,
    "colors": 4
}

@inlineCallbacks
def play_memory_game(session):
    yield session.call("rie.dialogue.say", text="Let's play a memory game!")
    yield session.call("rie.dialogue.say", text="Please choose a category: numbers, letters, animals, or colors.")
    yield session.call("rie.dialogue.say", text="To choose a category, show me the correct Aruco card.")

    category = None
    while category not in categories:
        yield sleep(2)
        aruco_response = yield session.call("rie.vision.card.read", time=0)
        print("Aruco response:", aruco_response)
        detected_category = aruco_response[-1]['data']['body'][-1][-1]
        aruco_response = None
        for cat, number in category_cards.items():
            if detected_category == number:
                category = cat
                break
        if category not in categories:
            yield session.call("rie.dialogue.say", text="I couldn't recognize that category card. Please try again.")

    yield session.call("rie.dialogue.say", text=f"You selected the category: {category}.")
    yield session.call("rie.dialogue.say", text=f"I will now say a few {category}. Try to remember them and show me the correct Aruco cards in the same order.")
    items = categories[category]
    sequence = []
    score = 0

    while True:
        sequence = [random.randint(1, 10) for _ in range(score + 1)]
        print("Generated sequence:", sequence)
        item_names = [items[i-1] for i in sequence]

        yield session.call("rie.dialogue.say", text=f"Listen carefully. The sequence is: {' '.join(item_names)}")
        yield session.call("rie.dialogue.say", text=f"Please show me the cards in the same order.")
        yield sleep(2)

        for i in range(len(sequence)):
            correct = False
            while not correct:
                yield sleep(5)
                aruco_response_2 = yield session.call("rie.vision.card.read", time=0)
                detected = aruco_response_2[-1]['data']['body'][-1][-1]
                print("Detected:", detected, "Expected:", sequence[i])

                if detected == sequence[i]:
                    correct = True
                else:
                    yield session.call("rie.dialogue.say", text="That card is incorrect.")
                    yield session.call("rie.dialogue.say", text=f"Your final score is {score}.")
                    return score

        score += 1
        yield session.call("rie.dialogue.say", text=f"Well done! Your current score is {score}.")
        yield session.call("rie.dialogue.say", text="Let's try a longer sequence!")
