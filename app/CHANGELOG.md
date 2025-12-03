# Changelog - Récy&Co

## [Sprint 1] Consolidation Backend - Décembre 2024

### 🔄 Modifié - Relations Database avec backref (03/12/2024)

**Contexte** :
- Refactorisation des relations SQLAlchemy pour réduire la redondance. (DRY)

**Changements** :
- Conversion de back_populates vers backref pour toutes les relations
- Réduction de 50% du code de relations
- Correction : retrait de `autoincrement=True` sur les clés étrangères dans les tables de liaison (UserBadge, UserInventory)

**Bénéfices** :
- Code plus maintenable (une seule définition par relation)
- Risque d'incohérence éliminé (impossible d'avoir des noms qui ne correspondent pas)
- Facilite les futures modifications de la structure de données

**Tests** :
- ✅ Connexion utilisateur
- ✅ Jeu et sauvegarde de scores
- ⏳ Badges (à tester en Sprint 2)
- ⏳ Shop (à tester en Sprint 2)

**Concept appris** :
- `backref` génère automatiquement la relation inverse, évitant de définir les deux côtés manuellement.
