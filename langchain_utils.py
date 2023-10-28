from langchain import PromptTemplate, LLMChain
from langchain.llms import CTransformers
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from data.list_genre import list_genres
import re

def init_llm() -> LLMChain:
    llm = CTransformers(model="TheBloke/Llama-2-7B-Chat-GGML", model_file = 'llama-2-7b-chat.ggmlv3.q2_K.bin', callbacks=[StreamingStdOutCallbackHandler()])
    template = """
        [INST] <<SYS>>
        I give you a sentence, answer in a very specific way.
        The objective is : based on a sentence describing a mood, I need get a list of characteristics allowing me to generate a playlist accordingly.
        I want you to format the answer this exact way:
        "target_acousticness: x,
        target_danceability: x,
        target_energy: x,
        target_instrumentalness: x,
        target_speechiness: x,
        genre: x"
        For parameters that start with "target_", replace the "x" with a value between 0.0 and 1.0 that you consider the most appropriate based on my sentence
        For the "genre" parameter, replace the "x" with the music genre you think is best suited from the following list : {list_genres}.
        So, for each sentence I will send, I want you to respond ONLY in the above format. NO OTHER TEXT, NO INTRO OR OUTRO MESSAGE.
        <</SYS>>
        {text}[/INST]
    """
    prompt = PromptTemplate(template=template, input_variables=["list_genres","text"])
    llm_chain = LLMChain(prompt=prompt, llm=llm)

    return llm_chain

def run_llm_on_text(input_phrase: str) -> str:
    llm_chain = init_llm()
    response = llm_chain.run(list_genres=list_genres, text=input_phrase)
    return response

def parse_response(response: str) -> str:
    # Normalize the string: remove commas, spaces, and convert to lowercase
    normalized_string = response.replace(',', '').replace(' ', '').replace('\n', '').lower()

    def extract_value(pattern, input_str, key):
        match = re.search(pattern, input_str)
        if not match:
            raise ValueError(f"Failed to extract {key} from the response.")
        return match.group(1)

    # Extract values using regular expressions
    target_acousticness = float(re.search(r'target_acousticness:([\d.]+)', normalized_string).group(1))
    target_danceability = float(re.search(r'target_danceability:([\d.]+)', normalized_string).group(1))
    target_energy = float(re.search(r'target_energy:([\d.]+)', normalized_string).group(1))
    target_instrumentalness = float(re.search(r'target_instrumentalness:([\d.]+)', normalized_string).group(1))
    target_speechiness = float(re.search(r'target_speechiness:([\d.]+)', normalized_string).group(1))
    genre = extract_value(r"genre:'?([a-z]+)'?", normalized_string, "genre")

    # Create the dictionary
    mood_data = {
        "target_acousticness": target_acousticness,
        "target_danceability": target_danceability,
        "target_energy": target_energy,
        "target_instrumentalness": target_instrumentalness,
        "target_speechiness": target_speechiness,
        "genre": genre
    }

    return mood_data