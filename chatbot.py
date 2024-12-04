################ SEGUNGA VERSÃO MAIS AVANÇADA, RECONHECIMENTO SEM DICIONÁRIO PARA COLUNAS
################ ATIVIDADE: ADICIONAR CHAMADA DA API OU TABELA, E RANDOMIZAÇÃO DAS FRASES DE RESPOSTA.
import customtkinter as ctk
import spacy
from difflib import SequenceMatcher
import requests
from collections import defaultdict
import csv

# Carregar o modelo de português
nlp = spacy.load('pt_core_news_sm')

class Chatbot:
    def __init__(self, master):
        self.master = master
        master.title("Artemis")
        master.geometry("600x500")

        # Configuração da janela
        master.grid_columnconfigure(0, weight=1)
        master.grid_rowconfigure(0, weight=1)
        master.grid_rowconfigure(1, weight=0)
        master.grid_rowconfigure(2, weight=0)

        ctk.set_appearance_mode("dark")  # "light" ou "dark"
        ctk.set_default_color_theme("dark-blue")

        # Área de texto
        self.text_area = ctk.CTkTextbox(master, width=500, height=300, wrap="word")
        self.text_area.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.text_area.insert(ctk.END, "Olá! Eu sou a Artemis, sua assistente virtual. Como posso te ajudar hoje?\n")
        self.text_area.configure(state="disabled")

        # Campo de entrada
        self.entry = ctk.CTkEntry(master, width=400, placeholder_text="Digite sua pergunta aqui...")
        self.entry.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.entry.bind("<Return>", self.process_input)

        # Botão de envio
        self.send_button = ctk.CTkButton(master, text="Enviar", fg_color="blue", command=self.process_input)
        self.send_button.grid(row=2, column=0, padx=20, pady=10)

        # Dados da tabela
        self.url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQIVaHcTlB62Tj29WEEhYXGAFx1mhwxstWtMAcvnsUemD_acuLrooLn3MC-T2KOGYexC_ctIPsKZPVx/pub?output=csv&gid=2900213"
        self.response = requests.get(self.url)
        self.response.raise_for_status()
        self.csv_data = csv.DictReader(self.response.text.splitlines())
        self.data_dict = defaultdict(list)
        for row in self.csv_data:
            for key, value in row.items():
                self.data_dict[key].append(value)
        self.data_dict = dict(self.data_dict)

    def process_input(self, event=None):
        user_input = self.entry.get()
        if not user_input:
            return

        self.text_area.configure(state="normal")
        self.text_area.insert(ctk.END, "Você: " + user_input + "\n")

        response = self.get_bot_response(user_input)
        self.text_area.insert(ctk.END, "Artemis: " + response + "\n")

        self.text_area.configure(state="disabled")

        self.entry.delete(0, ctk.END)

    def get_bot_response(self, user_input):
        # Processar o input com spaCy
        doc = nlp(user_input.lower())
        # Extrair tokens lematizados sem pontuações e palavras de parada
        tokens = [token.lemma_ for token in doc if not token.is_punct and not token.is_stop]

        # Tentar encontrar uma correspondência com as colunas
        for column in self.data_dict.keys():
            # Lematizar o nome da coluna
            column_lemma = nlp(column)[0].lemma_
            # Verificar se a coluna está nos tokens
            if column_lemma in tokens:
                column_data = self.data_dict[column]
                response = f"Os dados da coluna '{column}' são: {', '.join(map(str, column_data))}."
                return response
            else:
                # Verificar similaridade entre tokens e nome da coluna
                for token in tokens:
                    similarity = self.similarity(token, column_lemma)
                    if similarity > 0.8:
                        column_data = self.data_dict[column]
                        response = f"Os dados da coluna '{column}' são: {', '.join(map(str, column_data))}."
                        return response

        # Respostas simples baseadas em palavras-chave
        if any(greeting in tokens for greeting in ["olá", "oi"]):
            return "Olá! Em que posso ajudar?"
        elif any(farewell in tokens for farewell in ["tchau", "adeus", "até logo"]):
            return "Até mais! Se precisar de algo, estou aqui."
        elif "ajuda" in tokens or "socorro" in tokens:
            return "Claro! Estou aqui para ajudar. O que você precisa?"
        else:
            return "Desculpe, não entendi. Poderia reformular a pergunta?"

    def similarity(self, a, b):
        return SequenceMatcher(None, a, b).ratio()

if __name__ == "__main__":
        root = ctk.CTk()
        chatbot = Chatbot(root)
        root.mainloop()