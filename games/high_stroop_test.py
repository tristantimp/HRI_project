import random
import time
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.util import sleep

@inlineCallbacks
def get_user_response(session, audio_processor, start_time):
    for _ in range(20):  # max 10 sec
        audio_processor.loop()
        if audio_processor.new_words:
            heard = audio_processor.give_me_words()[-1][0].lower()
            rt = round(time.time() - start_time, 2)
            if "left" in heard:
                return "left", rt
            elif "right" in heard:
                return "right", rt
            else:
                return "unknown", rt
        yield sleep(0.5)
    return "none", None


@inlineCallbacks
def play_stroop_test_game(session, audio_processor):
    #yield session.call("rie.dialogue.say", text="We're going to play a focus game together!")
    yield session.call("rie.dialogue.say", text="When I raise this arm") 
    yield session.call("rom.optional.behavior.play", name="BlocklyRightArmUp")
    yield session.call("rie.dialogue.say", text="you say 'left'.")

    yield session.call("rie.dialogue.say", text="And when I raise this arm")
    yield session.call("rom.optional.behavior.play", name="BlocklyLeftArmUp")
    yield session.call("rie.dialogue.say", text="you say 'right'.")
    yield session.call("rie.dialogue.say_animated", text="Got it? Great! Let's begin")


    total_congruent = 1
    total_incongruent = 1
    correct_congruent = 0
    correct_incongruent = 0
    rt_congruent = []
    rt_incongruent = []

    # Congruent 
    for _ in range(total_congruent):
        side = random.choice(["left", "right"])
        motion = "BlocklyRightArmUp" if side == "left" else "BlocklyLeftArmUp"

        session.call("rom.optional.behavior.play", name=motion)
        session.call("rie.dialogue.say_animated", text=f"{side.capitalize()}")
        #yield session.call("rom.optional.behavior.play", name="BlocklyStand")

        t_start = time.time()
        user_response, rt = yield get_user_response(session, audio_processor, t_start)

        if user_response == side:
            correct_congruent += 1
            yield session.call("rie.dialogue.say", text="Correct.")
        else:
            yield session.call("rie.dialogue.say", text="Incorrect.")

        if rt:
            rt_congruent.append(rt)

        yield sleep(1)

    yield session.call("rie.dialogue.say_animated", text="Now it's going to be harder. Say which side I MOVE, not what I SAY.")
    yield sleep(1)

    # Incongruent
    for _ in range(total_incongruent):
        said = random.choice(["left", "right"])
        moved = "left" if said == "right" else "right"
        motion = "BlocklyRightArmUp" if moved == "left" else "BlocklyLeftArmUp"

        session.call("rom.optional.behavior.play", name=motion)
        session.call("rie.dialogue.say_animated", text=f"{said.capitalize()}")

        t_start = time.time()
        user_response, rt = yield get_user_response(session, audio_processor, t_start)

        if user_response == moved:
            correct_incongruent += 1
            yield session.call("rie.dialogue.say", text="Correct.")
        else:
            yield session.call("rie.dialogue.say", text="Incorrect.")

        if rt:
            rt_incongruent.append(rt)

        yield sleep(1)

    # Evaluation
    errors_congruent = total_congruent - correct_congruent
    errors_incongruent = total_incongruent - correct_incongruent
    interference_errors = errors_incongruent - errors_congruent

    avg_rt_cong = round(sum(rt_congruent) / len(rt_congruent), 2) if rt_congruent else 0
    avg_rt_incong = round(sum(rt_incongruent) / len(rt_incongruent), 2) if rt_incongruent else 0
    rt_interference = round(avg_rt_incong - avg_rt_cong, 2)

    # Scoring
    score = 10
    score -= interference_errors * 2  # penalize errors under interference
    if rt_interference > 1.0:
        score -= 2
    elif rt_interference > 0.5:
        score -= 1

    score = max(0, min(score, 10))

    return score 
