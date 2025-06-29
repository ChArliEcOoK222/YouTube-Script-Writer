#ToDO: Fit this whole program into a function in order to run it in Flask as a Web Application

# required libraries
from pytube import YouTube
import whisper
import openai
from openai import OpenAI
from chunkipy import TextChunker
import pyperclip
import os
import sys

# inputting the URL of the video from the bash script
url = input("Enter the URL: ")

# OpenAI API Key
client = OpenAI(
    api_key = os.getenv("OPENAI_API_KEY")
)
# directory to save the video to
directory = "WHERE TO SAVE FILES"

# function to download a youtube video which takes the URL and the directory as arguments
def download_audio(link, path):
    # using pytube to get the video from the link
    video = YouTube(link)
    # setting to download audio only
    audio = video.streams.filter(only_audio = True).first()
    # downloading the audio
    audio.download(path)
# calling the function
download_audio(url, directory)

# loading the Whisper model
model = whisper.load_model("base")
# listing all files now in the directory
all_files = os.listdir(directory)
# locating the newly downloaded .mp4 file
for file in all_files:
    if '.mp4' in file:
        # transcribing the video 
        result = model.transcribe(f"WHERE TO SAVE FILES{file}")
        # creating a text file to store the transcript and writing the transcript to that file
        transcript = open("transcription.txt", "w+")
        # Whispers returns a dictionary so the key with the value of the transcription is written to the .txt file
        transcript.write(result["text"])

# reading the .txt file type as a string type in order to be broken down into chunks
transcript = open("transcription.txt", "r")
transcript_text = transcript.read()

# using the chunkipy model to break down the text into chunks
transcript_chunker = TextChunker(2000, tokens=False, overlap_percent=0)
chunks = transcript_chunker.chunk(transcript_text)

# creating a .txt file to store the paraphrased transcript, the file is in a+ mode to add to the file and then have the ability to read the contents
paraphrased = open("paraphrased.txt", "a+")

# looping over the chunks in order to paraphrase them individually
for chunk in enumerate(chunks):
    # asking the gpt-3.5-turbo-16k model to paraphrase the transcript
    # saving the result to a variable
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {"role": "user", "content": f"Paraphrase the following: {chunk}."}
        ],
        max_tokens=4096,
        n=1
    )
    # accessing the message content of each response
    response_message = response.choices[0].message.content
    # writing all of the new text to the paraphrased.txt file
    paraphrased.write(f" {response_message}")

# reading the paraphrased.txt file in order to access the text
paraphrased_text = paraphrased.read()

# using the chunkipy model to break down the text into chunks
paraphrased_chunker = TextChunker(2000, tokens=False, overlap_percent=0)
paraphrased_chunks = paraphrased_chunker.chunk(paraphrased_text)

# creating a .txt file to store the script
script = open('script.txt', 'a+')

# looping over the chunks in order to create the script
for index, chunk in enumerate(chunks):
    # performing an OpenAI function on the first chunk which will contain the intro and the hook
    if index == 0:
        response = client.chat.completions.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {
            "role": "system",
            "content": f"Use the provided information to format the file {chunk} into a YouTube Script"
            },
            {
            "role": "user",
            "content": "To create engaging YouTube video scripts, start with a powerful hook, a statement that grabs the viewer's attention.\nAddress your viewers' concerns and questions in your video script to keep them engaged.\nMake your points in the script more engaging by sharing personal stories or experiences.\nUse metaphors and analogies to help viewers better understand your points and keep them engaged.\nWhen delivering a call to action in your script, emphasise the importance and value of the next step for the viewer.\nGive your viewers time to absorb information by breaking your script into manageable segments and delivering clear, concise points.\nGood hooks are crucial for retaining viewers from the start. \nQuestion hooks, statement hooks, and metaphor hooks are effective strategies. \nEngaging storytelling throughout the video enhances viewer interest and retention. \n"
            }
        ],
        max_tokens=4096,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
        )
        # accessing the output content of the OpenAI function's output
        response_message = response.choices[0].message.content
        # adding this output to the script.txt file
        script.write(response_message)
    # running a slightly different prompt over the next chunks of the text
    else: 
        response = client.chat.completions.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {
            "role": "system",
            "content": f"Use the provided information to format the file {chunk} into a YouTube Script"
            },
            {
            "role": "user",
            "content": "Address your viewers' concerns and questions in your video script to keep them engaged.\nMake your points in the script more engaging by sharing personal stories or experiences.\nUse metaphors and analogies to help viewers better understand your points and keep them engaged.\nWhen delivering a call to action in your script, emphasise the importance and value of the next step for the viewer.\nGive your viewers time to absorb information by breaking your script into manageable segments and delivering clear, concise points.\nOverloading viewers with multiple calls to action creates decision fatigue so avoid this. \nSuccessful call to actions mimic binge-watching behavior like Netflix series cliffhangers. \nUse subtle transition lines to lead into calls to action seamlessly. \nEnd with a clear directive to watch the next video, fostering longer viewing sessions. \n"
            }   
        ],
        max_tokens=4096,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
        )
        # accessing the output content of the OpenAI function's output
        response_message = response.choices[0].message.content
        # adding this output to the script.txt file
        script.write(response_message)

# reading the script file 
script_text = script.read()
# copying the script to clipboard
pyperclip.copy(script_text)