import os
import re
import requests
import pydub
import urllib
import speech_recognition as sr
from bs4 import BeautifulSoup
def solve(session, url):
    try:
        response = session.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        control_frame = None
        challenge_frame = None
        frames = soup.find_all('iframe')
        for frame in frames:
            title = frame.get('title', '')
            if re.search('reCAPTCHA', title):
                control_frame = frame.get('src')
            if re.search('recaptcha challenge', title):
                challenge_frame = frame.get('src')       
        if not (control_frame and challenge_frame):
            print("reCAPTCHA not found!")
            return False
        control_url = urllib.parse.urljoin(url, control_frame)
        session.get(control_url)
        challenge_url = urllib.parse.urljoin(url, challenge_frame)
        challenge_page = session.get(challenge_url)
        soup = BeautifulSoup(challenge_page.text, 'html.parser')
        audio_button = soup.find('button', {'id': 'recaptcha-audio-button'})

        if not audio_button:
            print("Audio challenge button not found!")
            return False
        audio_src = soup.find('audio', {'id': 'audio-source'}).get('src')
        audio_url = urllib.parse.urljoin(url, audio_src)
        path_to_mp3 = os.path.normpath(os.path.join(os.getcwd(), "sample.mp3"))
        path_to_wav = os.path.normpath(os.path.join(os.getcwd(), "sample.wav"))
        audio_data = session.get(audio_url)
        with open(path_to_mp3, 'wb') as f:
            f.write(audio_data.content)
        sound = pydub.AudioSegment.from_mp3(path_to_mp3)
        sound.export(path_to_wav, format="wav")
        sample_audio = sr.AudioFile(path_to_wav)
        r = sr.Recognizer()
        with sample_audio as source:
            audio = r.record(source)
        key = r.recognize_google(audio)
        data = {'audio-response': key.lower()}
        session.post(challenge_url, data=data)
        os.remove(path_to_mp3)
        os.remove(path_to_wav)
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False
if __name__ == "__main__":
    session = requests.Session()
    captcha_url = "https://example.com"
    result = solve(session, captcha_url)
    if result:
        print("CAPTCHA solved successfully!")
    else:
        print("Failed to solve CAPTCHA.")
