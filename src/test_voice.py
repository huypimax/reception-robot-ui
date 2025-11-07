# import pyttsx3

# def speak(text):
#     engine = pyttsx3.init()
#     voices = engine.getProperty('voices')
    
#     # Chọn voice tiếng Anh (tùy hệ điều hành)
#     english_voice = None
#     for voice in voices:
#         if "en" in voice.id.lower() or "english" in voice.name.lower():
#             english_voice = voice.id
#             print(f"✅ Found English voice: {voice.name} - {voice.id}")
#             break

#     if english_voice:
#         engine.setProperty('voice', english_voice)
#     else:
#         print("⚠️ No English voice found. Using default.")
    
#     engine.setProperty('rate', 150)
#     engine.say(text)
#     engine.runAndWait()


# if __name__ == "__main__":
#     speak("Hello! This is AIko speaking English.")
#     speak("You are now using an English voice.")

import asyncio
import edge_tts

async def speak(text):
    communicate = edge_tts.Communicate(text, voice="en-US-GuyNeural")
    await communicate.save("tts.mp3")

    # Phát file
    import playsound
    playsound.playsound("tts.mp3")

# Gọi bất đồng bộ
asyncio.run(speak("Hello, I am AIko, your assistant. How can I help you?"))
