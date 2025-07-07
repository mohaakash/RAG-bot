import ollama
import os
from extractor import extract_text_from_folder
from vector_database import VectorDatabase
from colorama import Fore, Style, init
from tqdm import tqdm

init(autoreset=True)

EMBEDDING_MODEL = 'hf.co/CompendiumLabs/bge-base-en-v1.5-gguf'
LANGUAGE_MODEL = 'gemma3'


from colorama import init, Fore, Style

# Initialize colorama
init()

# Main ASCII art
ascii_art = r"""
____      _    ____   ____   ___ _____ 
|  _ \    / \  / ___| | __ ) / _ \_   _|
| |_) |  / _ \| |  _  |  _ \| | | || |  
|  _ <  / ___ \ |_| | | |_) | |_| || |  
|_| \_\/_/   \_\____| |____/ \___/ |_|  
"""

# Old monitor-style robot head ASCII art
monitor_head = r"""
  _______________________________
 / \                             \.
|   |                            |.
 \_ |                            |.
    |  .-------.          .-.    |.
    |  |       |   _      | |    |.
    |  |   O   |  (_)     | |    |.
    |  |       |  /|\     '-'    |.
    |  '-------'   ^            |.
    |                            |.
    |                 ___        |.
    |      \   /\    /   \       |.
    |       \_/  \__/     \      |.
    |                            |.
    |   _________________________|___
    |  /                            /.
    \_/____________________________/.
"""

# Combine the ASCII arts
combined_art = ascii_art + monitor_head

# Color the combined art cyan and print
print(Fore.CYAN + combined_art + Style.RESET_ALL)

# File Loader Menu
def load_files_menu():
    while True:
        print("\nFile Loading Menu:")
        print("1. Load all files from folder")
        print("2. Load a specific file")
        print("3. Exit")

        choice = input("Choose an option: ")

        if choice == '1':
            folder_path = input("Enter folder path: ")
            dataset = extract_text_from_folder(folder_path)
            break
        elif choice == '2':
            file_path = input("Enter full file path: ")
            dataset = extract_text_from_folder(os.path.dirname(file_path), recursive=False)
            break
        elif choice == '3':
            exit()
        else:
            print("Invalid choice. Try again.")

    print(f"Loaded {len(dataset)} chunks.")
    return dataset

# Load dataset and rebuild Vector DB
dataset = load_files_menu()

vector_db = VectorDatabase()

print(f"Building vector database with {len(dataset)} chunks...")
for chunk in tqdm(dataset, desc="Processing Chunks", unit="chunk"):
    embedding = ollama.embed(model=EMBEDDING_MODEL, input=chunk)['embeddings'][0]
    vector_db.add(chunk, embedding)

vector_db.save()
print(f"Vector database saved with {len(vector_db.chunks)} chunks.")

# Continuous Chat Loop
print("\n=== Chat Mode ===")
while True:
    input_query = input(f"\n{Fore.YELLOW}You: {Style.RESET_ALL}").strip()
    if input_query.lower() in ['exit', 'quit']:
        print("Goodbye!")
        break

    query_embedding = ollama.embed(model=EMBEDDING_MODEL, input=input_query)['embeddings'][0]
    retrieved_knowledge = vector_db.search(query_embedding)

    if not retrieved_knowledge:
        print("Sorry, I couldn't find any relevant information.")
        continue

    context = '\n'.join(f'- {chunk}' for chunk, _ in retrieved_knowledge)
    instruction_prompt = f"""You are a helpful chatbot.
Only use the following pieces of information to answer. Do not make up facts:
{context}
"""

    stream = ollama.chat(
        model=LANGUAGE_MODEL,
        messages=[
            {'role': 'system', 'content': instruction_prompt},
            {'role': 'user', 'content': input_query},
        ],
        stream=True,
    )

    print(f"{Fore.CYAN}\nAI Bot:{Style.RESET_ALL} ", end='', flush=True)
    for chunk in stream:
        print(chunk['message']['content'], end='', flush=True)
    print()  # Newline after bot response
