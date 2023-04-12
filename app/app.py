import gradio as gr
from dotenv import load_dotenv
from langchain import OpenAI, SQLDatabase, SQLDatabaseChain
from pathlib import Path

load_dotenv()
DB_PATH = Path(__file__).parents[1] / 'data/uvb.db'

def query_db(text):
    # result = generator(text, max_length=30, num_return_sequences=1)
    result = text + " " + text
    return result

examples = ["Which location has seen the highest total erythemal irradiance in March 2022?",   # noqa
            "Across all sites in Colorado, what was the sunniest day in March 2022?"]

if __name__ == "__main__":

    # Connect to the database and LLM
    db = SQLDatabase.from_uri("sqlite:///" + DB_PATH.as_posix())
    llm = OpenAI(temperature=0)
    db_chain = SQLDatabaseChain(llm=llm, database=db, verbose=False)

    # Create the gradio app interface
    app = gr.Interface(
        fn=db_chain.run,
        inputs=gr.components.Textbox(lines=5, label="Input Query"),
        outputs=gr.components.Textbox(label="Search result"),
        examples=examples
    )

    app.launch(server_name='0.0.0.0', server_port=7860, inbrowser=True)
