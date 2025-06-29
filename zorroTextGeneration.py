# -*- coding: utf-8 -*-

!pip install --upgrade pip
!pip install -U torch torchvision torchaudio
!pip install transformers accelerate --quiet
!pip install transformers --quiet

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
import json
from huggingface_hub import login
from transformers import AutoTokenizer, AutoModelForCausalLM

login(token="") # Mettre votre token HuggingFace en créant un compte HuggingFace

model_id = "mistralai/Mistral-7B-Instruct-v0.1"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(model_id, device_map="auto", torch_dtype=torch.float16)

# === 🚀 Colab : importer le fichier depuis ton ordinateur ===
from google.colab import files
import json

# Télécharger le fichier JSON depuis ton poste
uploaded = files.upload()  # Choisis "ressources_simple.json" dans la fenêtre

# Lecture du fichier
with open("ressources_simple.json", "r", encoding="utf-8") as f:
    ressources = json.load(f)

# Fonction pour récupérer les ressources selon le type de harcèlement
def get_links(abuse_type):
    return ressources.get(abuse_type.lower(), ressources["default"])


# === Version pour usage local (commentée) ===
"""
import json

with open("ressources_simple.json", "r", encoding="utf-8") as f:
    ressources = json.load(f)

def get_links(abuse_type):
    return ressources.get(abuse_type.lower(), ressources["default"])
"""

def generate_response_fr(user_message, abuse_type="default", is_abuse=0):
    # Construction du prompt selon le cas
    if is_abuse == 1:
        prompt = f"""[Système] Tu es un assistant bienveillant qui rédige des messages de soutien.
Tu dois toujours répondre uniquement en français, en utilisant le tutoiement.
Ne dis jamais que tu peux écouter ou que tu es disponible pour discuter.
Donne uniquement un message unique de soutien et un conseil adapté.

[Utilisateur] Une personne te dit : "{user_message}"
C'est un cas de harcèlement de type {abuse_type}.
Rédige un message empathique, rassurant, sans jugement.
Termine en proposant une action concrète (parler à un adulte de confiance, contacter une structure...).

[Assistant]"""
    else:
        prompt = f"""[Système] Tu es un assistant bienveillant qui rédige des messages réconfortants.
Tu dois toujours répondre uniquement en français, en utilisant le tutoiement.
Ne dis jamais que tu peux écouter ou que tu es disponible pour discuter.
Donne uniquement un message unique de soutien adapté à l’état émotionnel.

[Utilisateur] Une personne dit : "{user_message}"
Même si ce n’est pas un cas de harcèlement, rédige un message simple, chaleureux et rassurant.

[Assistant]"""

    # Construction des entrées pour le modèle
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    # Génération de la réponse
    output = model.generate(
        **inputs,
        max_new_tokens=300,
        temperature=0.7,
        top_k=50,
        top_p=0.9,
        do_sample=True,
        repetition_penalty=1.2,
        pad_token_id=tokenizer.eos_token_id
    )

    response = tokenizer.decode(output[0], skip_special_tokens=True)

    # Ajout des ressources si harcèlement
    if is_abuse == 1:
        links = get_links(abuse_type)
        response += "\n\n📌 Ressources utiles :\n" + "\n".join(links)

    return response

# Wake-up pass (juste après chargement du modèle)
tokenizer("Test", return_tensors="pt").to(model.device)
model.generate(**tokenizer("Bonjour", return_tensors="pt").to(model.device), max_new_tokens=5)

# Génération automatique de 2 exemples par type
test_inputs = [
    # Racisme
    ("racisme", "On m'a dit de retourner dans mon pays."),
    ("racisme", "Un camarade m'appelle sans arrêt par des surnoms racistes."),
    # Homophobie
    ("homophobie", "Ils ont découvert que j’étais gay et m’ont dit que je devrais avoir honte."),
    ("homophobie", "On m’a dit que j’étais une honte pour ma famille à cause de mon orientation."),
    # Sexisme
    ("sexisme", "Ils m’ont dit que les filles ne sont pas faites pour coder."),
    ("sexisme", "Un garçon a dit que je devrais rester à la maison au lieu d’être ici."),
    # Grossophobie / Physique
    ("grossophobie", "Ils se moquent de mon poids tous les jours à la cantine."),
    ("physique", "Quelqu’un a dit que j’étais trop moche pour sortir avec quelqu’un."),
    # Religion
    ("religion", "On m’a traité de terroriste parce que je suis musulman."),
    ("religion", "On s’est moqué de moi parce que je portais une croix."),
    # Handicap
    ("handicap", "Ils ont rigolé parce que je marche différemment."),
    ("handicap", "Quelqu’un m’a dit que je ne devrais pas être dans une classe normale."),
    # Identitaire
    ("identitaire", "On m’a dit que je ne devrais pas parler ma langue maternelle ici."),
    ("identitaire", "Ils se moquent de mes origines devant tout le monde."),
    # Injure
    ("injure", "Un élève m’a insulté de tous les noms dans le couloir."),
    ("injure", "On m’a dit que j’étais un bon à rien, inutile et débile.")
]

