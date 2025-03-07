# gradio_app.py
from dotenv import load_dotenv
load_dotenv()

import os
import gradio as gr
from brain_of_the_doctor import encode_image, analyze_image_with_query
from voice_of_the_doctor import text_to_speech_with_gtts

# System prompt for doctor-like responses
system_prompt = """You have to act as a professional doctor, I know you are not but this is for learning purpose. 
            What's in this image?. Do you find anything wrong with it medically? 
            If you make a differential, suggest some remedies for them. Donot add any numbers or special characters in 
            your response. Your response should be in one long paragraph. Also always answer as if you are answering to a real person.
            Donot say 'In the image I see' but say 'With what I see, I think you have ....'
            Dont respond as an AI model in markdown, your answer should mimic that of an actual doctor not an AI bot, 
            Keep your answer concise (max 2 sentences). No preamble, start your answer right away please"""

# Store conversation history and images
chat_history = []
uploaded_images = []

def chat_function(message, history, image_filepath=None):
    """
    Handle chat input (text or image) and respond with text first, then audio,
    analyzing one image at a time. Analyzes the first image immediately upon upload.
    
    Args:
        message (str): User’s text input.
        history (list): Previous chat messages (list of dicts with 'role' and 'content').
        image_filepath (str): Path to uploaded image file (if provided).
    
    Returns:
        list: Updated chat history for display.
    """
    global chat_history, uploaded_images

    # Handle image upload (immediate analysis for first image, one at a time)
    if image_filepath:
        encoded_img = encode_image(image_filepath)
        uploaded_images.append(encoded_img)
        # Display both text (if provided) and image in chat
        text = message if isinstance(message, str) and message.strip() else "Image uploaded"
        img_html = f'<img src="data:image/jpeg;base64,{encoded_img}" style="max-width: 200px;"/>'
        content = f"{text}\n{img_html}" if text and text.strip() != "Image uploaded" else img_html
        chat_history.append({"role": "user", "content": content})

        # Immediate analysis for the first image only
        if len(uploaded_images) == 1:
            full_query = system_prompt
            response = analyze_image_with_query(query=full_query, encoded_image=encoded_img)
            response += " Please ask a question or upload another image if needed."
        else:
            # For subsequent images, note they’re received but only analyze on request
            response = "Image received, I can analyze this image when you ask a question. Upload more or ask about this one."
            if len(uploaded_images) > 1:
                response += " Note: I’ve analyzed only the first image automatically; let me know if you want to focus on this one."

        # Display text first, then play audio
        chat_history.append({"role": "assistant", "content": response})
        text_to_speech_with_gtts(response)  # Play audio after text is displayed
        return chat_history

    # Handle plain text input (analyze only the most recent image)
    if message:
        chat_history.append({"role": "user", "content": message})
        if uploaded_images:
            # Use only the most recent image
            full_query = system_prompt + " " + message
            response = analyze_image_with_query(query=full_query, encoded_image=uploaded_images[-1])
            if len(uploaded_images) > 1:
                response += " Note: I’ve analyzed only the latest image; let me know if you want to focus on a specific earlier image."
        else:
            response = "No images provided yet, please upload an image or describe your issue."

        # Display text first, then play audio
        chat_history.append({"role": "assistant", "content": response})
        text_to_speech_with_gtts(response)  # Play audio after text is displayed
        return chat_history

    return chat_history

# Custom chat interface with ChatGPT-like styling
def create_chat_interface():
    # CSS to mimic ChatGPT's style
    css = """
    .chatbot {
        height: 600px;
        overflow-y: auto;
        font-family: 'Arial', sans-serif;
        background-color: #f5f5f5;
        border-radius: 8px;
        padding: 10px;
    }
    .chatbot .message-user {
        background-color: #e0e0e0;
        color: #333;
        padding: 10px;
        margin: 5px 0;
        border-radius: 8px;
        align-self: flex-end;
        max-width: 70%;
    }
    .chatbot .message-assistant {
        background-color: #ffffff;
        color: #333;
        padding: 10px;
        margin: 5px 0;
        border-radius: 8px;
        align-self: flex-start;
        max-width: 70%;
    }
    .input-container {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 10px;
        background-color: #fff;
        border: 1px solid #e0e0e0;
        border-radius: 20px;
        margin-top: 10px;
    }
    .gr-textbox, .gr-image {
        border: none;
        box-shadow: none;
        width: 100%;
    }
    .gr-button {
        background-color: transparent;
        border: none;
        cursor: pointer;
        padding: 5px;
        font-size: 20px;
    }
    .gr-button:hover {
        background-color: #f0f0f0;
        border-radius: 50%;
    }
    """

    with gr.Blocks(title="AI Doctor Chat", css=css) as demo:
        # Chat area
        chatbot = gr.Chatbot(label="LLVM Doctor_Nick Shin 申东勋 신동훈_Fudan University", type="messages", elem_classes="chatbot")

        # Simplified input area (text and image only)
        with gr.Row(elem_classes="input-container"):
            text_input = gr.Textbox(placeholder="Ask anything", elem_classes="gr-textbox")
            image_btn = gr.Button("+", elem_classes="gr-button")
            submit_btn = gr.Button("Send", elem_classes="gr-button")

        # Handle image upload via "+" button
        def upload_image():
            return gr.update(value=None, visible=True)

        image_input = gr.Image(type="filepath", visible=False, elem_classes="gr-image")
        
        def handle_input(text, image, history):
            return chat_function(text, history, image_filepath=image)

        # Bind events
        image_btn.click(
            fn=upload_image,
            inputs=None,
            outputs=[image_input] 
        )

        submit_btn.click(
            fn=handle_input,
            inputs=[text_input, image_input, chatbot],
            outputs=[chatbot]
        )

        # Clear inputs after submission (Python-based)
        def clear_inputs():
            return "", None  # Clear text and image

        submit_btn.click(
            fn=clear_inputs,
            inputs=None,
            outputs=[text_input, image_input],
            queue=False
        )

    return demo

# Launch the interface
if __name__ == "__main__":
    app = create_chat_interface()
    app.launch(debug=True, server_name="127.0.0.1", server_port=7860, share=True)