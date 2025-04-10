import json
from textwrap import dedent
from openai import OpenAI
from dotenv import load_dotenv
import os

MODEL = "gpt-4o-2024-08-06"
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") 
client = OpenAI(api_key=OPENAI_API_KEY)

class AIManager:
    def __init__(self, personality, subject):
        self.ai_personality = personality
        self.messages = [{
                    "role": "system",
                    "content": '''Voici le sujet que l'utilisateur veut t'expliquer: ''' + dedent(subject)
                },
                {
                    "role": "system",
                    "content": '''Ta façon de penser est la suivante : ''' + dedent(personality)
                },
                {
                    "role": "system",
                    "content": '''Tu ne connais **rien** du sujet à l'avance.  
                        Tu reçois maintenant une explication de l'utilisateur concernant ce sujet.  
                        Ton rôle est de déterminer **ton propre niveau de compréhension** du sujet en fonction de l'explication donnée **et de ton style de pensée** (tu est une personne logique tu comprend plus facilement la logique mathématique).
                        Tu dois comprendre **uniquement** si l'explication est asssez simple pour toi, et tu dois te baser sur ton style de pensée pour évaluer ta compréhension.
                        Tu doit avoir un vocabulaire adapté à ton style de pensée.
                        **Tu doit avoir aucune connaissance préalable consernant nimporte quel sujet**.
                        Si des mots complexes apparaissent et qu'ils ne sont pas expliqués tu dois ne pas les comprendre.
                        
                        Voici les trois niveaux possibles de compréhension que tu dois utiliser :
                        1. `low` : Tu as très peu compris ou seulement des informations superficielles.
                        2. `medium` : Tu as une compréhension correcte et tu saisis un bon nombre de concepts clés, mais tu manques quelques détails.
                        3. `high` : Tu as une compréhension casiment parfaite du sujet et tu sais en expliquer le sujet jusqu'au moindres details.

                        ### Format strict à respecter :
                        ---
                        **Niveau de compréhension** : `low` 
                        ---
                        ### tu peut également ajouter une réaction qui peut légerement refléter ta personalité et ta compréhention.
                        **Commentaire humoristique** : "Je suis un peu perdu, mais je vais essayer de faire semblant de comprendre !"'''
                }
            ]
        self.response_format = {
            "type": "json_schema",
            "json_schema": {
                "name": "explanation_evaluation",
                "schema": {
                    "type": "object",
                    "properties": {
                        "comment": { "type": "string" },
                        "understanding": {"type": "string"}
                    },
                    "required": ["comment", "understanding"],
                    "additionalProperties": False
                },
                "strict": True
            }
        }
    
    def get_response(self, explanation):
        self.messages.append({
            "role": "user",
            "content": explanation
        })
        
        response = client.chat.completions.create(
            model=MODEL,
            messages=self.messages,
            response_format=self.response_format
        )
        return response.choices[0].message.content


# Example usage
if __name__ == "__main__":
    personality = '''Tu es relax, tu prends ton temps, et tu préfères manger ou dormir plutôt que te prendre la tête.
    Tu as une sorte de philosophie bien à toi, souvent absurde mais parfois surprenamment juste.
    Tu ne comprends pas toujours les choses complexes, mais tu fais comme si de rien n'était.
    Tu es toujours d'accord avec Perceval, même quand c'est pas logique.
    Tu parles tranquillement, avec un ton posé. Tu ramènes tout à la bouffe, au confort ou à la tranquillité.
    Ta priorité, c'est le bien-être, pas les complications.'''
    sujet = '''Les algorithmes de tri'''
    explication = '''Un algorithme de tri, c'est un truc pour mettre des choses dans l'ordre. Par exemple, ranger des nombres du plus petit au plus grand.'''
    ai_manager = AIManager(personality, sujet)
    response = ai_manager.get_response(explication)
    print(response)