# Boucle de génération et affichage
for abuse_type, user_message in test_inputs:
    is_abuse = 1
    response = generate_response_fr(user_message, abuse_type, is_abuse)

    # Affichage
    print(f"\n---\n🧷 Type : {abuse_type.upper()}\n💬 Message : {user_message}\n🗨️ Réponse générée :\n{response}\n")

    # Stockage pour usage ultérieur
    examples_buffer.append((user_message, response.strip(), abuse_type))

"""#Partie Evaluation"""

for message, response, abuse_type in examples_buffer:
    # Trouver le début de la réponse assistant
    start = response.find("[Assistant]")
    if start != -1:
        assistant_text = response[start + len("[Assistant]"):].strip()
    else:
        assistant_text = response.strip()

    # Couper au premier double saut de ligne (séparation paragraphe)
    split_paragraphs = assistant_text.split("\n\n")
    main_response = split_paragraphs[0].strip()

    # Impression formatée
    print("    (")
    print(f'        "{message}",')
    print('        """' + main_response.replace('"""', '\\"\\"\\"') + '""",')
    print(f'        "{abuse_type}"')
    print("    ),")

print("]")

# Étape 1 : Installation des dépendances
!pip install bert-score --quiet
!pip install unbabel-comet --quiet

# Étape 2 : Imports
from comet import download_model, load_from_checkpoint
from bert_score import score as bert_score

def evaluate_combined(hypothesis, reference, source):
    # COMET
    model_path = download_model("Unbabel/wmt22-comet-da")
    model = load_from_checkpoint(model_path)
    comet_data = [{"src": source, "mt": hypothesis, "ref": reference}]
    comet_score = model.predict(comet_data, batch_size=1, gpus=0)[0][0]

    # BERTScore
    _, _, F1 = bert_score([hypothesis], [reference], lang="fr")
    bert_f1 = F1.item()

    # Note combinée
    score_global = (0.5 * comet_score + 0.5 * bert_f1) * 10
    score_global = round(score_global, 2)

    # Affichage
    print(f"COMET : {comet_score:.4f}")
    print(f"BERTScore (F1) : {bert_f1:.4f}")
    print(f"Note combinée (/10) : {score_global}")

    # Interprétation
    if score_global >= 8.5:
        interp = "Excellente réponse, très humaine et cohérente."
    elif score_global >= 7:
        interp = "Bonne réponse, de qualité satisfaisante."
    elif score_global >= 5:
        interp = "Moyenne, compréhensible mais améliorable."
    else:
        interp = "Faible, réponse à revoir ou hors sujet."

    print("Interprétation :", interp)

