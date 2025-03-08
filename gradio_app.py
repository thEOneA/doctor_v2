from dotenv import load_dotenv
load_dotenv()

import gradio as gr
from brain_of_the_doctor import encode_image, analyze_image_with_query

# System prompt for the doctor persona
system_prompt = """You have to act as a professional doctor, I know you are not but this is for learning purposes. 
What's in this image? Do you find anything medically concerning? If you suggest a differential diagnosis, suggest some remedies.
Don't add numbers or special characters. Your response should be a concise paragraph in plain language as if answering a patient directly.
"""

# Use Gradio State for per-session history
def chat_function(message, history, image_filepath=None):
    """
    Process user input and image, generating a text response.
    History is stored per session using Gradio State, ensuring privacy.
    """
    # Initialize history if None (first message in session)
    if history is None:
        history = []

    if image_filepath:
        # Encode the uploaded image
        encoded_img = encode_image(image_filepath)
        # Add image to history with HTML for display
        img_html = f'<img src="data:image/jpeg;base64,{encoded_img}" style="max-width: 200px;"/>'
        content = f"{message if message.strip() else 'Image uploaded'}\n{img_html}" if message.strip() else img_html
        history.append({"role": "user", "content": content})

        # Analyze image with system prompt
        response = analyze_image_with_query(query=system_prompt, encoded_image=encoded_img)
        history.append({"role": "assistant", "content": response})

        return history

    elif message.strip():
        # Handle text-only input
        history.append({"role": "user", "content": message})
        
        if history and any("img" in msg["content"] for msg in history):
            # If an image exists in history, include it in the query
            last_image_msg = next(msg for msg in reversed(history) if "img" in msg["content"])
            encoded_img = last_image_msg["content"].split('base64,')[1].split('"')[0]
            response = analyze_image_with_query(query=system_prompt + " " + message, encoded_image=encoded_img)
        else:
            response = "Please upload an image so I can analyze your condition."

        history.append({"role": "assistant", "content": response})
        return history

    return history

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
        # State to store per-session history
        history_state = gr.State(value=None)

        # Chatbot UI
        chatbot = gr.Chatbot(label="LLVM Doctor_Nick Shin 申东勋 신동훈_Fudan University", type="messages", elem_classes="chatbot")
        msg = gr.Textbox(placeholder="Ask anything or upload an image")
        image_input = gr.Image(type="filepath")

        submit_btn = gr.Button("Submit")

        # Clear button to reset history for the current session
        clear_btn = gr.Button("Clear Chat")

        submit_btn.click(
            fn=chat_function,
            inputs=[msg, history_state, image_input],
            outputs=chatbot
        )

        def clear_inputs():
            return "", None

        submit_btn.click(
            fn=clear_inputs,
            outputs=[msg, image_input]
        )

        clear_btn.click(
            fn=lambda: (None, []),
            outputs=[history_state, chatbot]
        )

    return demo

if __name__ == "__main__":
    app = create_chat_interface()
    app.launch()