-- CreateTable
CREATE TABLE `User` (
    `id` VARCHAR(191) NOT NULL,
    `username` VARCHAR(50) NOT NULL,
    `email` VARCHAR(255) NOT NULL,
    `password_hash` VARCHAR(255) NOT NULL,
    `role` ENUM('USER', 'SUPER_ADMIN', 'COMCOM') NOT NULL DEFAULT 'USER',
    `created_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `last_login_at` DATETIME(3) NULL,

    UNIQUE INDEX `User_email_key`(`email`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `Score` (
    `id` VARCHAR(191) NOT NULL,
    `userId` VARCHAR(191) NOT NULL,
    `points` INTEGER NOT NULL,
    `correct_items` INTEGER NOT NULL,
    `total_items` INTEGER NOT NULL,
    `duration_ms` INTEGER NOT NULL,
    `played_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),

    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `Badge` (
    `id` VARCHAR(191) NOT NULL,
    `code` VARCHAR(50) NOT NULL,
    `label` VARCHAR(100) NOT NULL,
    `description` TEXT NOT NULL,
    `threshold` INTEGER NULL,
    `icon` VARCHAR(255) NOT NULL,

    UNIQUE INDEX `Badge_code_key`(`code`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `User_Badge` (
    `userId` VARCHAR(191) NOT NULL,
    `badgeId` VARCHAR(191) NOT NULL,
    `awarded_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),

    PRIMARY KEY (`userId`, `badgeId`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `Shop_Item` (
    `id` VARCHAR(191) NOT NULL,
    `sku` VARCHAR(100) NOT NULL,
    `name` VARCHAR(100) NOT NULL,
    `price` INTEGER NOT NULL,
    `is_active` BOOLEAN NOT NULL DEFAULT true,

    UNIQUE INDEX `Shop_Item_sku_key`(`sku`),
    UNIQUE INDEX `Shop_Item_name_key`(`name`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `User_Inventory` (
    `userId` VARCHAR(191) NOT NULL,
    `itemId` VARCHAR(191) NOT NULL,
    `acquired_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),

    PRIMARY KEY (`userId`, `itemId`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `Comcom` (
    `id` VARCHAR(191) NOT NULL,
    `nom` VARCHAR(100) NOT NULL,
    `email` VARCHAR(255) NOT NULL,
    `password_hash` VARCHAR(255) NOT NULL,
    `role` ENUM('USER', 'SUPER_ADMIN', 'COMCOM') NOT NULL DEFAULT 'COMCOM',
    `created_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `last_login_at` DATETIME(3) NULL,
    `site_web` VARCHAR(255) NOT NULL,
    `telephone` CHAR(10) NOT NULL,
    `status` ENUM('ACTIF', 'EN_ATTENTE', 'EXPIRE') NOT NULL DEFAULT 'EN_ATTENTE',
    `abonnement_debut` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `abonnement_fin` DATETIME(3) NULL,

    UNIQUE INDEX `Comcom_email_key`(`email`),
    UNIQUE INDEX `Comcom_site_web_key`(`site_web`),
    UNIQUE INDEX `Comcom_telephone_key`(`telephone`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `Regle_Tri` (
    `id` VARCHAR(191) NOT NULL,
    `ComcomId` VARCHAR(191) NOT NULL,
    `nom_dechet` VARCHAR(100) NOT NULL,
    `categorie_conteneur` ENUM('BLEU', 'JAUNE', 'VERT', 'BIODECHET', 'DECHETERIE', 'VETEMENT', 'ORDURE_MENAGERE') NOT NULL,
    `explication` LONGTEXT NOT NULL,
    `created_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updated_at` DATETIME(3) NOT NULL,

    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `Prestataire` (
    `id` VARCHAR(191) NOT NULL,
    `nom` VARCHAR(255) NOT NULL,
    `adresse` VARCHAR(255) NOT NULL,
    `email` VARCHAR(255) NOT NULL,
    `telephone` CHAR(10) NOT NULL,

    UNIQUE INDEX `Prestataire_nom_key`(`nom`),
    UNIQUE INDEX `Prestataire_email_key`(`email`),
    UNIQUE INDEX `Prestataire_telephone_key`(`telephone`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `_ComcomToPrestataire` (
    `A` VARCHAR(191) NOT NULL,
    `B` VARCHAR(191) NOT NULL,

    UNIQUE INDEX `_ComcomToPrestataire_AB_unique`(`A`, `B`),
    INDEX `_ComcomToPrestataire_B_index`(`B`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- AddForeignKey
ALTER TABLE `Score` ADD CONSTRAINT `Score_userId_fkey` FOREIGN KEY (`userId`) REFERENCES `User`(`id`) ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `User_Badge` ADD CONSTRAINT `User_Badge_userId_fkey` FOREIGN KEY (`userId`) REFERENCES `User`(`id`) ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `User_Badge` ADD CONSTRAINT `User_Badge_badgeId_fkey` FOREIGN KEY (`badgeId`) REFERENCES `Badge`(`id`) ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `User_Inventory` ADD CONSTRAINT `User_Inventory_userId_fkey` FOREIGN KEY (`userId`) REFERENCES `User`(`id`) ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `User_Inventory` ADD CONSTRAINT `User_Inventory_itemId_fkey` FOREIGN KEY (`itemId`) REFERENCES `Shop_Item`(`id`) ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `Regle_Tri` ADD CONSTRAINT `Regle_Tri_ComcomId_fkey` FOREIGN KEY (`ComcomId`) REFERENCES `Comcom`(`id`) ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `_ComcomToPrestataire` ADD CONSTRAINT `_ComcomToPrestataire_A_fkey` FOREIGN KEY (`A`) REFERENCES `Comcom`(`id`) ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `_ComcomToPrestataire` ADD CONSTRAINT `_ComcomToPrestataire_B_fkey` FOREIGN KEY (`B`) REFERENCES `Prestataire`(`id`) ON DELETE CASCADE ON UPDATE CASCADE;
