from db import db
from db.models import Badge
from app import app

# script : python3 seed_badges.py
# Attention à mettre à jour badge_rule dans badge_service

badges_data = [
    # --- Badges ludiques (enfants) ---
    {
        "code": "TRIEUR_MALIN",
        "label": "Trieur malin 🦝",
        "description": "Trie au moins 10 objets correctement"
    },
    {
        "code": "TRIEUR_FUTE",
        "label": "Trieur futé 🧩",
        "description": "Trie au moins 40 objets correctement"
    },
    {
        "code": "TRIEUR_PROPRET",
        "label": "Trieur propret 🧽",
        "description": "Trie au moins 60 objets correctement"
    },
    {
        "code": "TRIEUR_CHAMPION",
        "label": "Trieur champion 🏆",
        "description": "Atteins 80 points cumulés"
    },
    {
        "code": "TRIEUR_RAPIDE",
        "label": "Trieur rapide ⏱️",
        "description": "Trie un objet en moins de 2 secondes"
    },
    {
        "code": "TRIEUR_JOUEUR",
        "label": "Trieur joueur 🎲",
        "description": "Joue avec au moins 20 objets"
    },
    {
        "code": "AMI_DE_RECY",
        "label": "Ami de Recy 🦝",
        "description": "Atteins 25 points cumulés"
    },

    # --- Badges progression sérieuse ---
    {
        "code": "FIRST_GAME",
        "label": "Première partie",
        "description": "Joue et réussis ton premier geste"
    },
    {
        "code": "PERFECT_RUN",
        "label": "Sans faute",
        "description": "Réussis une série parfaite sans erreurs"
    },
    {
        "code": "TRIEUR_NOVICE",
        "label": "Trieur novice",
        "description": "Atteins 30 points cumulés"
    },
    {
        "code": "TRIEUR_DEBUTANT",
        "label": "Trieur débutant",
        "description": "Atteins 50 points cumulés"
    },
    {
        "code": "TRIEUR",
        "label": "Trieur",
        "description": "Atteins 70 points cumulés"
    },
    {
        "code": "TRIEUR_APPLIQUE",
        "label": "Trieur appliqué",
        "description": "Atteins 100 points cumulés"
    },
    {
        "code": "200_POINTS",
        "label": "Score 200 points",
        "description": "Atteins 200 points cumulés"
    },
    {
        "code": "TRIEUR_ASSIDU",
        "label": "Trieur assidu",
        "description": "Atteins 300 points cumulés"
    },
    {
        "code": "400_POINTS",
        "label": "Score 400 points",
        "description": "Atteins 400 points cumulés"
    },
    {
        "code": "TRIEUR_CONFIRME",
        "label": "Trieur confirmé",
        "description": "Atteins 500 points cumulés"
    },

    # --- Badge spécial collectionneur ---
    {
        "code": "PETIT_COLLECTIONNEUR",
        "label": "Petit collectionneur",
        "description": "Obtiens au moins 5 badges"
    }
]

if __name__ == "__main__":
    with app.app_context():
        for data in badges_data:
            if not db.session.query(Badge).filter_by(code=data["code"]).first():
                badge = Badge(**data)
                db.session.add(badge)
        db.session.commit()
        print("✅ Tous les badges ont été insérés dans la base de données !")
