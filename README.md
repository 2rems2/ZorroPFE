# PFE Zorro : La génération de texte

## Contexte

Ce script a été développé dans le cadre d’un projet de génération automatique de messages de soutien en réponse à des témoignages de harcèlement (racisme, homophobie, sexisme, etc.).  
Il utilise un modèle de langage pré-entraîné (**Mistral-7B-Instruct**) et est conçu pour fonctionner directement dans **Google Colab**.

L’objectif est de fournir des réponses bienveillantes, rédigées en français, adaptées à différents types de situations.  
Il intègre également une phase d’évaluation automatique des réponses générées ainsi qu’un nettoyage automatique de textes contenant des phrases en anglais.

---

## Fonctionnalités

- Chargement interactif d’un fichier de ressources `ressources_simple.json` pour proposer des liens utiles par type de harcèlement.  
- Génération de messages empathiques et conseils d’action.  
- Évaluation automatique avec COMET + BERTScore.  
- Traduction automatique des phrases résiduelles en anglais vers le français.  
- Exemples de cas concrets et scores d'évaluation.

---

## Utilisation sur Google Colab

Le script notebook est **prêt à l’emploi** sur Google Colab. Il contient tous les blocs nécessaires pour :

1. Installer les bibliothèques.  
2. Télécharger le modèle et le tokenizer.  
3. Charger les ressources.  
4. Générer des exemples de réponses.  
5. Évaluer leur qualité.

Aucun ajustement n’est requis sauf :

- **Ajouter votre token HuggingFace** dans la ligne suivante :

```python
login(token="")
```
# ATTENTION à la compatibilité

Pour éviter des erreurs de compatibilité entre `transformers`, `torch`, `accelerate` et `numpy`, il est recommandé d’installer la version suivante de NumPy :

```bash
pip install numpy==1.26.4
```

Des incompatibilités ont été observées avec des versions plus récentes dans certains environnements, notamment en usage GPU sur Colab.

---

## Dépendances principales

Le script installe automatiquement les bibliothèques suivantes :

```bash
pip install --upgrade pip
pip install torch torchvision torchaudio
pip install transformers accelerate
pip install bert-score
pip install unbabel-comet
pip install langdetect
```

---

## Ressources nécessaires

- Un fichier `ressources_simple.json` contenant un dictionnaire de liens utiles par type de harcèlement.
- Un compte HuggingFace avec un token d’accès gratuit.
- Une machine compatible GPU (**Google Colab** recommandé pour l'exécution).

---

## Données sensibles

**Attention à ne pas partager votre token HuggingFace en clair** dans un script partagé publiquement.

---

## Exemple d’appel

```python
generate_response_fr(
    user_message="On m’a dit que j’étais une honte pour ma famille à cause de mon orientation.",
    abuse_type="homophobie",
    is_abuse=1
)
```

---

## Licence

Usage **académique ou pédagogique uniquement**.  
Merci de **citer ce projet** en cas d’utilisation.

Rabemananjara Joëlla - joella.rabe@icloud.com

Renaudin Rémi - renaudinremi2002@gmail.com
