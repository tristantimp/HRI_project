from autobahn.twisted.component import Component, run
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.util import sleep
import openai
from alpha_mini_rug.speech_to_text import SpeechToText 
import os
from memory_game import play_memory_game

audio_processor = SpeechToText() # create an instance of the class  # changing these values might not be necessary 
audio_processor.silence_time = 0.5 # parameter set to indicate when to stop recording 
audio_processor.silence_threshold2 = 120 # any sound recorded below this value is considered silence   
audio_processor.logging = False # set to true if you want to see all the output 


openai.api_key = os.environ["OPENAI_API_KEY"]

def request_to_chatgpt(prompt, history):
    with open("initial_prompt.txt", "r") as file:
        content = file.read()
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", 
        messages=[
            {"role": "system", "content": content + history},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

@inlineCallbacks
def main(session, details):
    history = "None"

    yield session.call("rom.optional.behavior.play", name="BlocklyStand")
    yield session.call("rie.dialogue.say_animated", text="Hello there!")

    yield play_memory_game(session)

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
    
            if word_array[-1][0] != "stop":
                question = word_array[-1][0] 
                answer = request_to_chatgpt(question, history)
                yield session.call("rie.dialogue.say_animated", text=answer)
                yield sleep(2)
                history += "Elderly response:" + word_array[-1][0] + " " + "GPT answer:" + answer


            if word_array[-1][0] == "stop":
                yield sleep(2)
                yield session.call("rie.dialogue.say_animated", text="Bye bye, see you next time")
                yield session.call("rom.optional.behavior.play", name="BlocklyWaveRightArm")
                with open("cog_prompt.txt", "r") as file:
                    cog_content = file.read()
                cog_answer = request_to_chatgpt(cog_content, history)
                with open("cog_evaluation.txt", "w") as file:
                    file.write(cog_answer)
                #yield session.call("rie.dialogue.say_animated", text=cog_answer)

                x=False

        audio_processor.loop()  

    session.leave() 

wamp = Component(
    transports=[{
        "url": "ws://wamp.robotsindeklas.nl",
        "serializers": ["msgpack"],
        "max_retries": 0
    }],
    realm="rie.68245ea644932a6a6ce018bd",
)

wamp.on_join(main)

if __name__ == "__main__":
    run([wamp])
