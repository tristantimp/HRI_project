from games.medium_digit_span import play_digit_span_game
from games.high_stroop_test import play_stroop_test_game
from games.low_word_chain import play_word_chain_game

cognitive_scores = []
cognitive_level = "" # first based on first conversation

def evaluate_cognitive_state(scores):
    average = sum(scores) / len(scores)
    mean_score = round(average)

    if mean_score >= 8:
        cognitive_level = "good"
    elif mean_score >= 6:
        cognitive_level = "medium"
    else:
        cognitive_level = "bad"
   
    return cognitive_level



score = play_word_chain_game(session, audio_processor)
cognitive_scores.append(score)

score = play_digit_span_game(session, audio_processor)
cognitive_scores.append(score)

score = play_stroop_test_game(session, audio_processor)
cognitive_scores.append(score)

cognitive_level = evaluate_cognitive_state(cognitive_scores)