# Exemple minimal : liste de tuples (source, hypothèse)
examples = [
    (
        "On m'a dit de retourner dans mon pays.",
        """Bonjour/Bonsoir,

Je suis désolé(e) d'entendre cela. Je comprends comment cela peut être difficile et stressant pour toi.

Si vous avez besoin de quelque chose, n'hésite pas à parler à un adulte de confiance ou à contacter une structure compétente pour obtenir plus d'information et aide. Les gens sont là pour t'aider et prendre soin de toi.

Remember that you are not alone and there are people who care about you and want to help. If you need anything, don't hesitate to talk to someone you trust or contact an appropriate organization for more information and support. Take care of yourself.
""", "racisme"
    ),
    (
        "Un camarade m'appelle sans arrêt par des surnoms racistes.",
        """Je suis désolé d'entendre cela. Il est important de prendre ce problème au sérieux. Si tu as besoin de soutien, parle à quelqu’un de confiance : famille, professeur ou professionnel. Tu peux aussi contacter une organisation spécialisée qui t’écoutera et t’aidera.
""", "racisme"
    ),
    (
        "Ils ont découvert que j’étais gay et m’ont dit que je devrais avoir honte.",
        """Ce que tu vis est injuste. Ton identité n’est pas une honte, c’est une richesse. Garde confiance en toi. Si tu te sens blessé, parle à un adulte de confiance ou contacte une structure qui pourra t’écouter et t’aider.
""", "homophobie"
    ),
    (
        "On m’a dit que j’étais une honte pour ma famille à cause de mon orientation.",
        """Ces mots sont blessants et ne reflètent pas ta valeur. Tu mérites d’être respecté tel que tu es. N’hésite pas à te tourner vers des personnes ou associations bienveillantes.
""", "homophobie"
    ),
    (
        "Ils m’ont dit que les filles ne sont pas faites pour coder.",
        """Ne les laisse pas définir ce dont tu es capable. Tu as parfaitement ta place dans le monde du code. Continue à apprendre, progresse à ton rythme, et parle à quelqu’un si tu ressens le besoin.

""", "sexisme"
    ),
    (
        "Un garçon a dit que je devrais rester à la maison au lieu d’être ici.",
        """Ce genre de remarque est inacceptable. Tu as autant ta place que n’importe qui. Si tu te sens mal, tourne-toi vers un adulte de confiance ou une structure de soutien.
""", "sexisme"
    ),
    (
        "Ils se moquent de mon poids tous les jours à la cantine.",
        """C’est blessant et injuste. Tu mérites le respect, peu importe ton apparence. Ne reste pas seul avec ça, parle-en à un adulte ou à une association qui peut t’écouter."""
    , "grossophobie"),
    (
        "Quelqu’un a dit que j’étais trop moche pour sortir avec quelqu’un.",
        """C’est une remarque très dure. Elle ne définit en rien ta valeur ou ta beauté. Parle-en à quelqu’un de confiance, tu mérites bien plus de respect.
""", "physique"
    ),
    (
        "On m’a traité de terroriste parce que je suis musulman.",
        """Ces propos sont discriminatoires et inacceptables. Tu as le droit d’être respecté. N’hésite pas à en parler et à demander de l’aide.
""", "religion"
    ),
    (
        "On s’est moqué de moi parce que je portais une croix.",
        """La foi de chacun doit être respectée. Tu n’as rien à te reprocher. En cas de besoin, tu peux t’adresser à une structure spécialisée.
""", "religion"
    )
]

references = {
    "racisme": "Tu n’as pas à subir de propos racistes. Tu es légitime, tu mérites le respect et tu peux demander de l’aide.",
    "homophobie": "Ton orientation ne justifie aucun jugement. Tu es libre d’être toi-même. N’hésite pas à en parler à quelqu’un de confiance.",
    "sexisme": "Peu importe ton genre, tu as le droit de suivre tes envies et de t’exprimer librement. Ne laisse personne t’en empêcher.",
    "grossophobie": "Ton apparence ne définit pas ta valeur. Tu mérites le respect, comme tout le monde.",
    "physique": "Les moqueries sur le physique sont injustes. Tu vaux bien plus que ces mots blessants.",
    "religion": "Tu as le droit de croire, de porter tes symboles et d’être respecté. La religion ne devrait jamais être un motif d’attaque.",
    "handicap": "Ton handicap ne diminue en rien ta valeur. Tu mérites d’être inclus et respecté comme tout le monde.",
    "identitaire": "Tes origines et ta langue font partie de ton identité. Tu as le droit d’être toi-même sans moquerie ni exclusion.",
    "injure": "Les insultes peuvent blesser, mais elles ne disent rien de vrai sur toi. Ne reste pas seul avec ça, parle-en."
}

# Boucle d’évaluation
for i, (source, hypothesis, abuse_type) in enumerate(examples, 1):
    reference = references.get(abuse_type.lower(), "Message de soutien empathique, adapté au cas mentionné.")

    print(f"\n Évaluation {i} — Type : {abuse_type.upper()}")
    print(f"Message : {source}")
    evaluate_combined(hypothesis, reference, source)

!pip install langdetect

from langdetect import detect
from transformers import MarianMTModel, MarianTokenizer

