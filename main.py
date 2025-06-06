from autobahn.twisted.component import Component, run
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.util import sleep
from alpha_mini_rug.speech_to_text import SpeechToText 
from games.medium_digit_span import play_digit_span_game
from games.high_stroop_test import play_stroop_test_game
from games.low_word_chain import play_word_chain_game
from utils.extra import request_to_chatgpt  

audio_processor = SpeechToText() # create an instance of the class  # changing these values might not be necessary 
audio_processor.silence_time = 0.5 # parameter set to indicate when to stop recording 
audio_processor.silence_threshold2 = 120 # any sound recorded below this value is considered silence   
audio_processor.logging = False # set to true if you want to see all the output 

@inlineCallbacks
def main(session, details):
    history = "None"

    yield session.call("rom.optional.behavior.play", name="BlocklyStand")
    yield session.call("rie.dialogue.say_animated", text="Hello there!")

    yield session.call("rom.sensor.hearing.sensitivity", 1650)   
    yield session.call("rie.dialogue.config.language", lang="en")  
    print("listening to audio")  
    yield session.subscribe(audio_processor.listen_continues, "rom.sensor.hearing.stream")  
    yield session.call("rom.sensor.hearing.stream") 

    x=True
    while x:      
        if not audio_processor.new_words:          
            yield sleep(0.5)  # VERY IMPORTANT, OTHERWISE THE CONNECTION TO THE SERVER MIGHT CRASH          
            print("I am recording")      
        else:          
            word_array = audio_processor.give_me_words()          
            print("I'm processing the words")          
            print(word_array[-3:])  # print last 3 sentences 
    
            if word_array[-1][0] != "game time":
                question = word_array[-1][0] 
                answer = request_to_chatgpt(question, history)
                yield session.call("rie.dialogue.say_animated", text=answer)
                yield sleep(2)
                history += "Elderly response:" + word_array[-1][0] + " " + "GPT answer:" + answer


            if word_array[-1][0] == "game time":
                yield sleep(2)

                with open("prompts/cog_prompt2.txt", "r") as file:
                    cog_content = file.read()
                cog_answer = request_to_chatgpt(cog_content, history)
                print(int(cog_answer))
                #with open("prompts/cog_score.txt", "w") as file:
                    #file.write(cog_answer)
                
                yield session.call("rie.dialogue.say_animated", text="Now, let's play a game!")

                if int(cog_answer) >= 8:
                    yield play_stroop_test_game(session, audio_processor)
                
                elif int(cog_answer) >= 6:
                    yield play_digit_span_game(session, audio_processor)
                
                else:
                    yield play_word_chain_game(session, audio_processor)

                x=False

        audio_processor.loop()  

    session.leave() 

wamp = Component(
    transports=[{
        "url": "ws://wamp.robotsindeklas.nl",
        "serializers": ["msgpack"],
        "max_retries": 0
    }],
    realm="rie.6842bf6d9827d41c07337c2b",
)

wamp.on_join(main)

if __name__ == "__main__":
    run([wamp])
