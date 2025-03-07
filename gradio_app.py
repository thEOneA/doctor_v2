from dotenv import load_dotenv
load_dotenv()

import gradio as gr
from brain_of_the_doctor import encode_image, analyze_image_with_query
from voice_of_the_doctor import text_to_speech_with_gtts

system_prompt = """You have to act as a professional doctor, I know you are not but this is for learning purposes. 
What's in this image? Do you find anything medically concerning? If you suggest a differential diagnosis, suggest some remedies.
Don't add numbers or special characters. Your response should be a concise paragraph in plain language as if answering a patient directly.
"""

chat_history = []
uploaded_images = []

def chat_function(message, history, image_filepath=None):
    global chat_history, uploaded_images

    if image_filepath:
        encoded_img = encode_image(image_filepath)
        uploaded_images.append(encoded_img)
        text = message if message.strip() else "Image uploaded"
        img_html = f'<img src="data:image/jpeg;base64,{encoded_img}" style="max-width: 200px;"/>'
        content = f"{text}\n{img_html}" if text != "Image uploaded" else img_html
        chat_history.append({"role": "user", "content": content})

        query = system_prompt
        response = analyze_image_with_query(query=query, encoded_image=encoded_img)
        chat_history.append({"role": "assistant", "content": response})

        text_to_speech_with_gtts(response)
        return chat_history

    elif message.strip():
        chat_history.append({"role": "user", "content": message})
        
        if uploaded_images:
            query = system_prompt + " " + message
            response = analyze_image_with_query(query=query, encoded_image=uploaded_images[-1])
        else:
            response = "Please upload an image so I can analyze your condition."

        chat_history.append({"role": "assistant", "content": response})
        text_to_speech_with_gtts(response)
        return chat_history

    return chat_history

def create_chat_interface():
    css = """
    .chatbot {
        height: 600px;
        overflow-y: auto;
        background-color: #f5f5f5;
        padding: 10px;
    }
    """

    with gr.Blocks(css=css) as demo:
        chatbot = gr.Chatbot(label="LLVM Doctor_Nick Shin 申东勋 신동훈_Fudan University", type="messages", elem_classes="chatbot")
        msg = gr.Textbox(placeholder="Ask anything or upload an image")
        image_input = gr.Image(type="filepath")

        submit_btn = gr.Button("Submit")

        submit_btn.click(
            fn=chat_function,
            inputs=[msg, chatbot, image_input],
            outputs=chatbot
        )

        def clear_inputs():
            return "", None

        submit_btn.click(
            fn=clear_inputs,
            outputs=[msg, image_input]
        )

    return demo

if __name__ == "__main__":
    app = create_chat_interface()
    app.launch()