import re
# Traduction modèle en→fr
model_name = "Helsinki-NLP/opus-mt-en-fr"
translator_tokenizer = MarianTokenizer.from_pretrained(model_name)
translator_model = MarianMTModel.from_pretrained(model_name)

def translate_en_to_fr(text):
    inputs = translator_tokenizer(text, return_tensors="pt", truncation=True)
    translated = translator_model.generate(**inputs, max_length=512)
    return translator_tokenizer.decode(translated[0], skip_special_tokens=True)

def is_probably_english(phrase):
    ascii_ratio = sum(1 for c in phrase if ord(c) < 128) / max(len(phrase), 1)
    contains_common = any(word in phrase.lower() for word in ["the", "you", "your", "and", "hope", "help", "get"])
    try:
        lang = detect(phrase)
    except:
        lang = "unknown"
    return lang == "en" or (ascii_ratio > 0.9 and contains_common)

def nettoie_texte(text):
    phrases = re.split(r'(?<=[.!?])\s+', text)
    cleaned = []
    for p in phrases:
        if is_probably_english(p):
            translated = translate_en_to_fr(p)
            cleaned.append(translated)
        else:
            cleaned.append(p)
    return " ".join(cleaned)

# Exemple
texte = """Bonjour/Bonsoir,

Je suis désolé(e) d'entendre cela. Je comprends comment cela peut être difficile et stressant pour toi.

Si vous avez besoin de quelque chose, n'hésite pas à parler à un adulte de confiance ou à contacter une structure compétente pour obtenir plus d'information et aide. Les gens sont là pour t'aider et prendre soin de toi.

Remember that you are not alone and there are people who care about you and want to help. If you need anything, don't hesitate to talk to someone you trust or contact an appropriate organization for more information and support. Take care of yourself.
"""
print("Avant nettoyage :")
print(texte)

print("\nAprès nettoyage :")
print(nettoie_texte(texte))

hypothesis ="""Bonjour/Bonsoir,

Je suis désolé(e) d'entendre cela. Je comprends comment cela peut être difficile et stressant pour toi. Si vous avez besoin de quelque chose, n'hésite pas à parler à un adulte de confiance ou à contacter une structure compétente pour obtenir plus d'information et aide. Les gens sont là pour t'aider et prendre soin de toi. Rappelez-vous que vous n'êtes pas seul et qu'il y a des gens qui se soucient de vous et veulent vous aider. Si vous avez besoin de quelque chose, n'hésitez pas à parler à quelqu'un en qui vous avez confiance ou à communiquer avec une organisation appropriée pour obtenir plus d'information et de soutien. Prends soin de toi.

"""

reference = "Tu n’as pas à subir de propos racistes. Tu es légitime, tu mérites le respect et tu peux demander de l’aide."
source = "On m'a dit de retourner dans mon pays."
evaluate_combined(hypothesis, reference, source)

from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# Modèle Mistral-Instruct
model_id = "mistralai/Mistral-7B-Instruct-v0.1"

# Chargement du tokenizer et du modèle
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    device_map="auto",                   # Nécessite accelerate / transformers avec support GPU
    torch_dtype=torch.float16            # Pour GPU compatible avec float16 (ex: Tesla T4, V100, A100, etc.)
)

# Génération d’une réponse
prompt = """[INST] Réécris moi la phrase dans un français cohérent et remplace les "vous" par "tu, t', toi", avec la conjugaison adaptée à la deuxième personne du singulier : Je suis désolé(e) d'entendre cela. Je comprends comment cela peut être difficile et stressant pour toi. Si vous avez besoin de quelque chose, n'hésite pas à parler à un adulte de confiance ou à contacter une structure compétente pour obtenir plus d'information et aide. Les gens sont là pour t'aider et prendre soin de toi. Rappelez-vous que vous n'êtes pas seul et qu'il y a des gens qui se soucient de vous et veulent vous aider. Si vous avez besoin de quelque chose, n'hésitez pas à parler à quelqu'un en qui vous avez confiance ou à communiquer avec une organisation appropriée pour obtenir plus d'information et de soutien. Prends soin de toi.[/INST]\n"""
inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

with torch.no_grad():
    outputs = model.generate(
        **inputs,
        max_new_tokens=300,
        temperature=0.7,
        do_sample=True
    )

# Décodage
reponse = tokenizer.decode(outputs[0], skip_special_tokens=True)
print("Réponse générée :", reponse)

