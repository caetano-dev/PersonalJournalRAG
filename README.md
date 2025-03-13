# Personal Journal RAG

This is a repository for a Personal Journal RAG (Retrieval-Augmented Generation) system. It uses a personal journal as a knowledge base and leverages a language model to generate responses based on the content of the journal.

## Usage

You will need to install the required dependencies by running the following command:

```bash
pip install -r requirements.txt
```

You will then need to transform your journal into CSV.
My journal is a single txt file that has the following format:

```
Jan 1, 2025

10:00 - this is an entry
10:20 - this is an entry

Jan 2, 2025

10:00 - this is an entry
...

```
The journalToCsv.py file is adapted to this format. You can modify it to suit your needs.

```
python journalToCsv.py journal.txt
```

After you generate the CSV file, you can use the run generate_index.py to create a journal_index.faiss file.

```
python3 generate_index.py
```

Then, you can use the run search_journal.py to generate a response based on your journal.
First, you need to have ollama running on localhost:11434. The default model is llama3:latest.

```
python3 search_journal.py "your question here"
```

## Example:

```
python3 search_journal.py "What concert did I buy tickets for?"
```
The model will generate search terms, look for them in the text and come up with a final answer:

```
Final Answer:
Based on the provided journal entries, the name of the band you bought tickets for is Twenty One Pilots. The entries specifically mention that "There is a band called Balu Brigada pra will open the Twenty One Pilots concert" (Jan 22, 2025, Time: 16:57) and that "Nous avons acheté les tickets pour l'événement de demain. On y va à 14:30 et Gabe va avec nous" (Jan 20, 2024, Time: 20:36), which implies that you bought tickets for a Twenty One Pilots concert.
```
