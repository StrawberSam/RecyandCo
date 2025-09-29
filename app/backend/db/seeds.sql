-- Nettoyage (utile si tu relances le fichier plusieurs fois en test)
DELETE FROM user_inventory;
DELETE FROM user_badges;
DELETE FROM scores;
DELETE FROM shop_items;
DELETE FROM badges;
DELETE FROM users;

-- Réinitialiser les auto-incréments
ALTER TABLE scores AUTO_INCREMENT = 1;
ALTER TABLE badges AUTO_INCREMENT = 1;
ALTER TABLE shop_items AUTO_INCREMENT = 1;

-- 1 utilisateur de test (UUID fixe)
INSERT INTO users (id, username, email, password_hash)
VALUES ('550e8400-e29b-41d4-a716-446655440000', 'samira', 'samira@example.com', 'hashed_password_123');

-- 2 badges
INSERT INTO badges (code, label, description, threshold, icon)
VALUES
('FIRST_GAME', 'Premier jeu', 'Attribué après ta première partie', NULL, 'img/badges/first_game.svg'),
('HUNDRED_POINTS', '100 Points', 'Attribué après avoir atteint 100 points', 100, 'img/badges/100_points.svg');

-- 1 item de boutique
INSERT INTO shop_items (sku, name, price, is_active)
VALUES ('HAT01', 'Chapeau Recy', 50, TRUE);

-- 1 score de test lié à l’utilisateur
INSERT INTO scores (user_id, points, correct_items, total_items, duration_ms)
VALUES ('550e8400-e29b-41d4-a716-446655440000', 10, 8, 10, 45000);

-- Attribuer un badge à l’utilisateur
INSERT INTO user_badges (user_id, badge_id, awarded_at)
VALUES ('550e8400-e29b-41d4-a716-446655440000', 1, CURRENT_TIMESTAMP);

-- Enregistrer un objet acheté par l’utilisateur
INSERT INTO user_inventory (user_id, item_id, acquired_at)
VALUES ('550e8400-e29b-41d4-a716-446655440000', 1, CURRENT_TIMESTAMP);
