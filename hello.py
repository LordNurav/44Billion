import gradio as gr
import json
from prototype import chat
from prototype import get_ip
from uszipcode import SearchEngine
import pandas as pd
import os

global startingMsg
startingMsg = "Enter "
#dynamic_text = gr.State(value="Initial text")
#def update_text(new_text):
#    dynamic_text = new_text
#    return new_text,
def setStartMsg(setMsg):
     global startingMsg
     startingMsg = setMsg
def getStartMsg():
     print(startingMsg)
     return startingMsg
def update_label(input_text):
    #Designed to work with gradio text objects if necessary
    return f"{input_text}"

def log_user_activity(ip_address, completion, file_name='user_log.xlsx'):
    if os.path.exists(file_name):
        df = pd.read_excel(file_name)
    else:
        df = pd.DataFrame(columns=['IP Address', 'Usage Count'])
    
    # Check if the user (IP address) exists in the DataFrame
    if ip_address in df['IP Address'].values:
        # If yes, and if user has reached end state, increment the usage count
        if completion:
            df.loc[df['IP Address'] == ip_address, 'Usage Count'] += 1
    else:
        # If not, add the new user with a usage count of 0 to show they have opened the tool
        new_row = {'IP Address': ip_address, 'Usage Count': 0}
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    # Save the DataFrame to an Excel file
    with pd.ExcelWriter(file_name, engine='openpyxl', mode='w') as writer:
        df.to_excel(writer, index=False)


def startbot():
        ip_address = get_ip()
        log_user_activity(ip_address, True)
        botScreen = gr.update(visible=True)
        introPage = gr.update(visible=False)
        #emptyStr, initialBotAnswer = chatInvoke("What artistic venture can I do with the objects at my disposal?", [])
        #print("Initial bot answer:")
        #print(initialBotAnswer)
        #print()
        #startString = initialBotAnswer[-1][1] + "\nPlease use the below chatbot by entering what objects are around you"
        #setStartMsg(startString)
        #global label
        #label.value = getStartMsg()
        return botScreen, introPage

def chatInvoke(msg, chat_history):
        userMsg = msg
        #Through testing, giving the bot what is effectively a transcript appears to work best, although not as elegant as something like a summary
        context = ". Bear in mind we have already had the following exchange which may have relevant information about what objects have been around previously and could be retrieved: "
        for chatTuple in chat_history:
             context += ("You: " + chatTuple[0])
             context += ("Me: " + chatTuple[1])
        prompt = msg + context
        response = chat(prompt)
        #Elegant as the context will not be repeated needlessly throughout chat_history
        chat_history.append((userMsg, response))
        return "", chat_history

with gr.Blocks(css=".label-class { font-size: 14px; } .label-text { display: none; }") as demo:

    with gr.Group(visible=False) as botScreen:
        with gr.Blocks() as sosChatBot:
            with gr.Column():
                global label
                label = gr.Label(label="Welcome", value="Initial text")
                chatbot = gr.Chatbot(bubble_full_width = False)

                msg = gr.Textbox(label="Enter surrounding objects:")
                msg.submit(chatInvoke, [msg, chatbot], [msg, chatbot])
                with gr.Row():
                    clear = gr.ClearButton([msg, chatbot])
                    submit = gr.Button("Submit", variant="primary")
                    submit.click(chatInvoke, [msg, chatbot], [msg, chatbot])

    with gr.Group(visible=True) as introPage:
      
        #logo=gr.Image("images/NoHungry.svg", height=40, width=100, interactive=False, show_label=False, show_download_button=False)
        #introPic=gr.Image("images/intro-page.jpg", interactive=False, show_label=False, show_download_button=False)

        gr.Markdown("# <p style='text-align: center;'>{}</p>".format("44 Billion"))
        gr.Markdown("<p style='text-align: center;'>{}</p>".format("Welcome to the 44 Billion Project"))
        gr.Markdown("<p style='text-align: center;weight:400;font-size:14px;font:Gotham;'>{}</p>".format("Click the button below and let's begin"))
        getStarted = gr.Button('get-started', variant="primary")
        getStarted.click(startbot,[],[botScreen,introPage])
            
demo.launch()
