# gradio_app.py
from dotenv import load_dotenv
load_dotenv()

import os
import gradio as gr
from brain_of_the_doctor import encode_image, analyze_image_with_query

system_prompt = """
You are an AI Doctor assistant. Analyze medical images. If you see symptoms, provide possible differentials and suggest remedies. Respond naturally in one paragraph without referencing the image explicitly.
"""

# Maintain chat history
chat_history = []
uploaded_images = []

def chat_function(message, history, image_filepath=None):
    global chat_history, uploaded_images

    # Initialize chat history if not existing
    if 'chat_history' not in globals():
        global chat_history
        chat_history = []

    # Handle image upload and immediate analysis
    if image_filepath:
        encoded_img = encode_image(image_filepath)
        uploaded_images.append(encoded_img)

        content = message if message else "Image uploaded."
        chat_history.append({"role": "user", "content": content})

        full_query = system_prompt
        response = analyze_image_with_query(query=full_query, encoded_image=encoded_img)
        chat_history.append({"role": "assistant", "content": response})
        return chat_history

    # Handle text input
    if message:
        if uploaded_images:
            encoded_img = uploaded_images[-1]
            full_query = system_prompt + " " + message
            response = analyze_image_with_query(query=full_query, encoded_image=encoded_img)
        else:
            response = "Please upload an image for analysis."

        chat_history.append({"role": "user", "content": message})
        chat_history.append({"role": "assistant", "content": response})

        return chat_history

    return chat_history

# Gradio Interface
uploaded_images = []

def create_chat_interface():
    css = """
    .chatbot {
        height: 600px;
    }
    .chatbot .user, .chatbot .assistant {
        padding: 8px;
        border-radius: 10px;
        margin: 4px;
    }
    """

    with gr.Blocks(title="AI Doctor Chat", css=css) as demo:
        chatbot = gr.Chatbot(label="LLVM Doctor_Nick Shin 申东勋")
        with gr.Row():
            text_input = gr.Textbox(placeholder="Type your message here", scale=4)
            image_input = gr.Image(type="filepath", scale=1)
            submit_btn = gr.Button("Send")

        submit_btn.click(
            chat_function,
            inputs=[text_input, chatbot, image_input],
            outputs=chatbot
        )

        submit_btn.click(lambda: ("", None), None, [text_input, image_input])

    return gr.Interface(
        fn=chat_function,
        inputs=[text_input, chatbot, image_input],
        outputs=chatbot,
        allow_flagging="never",
        title="AI Doctor Assistant",
        css=css
    )

app = create_chat_interface()
app.launch()
