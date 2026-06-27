import gradio as gr

def greet(name, is_morning, temperature):
    salutation = "Good morning" if is_morning else "Good evening"
    greeting = f"{salutation} {name}. It is {temperature} degrees today."
    return greeting

demo = gr.Interface(
    fn=greet,
    inputs=[
        gr.Textbox(label="Your Name"),
        gr.Checkbox(label="Is it Morning?"),
        gr.Slider(0, 100, label="Temperature")
    ],
    outputs="text",
)

demo.launch()