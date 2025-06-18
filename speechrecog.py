import speech_recognition as sr

# Initialize recognizer
recognizer = sr.Recognizer()

# Use microphone as source
with sr.Microphone() as source:
    print("Say something...")
    audio = recognizer.listen(source)

    try:
        # Use Google's free speech recognition
        text = recognizer.recognize_google(audio)
        print("You said:", text)
    except sr.UnknownValueError:
        print("Sorry, could not understand audio.")
    except sr.RequestError as e:
        print(f"Could not request results; {e}")
