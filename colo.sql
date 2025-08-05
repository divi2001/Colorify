-- MySQL dump 10.13  Distrib 9.1.0, for Win64 (x86_64)
--
-- Host: localhost    Database: colorify3
-- ------------------------------------------------------
-- Server version	9.1.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `account_emailaddress`
--

DROP TABLE IF EXISTS `account_emailaddress`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `account_emailaddress` (
  `id` int NOT NULL AUTO_INCREMENT,
  `email` varchar(254) NOT NULL,
  `verified` tinyint(1) NOT NULL,
  `primary` tinyint(1) NOT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `account_emailaddress_user_id_email_987c8728_uniq` (`user_id`,`email`),
  KEY `account_emailaddress_email_03be32b2` (`email`),
  CONSTRAINT `account_emailaddress_user_id_2c513194_fk_core_customuser_id` FOREIGN KEY (`user_id`) REFERENCES `core_customuser` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `account_emailaddress`
--

LOCK TABLES `account_emailaddress` WRITE;
/*!40000 ALTER TABLE `account_emailaddress` DISABLE KEYS */;
INSERT INTO `account_emailaddress` VALUES (1,'tcchavan999@gmail.com',1,1,1);
/*!40000 ALTER TABLE `account_emailaddress` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `account_emailconfirmation`
--

DROP TABLE IF EXISTS `account_emailconfirmation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `account_emailconfirmation` (
  `id` int NOT NULL AUTO_INCREMENT,
  `created` datetime(6) NOT NULL,
  `sent` datetime(6) DEFAULT NULL,
  `key` varchar(64) NOT NULL,
  `email_address_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `key` (`key`),
  KEY `account_emailconfirm_email_address_id_5b7f8c58_fk_account_e` (`email_address_id`),
  CONSTRAINT `account_emailconfirm_email_address_id_5b7f8c58_fk_account_e` FOREIGN KEY (`email_address_id`) REFERENCES `account_emailaddress` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `account_emailconfirmation`
--

LOCK TABLES `account_emailconfirmation` WRITE;
/*!40000 ALTER TABLE `account_emailconfirmation` DISABLE KEYS */;
/*!40000 ALTER TABLE `account_emailconfirmation` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_permission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=109 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add log entry',1,'add_logentry'),(2,'Can change log entry',1,'change_logentry'),(3,'Can delete log entry',1,'delete_logentry'),(4,'Can view log entry',1,'view_logentry'),(5,'Can add permission',2,'add_permission'),(6,'Can change permission',2,'change_permission'),(7,'Can delete permission',2,'delete_permission'),(8,'Can view permission',2,'view_permission'),(9,'Can add group',3,'add_group'),(10,'Can change group',3,'change_group'),(11,'Can delete group',3,'delete_group'),(12,'Can view group',3,'view_group'),(13,'Can add content type',4,'add_contenttype'),(14,'Can change content type',4,'change_contenttype'),(15,'Can delete content type',4,'delete_contenttype'),(16,'Can view content type',4,'view_contenttype'),(17,'Can add session',5,'add_session'),(18,'Can change session',5,'change_session'),(19,'Can delete session',5,'delete_session'),(20,'Can view session',5,'view_session'),(21,'Can add site',6,'add_site'),(22,'Can change site',6,'change_site'),(23,'Can delete site',6,'delete_site'),(24,'Can view site',6,'view_site'),(25,'Can add email address',7,'add_emailaddress'),(26,'Can change email address',7,'change_emailaddress'),(27,'Can delete email address',7,'delete_emailaddress'),(28,'Can view email address',7,'view_emailaddress'),(29,'Can add email confirmation',8,'add_emailconfirmation'),(30,'Can change email confirmation',8,'change_emailconfirmation'),(31,'Can delete email confirmation',8,'delete_emailconfirmation'),(32,'Can view email confirmation',8,'view_emailconfirmation'),(33,'Can add social account',9,'add_socialaccount'),(34,'Can change social account',9,'change_socialaccount'),(35,'Can delete social account',9,'delete_socialaccount'),(36,'Can view social account',9,'view_socialaccount'),(37,'Can add social application',10,'add_socialapp'),(38,'Can change social application',10,'change_socialapp'),(39,'Can delete social application',10,'delete_socialapp'),(40,'Can view social application',10,'view_socialapp'),(41,'Can add social application token',11,'add_socialtoken'),(42,'Can change social application token',11,'change_socialtoken'),(43,'Can delete social application token',11,'delete_socialtoken'),(44,'Can view social application token',11,'view_socialtoken'),(45,'Can add user',12,'add_customuser'),(46,'Can change user',12,'change_customuser'),(47,'Can delete user',12,'delete_customuser'),(48,'Can view user',12,'view_customuser'),(49,'Can add contact',13,'add_contact'),(50,'Can change contact',13,'change_contact'),(51,'Can delete contact',13,'delete_contact'),(52,'Can view contact',13,'view_contact'),(53,'Can add project',14,'add_project'),(54,'Can change project',14,'change_project'),(55,'Can delete project',14,'delete_project'),(56,'Can view project',14,'view_project'),(57,'Can add inspiration pdf',15,'add_inspirationpdf'),(58,'Can change inspiration pdf',15,'change_inspirationpdf'),(59,'Can delete inspiration pdf',15,'delete_inspirationpdf'),(60,'Can view inspiration pdf',15,'view_inspirationpdf'),(61,'Can add subscription plan',16,'add_subscriptionplan'),(62,'Can change subscription plan',16,'change_subscriptionplan'),(63,'Can delete subscription plan',16,'delete_subscriptionplan'),(64,'Can view subscription plan',16,'view_subscriptionplan'),(65,'Can add palette',17,'add_palette'),(66,'Can change palette',17,'change_palette'),(67,'Can delete palette',17,'delete_palette'),(68,'Can view palette',17,'view_palette'),(69,'Can add color',18,'add_color'),(70,'Can change color',18,'change_color'),(71,'Can delete color',18,'delete_color'),(72,'Can view color',18,'view_color'),(73,'Can add user subscription',19,'add_usersubscription'),(74,'Can change user subscription',19,'change_usersubscription'),(75,'Can delete user subscription',19,'delete_usersubscription'),(76,'Can view user subscription',19,'view_usersubscription'),(77,'Can add palette favorite',20,'add_palettefavorite'),(78,'Can change palette favorite',20,'change_palettefavorite'),(79,'Can delete palette favorite',20,'delete_palettefavorite'),(80,'Can view palette favorite',20,'view_palettefavorite'),(81,'Can add pdf like',21,'add_pdflike'),(82,'Can change pdf like',21,'change_pdflike'),(83,'Can delete pdf like',21,'delete_pdflike'),(84,'Can view pdf like',21,'view_pdflike'),(85,'Can add payment transaction',22,'add_paymenttransaction'),(86,'Can change payment transaction',22,'change_paymenttransaction'),(87,'Can delete payment transaction',22,'delete_paymenttransaction'),(88,'Can view payment transaction',22,'view_paymenttransaction'),(89,'Can add base color',23,'add_basecolor'),(90,'Can change base color',23,'change_basecolor'),(91,'Can delete base color',23,'delete_basecolor'),(92,'Can view base color',23,'view_basecolor'),(93,'Can add device',24,'add_device'),(94,'Can change device',24,'change_device'),(95,'Can delete device',24,'delete_device'),(96,'Can view device',24,'view_device'),(97,'Can add Dashboard',25,'add_dashboardmodel'),(98,'Can change Dashboard',25,'change_dashboardmodel'),(99,'Can delete Dashboard',25,'delete_dashboardmodel'),(100,'Can view Dashboard',25,'view_dashboardmodel'),(101,'Can add referral code',26,'add_referralcode'),(102,'Can change referral code',26,'change_referralcode'),(103,'Can delete referral code',26,'delete_referralcode'),(104,'Can view referral code',26,'view_referralcode'),(105,'Can add mockup',27,'add_mockup'),(106,'Can change mockup',27,'change_mockup'),(107,'Can delete mockup',27,'delete_mockup'),(108,'Can view mockup',27,'view_mockup');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `core_contact`
--

DROP TABLE IF EXISTS `core_contact`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `core_contact` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `first_name` varchar(30) NOT NULL,
  `last_name` varchar(30) NOT NULL,
  `email` varchar(254) NOT NULL,
  `phone_number` varchar(15) DEFAULT NULL,
  `subject` varchar(20) NOT NULL,
  `message` longtext NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `core_contact_user_id_2570c512_fk_core_customuser_id` (`user_id`),
  CONSTRAINT `core_contact_user_id_2570c512_fk_core_customuser_id` FOREIGN KEY (`user_id`) REFERENCES `core_customuser` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `core_contact`
--

LOCK TABLES `core_contact` WRITE;
/*!40000 ALTER TABLE `core_contact` DISABLE KEYS */;
/*!40000 ALTER TABLE `core_contact` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `core_customuser`
--

DROP TABLE IF EXISTS `core_customuser`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `core_customuser` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  `gender` varchar(1) DEFAULT NULL,
  `designation` varchar(100) DEFAULT NULL,
  `phone_number` varchar(20) DEFAULT NULL,
  `address_line` varchar(255) DEFAULT NULL,
  `city` varchar(100) DEFAULT NULL,
  `state` varchar(100) DEFAULT NULL,
  `country` varchar(100) DEFAULT NULL,
  `profile_photo` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `core_customuser`
--

LOCK TABLES `core_customuser` WRITE;
/*!40000 ALTER TABLE `core_customuser` DISABLE KEYS */;
INSERT INTO `core_customuser` VALUES (1,'pbkdf2_sha256$870000$9tesFLuwg4Qm12YwosOFZo$GwVoRDasng01/USqNql8t7vKI1MuFKzShYhRAcpooTg=','2025-08-05 05:47:57.258621',1,'tanuj','','','tcchavan999@gmail.com',1,1,'2025-06-10 03:37:53.714288',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'');
/*!40000 ALTER TABLE `core_customuser` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `core_customuser_groups`
--

DROP TABLE IF EXISTS `core_customuser_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `core_customuser_groups` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `customuser_id` bigint NOT NULL,
  `group_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `core_customuser_groups_customuser_id_group_id_7990e9c6_uniq` (`customuser_id`,`group_id`),
  KEY `core_customuser_groups_group_id_301aeff4_fk_auth_group_id` (`group_id`),
  CONSTRAINT `core_customuser_grou_customuser_id_976bc4d7_fk_core_cust` FOREIGN KEY (`customuser_id`) REFERENCES `core_customuser` (`id`),
  CONSTRAINT `core_customuser_groups_group_id_301aeff4_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `core_customuser_groups`
--

LOCK TABLES `core_customuser_groups` WRITE;
/*!40000 ALTER TABLE `core_customuser_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `core_customuser_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `core_customuser_user_permissions`
--

DROP TABLE IF EXISTS `core_customuser_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `core_customuser_user_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `customuser_id` bigint NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `core_customuser_user_per_customuser_id_permission_49ea742a_uniq` (`customuser_id`,`permission_id`),
  KEY `core_customuser_user_permission_id_80ceaab9_fk_auth_perm` (`permission_id`),
  CONSTRAINT `core_customuser_user_customuser_id_ebd2ce6c_fk_core_cust` FOREIGN KEY (`customuser_id`) REFERENCES `core_customuser` (`id`),
  CONSTRAINT `core_customuser_user_permission_id_80ceaab9_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `core_customuser_user_permissions`
--

LOCK TABLES `core_customuser_user_permissions` WRITE;
/*!40000 ALTER TABLE `core_customuser_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `core_customuser_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `core_project`
--

DROP TABLE IF EXISTS `core_project`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `core_project` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `slug` varchar(50) NOT NULL,
  `status` varchar(10) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `modified_at` datetime(6) NOT NULL,
  `exported_at` datetime(6) DEFAULT NULL,
  `original_file` varchar(100) DEFAULT NULL,
  `exported_image` varchar(100) DEFAULT NULL,
  `original_filename` varchar(255) DEFAULT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `slug` (`slug`),
  KEY `core_project_user_id_8670f2b9_fk_core_customuser_id` (`user_id`),
  CONSTRAINT `core_project_user_id_8670f2b9_fk_core_customuser_id` FOREIGN KEY (`user_id`) REFERENCES `core_customuser` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `core_project`
--

LOCK TABLES `core_project` WRITE;
/*!40000 ALTER TABLE `core_project` DISABLE KEYS */;
INSERT INTO `core_project` VALUES (1,'Untitled Project','untitled-project','drafts','2025-08-04 05:03:58.434914','2025-08-04 05:03:58.434914',NULL,'','',NULL,1);
/*!40000 ALTER TABLE `core_project` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_admin_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_core_customuser_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_core_customuser_id` FOREIGN KEY (`user_id`) REFERENCES `core_customuser` (`id`),
  CONSTRAINT `django_admin_log_chk_1` CHECK ((`action_flag` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=41 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
INSERT INTO `django_admin_log` VALUES (1,'2025-06-10 04:24:13.242727','1','TRENDING Palette 1',3,'',17,1),(2,'2025-08-04 05:54:17.855276','1','Shirt',1,'[{\"added\": {}}]',27,1),(3,'2025-08-04 05:54:49.267681','1','Legacy Default Plan (Monthly)',2,'[{\"changed\": {\"fields\": [\"File upload limit\", \"Storage limit mb\"]}}]',16,1),(4,'2025-08-04 05:56:25.856977','2','Girl Hoody mask',1,'[{\"added\": {}}]',27,1),(5,'2025-08-04 05:56:39.400479','3','Dress Mask',1,'[{\"added\": {}}]',27,1),(6,'2025-08-04 05:56:57.775395','4','Kaftan Masl',1,'[{\"added\": {}}]',27,1),(7,'2025-08-04 05:57:14.802953','5','Leggings Mask',1,'[{\"added\": {}}]',27,1),(8,'2025-08-04 09:25:36.443963','26','TRENDING Palette 0',3,'',17,1),(9,'2025-08-04 09:25:58.546762','25','TRENDING Palette 0',3,'',17,1),(10,'2025-08-04 09:26:02.146113','24','TRENDING Palette 0',3,'',17,1),(11,'2025-08-04 09:26:05.313113','23','TRENDING Palette 0',3,'',17,1),(12,'2025-08-04 09:26:07.649052','22','TRENDING Palette 0',3,'',17,1),(13,'2025-08-04 09:26:12.663596','2','TRENDING Palette 2',3,'',17,1),(14,'2025-08-04 09:26:15.729666','21','TRENDING Palette 0',3,'',17,1),(15,'2025-08-04 09:26:18.928426','20','TRENDING Palette 0',3,'',17,1),(16,'2025-08-04 09:26:22.446470','19','TRENDING Palette 0',3,'',17,1),(17,'2025-08-04 09:26:25.313998','18','TRENDING Palette 0',3,'',17,1),(18,'2025-08-04 09:26:29.947686','17','TRENDING Palette 7',3,'',17,1),(19,'2025-08-04 09:26:33.396875','16','TRENDING Palette 3',3,'',17,1),(20,'2025-08-04 09:26:36.646869','15','TRENDING Palette 8',3,'',17,1),(21,'2025-08-04 09:26:39.845163','14','TRENDING Palette 0',3,'',17,1),(22,'2025-08-04 09:26:43.195019','13','TRENDING Palette 0',3,'',17,1),(23,'2025-08-04 09:26:46.583037','12','TRENDING Palette 2',3,'',17,1),(24,'2025-08-04 09:26:49.462859','11','TRENDING Palette 1',3,'',17,1),(25,'2025-08-04 09:26:59.881141','10','TRENDING Palette 0',3,'',17,1),(26,'2025-08-04 09:27:04.782574','9','TRENDING Palette 0',3,'',17,1),(27,'2025-08-04 09:27:07.951433','8','TRENDING Palette 6',3,'',17,1),(28,'2025-08-04 09:27:10.864454','7','TRENDING Palette 5',3,'',17,1),(29,'2025-08-04 09:27:13.730258','6','TRENDING Palette 4',3,'',17,1),(30,'2025-08-04 09:27:16.914919','5','TRENDING Palette 1',3,'',17,1),(31,'2025-08-04 09:27:20.495739','4','TRENDING Palette 1',3,'',17,1),(32,'2025-08-04 09:27:23.662905','3','TRENDING Palette 2',3,'',17,1),(33,'2025-08-04 09:43:14.671715','28','TRENDING Palette 0',3,'',17,1),(34,'2025-08-04 09:43:22.102319','27','TRENDING Palette 0',3,'',17,1),(35,'2025-08-05 05:53:28.435801','34','TRENDING Palette 1',3,'',17,1),(36,'2025-08-05 05:53:33.887783','33','TRENDING Palette 1',3,'',17,1),(37,'2025-08-05 05:53:40.470031','32','TRENDING Palette 2',3,'',17,1),(38,'2025-08-05 05:53:45.451306','31','TRENDING Palette 0',3,'',17,1),(39,'2025-08-05 05:53:49.371432','30','TRENDING Palette 2',3,'',17,1),(40,'2025-08-05 05:53:54.285602','29','TRENDING Palette 0',3,'',17,1);
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_cache_table`
--

DROP TABLE IF EXISTS `django_cache_table`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_cache_table` (
  `cache_key` varchar(255) NOT NULL,
  `value` text NOT NULL,
  `expires` datetime(6) NOT NULL,
  PRIMARY KEY (`cache_key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_cache_table`
--

LOCK TABLES `django_cache_table` WRITE;
/*!40000 ALTER TABLE `django_cache_table` DISABLE KEYS */;
INSERT INTO `django_cache_table` VALUES (':1:allauth:rl:login_failed:2574dc79f95317c18e887f71da24e46837bbdf16511bcf83cc2297447386cb0c','gAWVDQAAAAAAAABdlEdB2iRmqVPep2Eu','2025-08-05 05:51:13.000000'),(':1:allauth:rl:login:ip:127.0.0.1','gAWVFwAAAAAAAABdlChHQdokZsM4FzlHQdokZrsDpttlLg==','2025-08-05 05:48:56.000000'),(':1:django.contrib.sessions.cached_db20v59nfdhxhuqb7j4497y8c4x646a66c','gAWVOgEAAAAAAAB9lCiMHmFjY291bnRfYXV0aGVudGljYXRpb25fbWV0aG9kc5RdlH2UKIwGbWV0aG9klIwIcGFzc3dvcmSUjAJhdJRHQdoW9VLhIfOMBWVtYWlslIwVdGNjaGF2YW45OTlAZ21haWwuY29tlHVhjA1fYXV0aF91c2VyX2lklIwBMZSMEl9hdXRoX3VzZXJfYmFja2VuZJSMM2FsbGF1dGguYWNjb3VudC5hdXRoX2JhY2tlbmRzLkF1dGhlbnRpY2F0aW9uQmFja2VuZJSMD19hdXRoX3VzZXJfaGFzaJSMQDA1N2U4Mjk1ZDE3ODNkZjI5NGExNmUyNDgxOTU4NDU1N2EyYWVkYmMyZmNkNTcyZDczMjg4MWJkNWE3YmYzOWGUjA9fc2Vzc2lvbl9leHBpcnmUSoBRAQB1Lg==','2025-06-26 10:54:03.000000'),(':1:django.contrib.sessions.cached_dbhwuwrj3vc067yvj2lgwjf1vs5k7fmfd0','gAWVOgEAAAAAAAB9lCiMHmFjY291bnRfYXV0aGVudGljYXRpb25fbWV0aG9kc5RdlH2UKIwGbWV0aG9klIwIcGFzc3dvcmSUjAJhdJRHQdokZsNQO1WMBWVtYWlslIwVdGNjaGF2YW45OTlAZ21haWwuY29tlHVhjA1fYXV0aF91c2VyX2lklIwBMZSMEl9hdXRoX3VzZXJfYmFja2VuZJSMM2FsbGF1dGguYWNjb3VudC5hdXRoX2JhY2tlbmRzLkF1dGhlbnRpY2F0aW9uQmFja2VuZJSMD19hdXRoX3VzZXJfaGFzaJSMQDA1N2U4Mjk1ZDE3ODNkZjI5NGExNmUyNDgxOTU4NDU1N2EyYWVkYmMyZmNkNTcyZDczMjg4MWJkNWE3YmYzOWGUjA9fc2Vzc2lvbl9leHBpcnmUSoBRAQB1Lg==','2025-08-06 05:47:57.000000'),(':1:django.contrib.sessions.cached_dbkqdvbgavdxviuyuyulns7j87suweosh9','gAWVOgEAAAAAAAB9lCiMHmFjY291bnRfYXV0aGVudGljYXRpb25fbWV0aG9kc5RdlH2UKIwGbWV0aG9klIwIcGFzc3dvcmSUjAJhdJRHQdokEgZshk6MBWVtYWlslIwVdGNjaGF2YW45OTlAZ21haWwuY29tlHVhjA1fYXV0aF91c2VyX2lklIwBMZSMEl9hdXRoX3VzZXJfYmFja2VuZJSMM2FsbGF1dGguYWNjb3VudC5hdXRoX2JhY2tlbmRzLkF1dGhlbnRpY2F0aW9uQmFja2VuZJSMD19hdXRoX3VzZXJfaGFzaJSMQDA1N2U4Mjk1ZDE3ODNkZjI5NGExNmUyNDgxOTU4NDU1N2EyYWVkYmMyZmNkNTcyZDczMjg4MWJkNWE3YmYzOWGUjA9fc2Vzc2lvbl9leHBpcnmUSoBRAQB1Lg==','2025-08-05 05:41:45.000000'),(':1:django.contrib.sessions.cached_dbtfanlvkax1546o8fi9n3ylf5tu3mgf7u','gAWVrwAAAAAAAAB9lCiMDV9hdXRoX3VzZXJfaWSUjAExlIwSX2F1dGhfdXNlcl9iYWNrZW5klIwpZGphbmdvLmNvbnRyaWIuYXV0aC5iYWNrZW5kcy5Nb2RlbEJhY2tlbmSUjA9fYXV0aF91c2VyX2hhc2iUjEAwNTdlODI5NWQxNzgzZGYyOTRhMTZlMjQ4MTk1ODQ1NTdhMmFlZGJjMmZjZDU3MmQ3MzI4ODFiZDVhN2JmMzlhlHUu','2025-06-11 03:41:44.000000'),(':1:django.contrib.sessions.cached_dbxj5cbctw0nxdcpdn5g3y256ipty8nyp9','gAWVrwAAAAAAAAB9lCiMDV9hdXRoX3VzZXJfaWSUjAExlIwSX2F1dGhfdXNlcl9iYWNrZW5klIwpZGphbmdvLmNvbnRyaWIuYXV0aC5iYWNrZW5kcy5Nb2RlbEJhY2tlbmSUjA9fYXV0aF91c2VyX2hhc2iUjEAwNTdlODI5NWQxNzgzZGYyOTRhMTZlMjQ4MTk1ODQ1NTdhMmFlZGJjMmZjZDU3MmQ3MzI4ODFiZDVhN2JmMzlhlHUu','2025-06-12 11:03:33.000000'),(':1:last_activity_1','gAWVVwAAAAAAAACMCGRhdGV0aW1llIwIZGF0ZXRpbWWUk5RDCgfpCAUGFAkCB0+UaACMCHRpbWV6b25llJOUaACMCXRpbWVkZWx0YZSTlEsASwBLAIeUUpSFlFKUhpRSlC4=','9999-12-31 23:59:59.000000'),(':1:user_sessions_1','gAWVSwAAAAAAAABdlCiMIGtxZHZiZ2F2ZHh2aXV5dXl1bG5zN2o4N3N1d2Vvc2g5lIwgaHd1d3JqM3ZjMDY3eXZqMmxnd2pmMXZzNWs3Zm1mZDCUZS4=','9999-12-31 23:59:59.000000');
/*!40000 ALTER TABLE `django_cache_table` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_content_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=28 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (7,'account','emailaddress'),(8,'account','emailconfirmation'),(1,'admin','logentry'),(3,'auth','group'),(2,'auth','permission'),(4,'contenttypes','contenttype'),(13,'core','contact'),(12,'core','customuser'),(14,'core','project'),(25,'mainadmin','dashboardmodel'),(5,'sessions','session'),(6,'sites','site'),(9,'socialaccount','socialaccount'),(10,'socialaccount','socialapp'),(11,'socialaccount','socialtoken'),(23,'subscription_module','basecolor'),(18,'subscription_module','color'),(24,'subscription_module','device'),(15,'subscription_module','inspirationpdf'),(17,'subscription_module','palette'),(20,'subscription_module','palettefavorite'),(22,'subscription_module','paymenttransaction'),(21,'subscription_module','pdflike'),(26,'subscription_module','referralcode'),(16,'subscription_module','subscriptionplan'),(19,'subscription_module','usersubscription'),(27,'tif_to_picker','mockup');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_migrations` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=50 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (1,'contenttypes','0001_initial','2025-06-10 03:37:15.342855'),(2,'contenttypes','0002_remove_content_type_name','2025-06-10 03:37:15.367359'),(3,'auth','0001_initial','2025-06-10 03:37:15.453447'),(4,'auth','0002_alter_permission_name_max_length','2025-06-10 03:37:15.472615'),(5,'auth','0003_alter_user_email_max_length','2025-06-10 03:37:15.476629'),(6,'auth','0004_alter_user_username_opts','2025-06-10 03:37:15.480670'),(7,'auth','0005_alter_user_last_login_null','2025-06-10 03:37:15.480670'),(8,'auth','0006_require_contenttypes_0002','2025-06-10 03:37:15.480670'),(9,'auth','0007_alter_validators_add_error_messages','2025-06-10 03:37:15.487017'),(10,'auth','0008_alter_user_username_max_length','2025-06-10 03:37:15.488521'),(11,'auth','0009_alter_user_last_name_max_length','2025-06-10 03:37:15.488521'),(12,'auth','0010_alter_group_name_max_length','2025-06-10 03:37:15.497604'),(13,'auth','0011_update_proxy_permissions','2025-06-10 03:37:15.501124'),(14,'auth','0012_alter_user_first_name_max_length','2025-06-10 03:37:15.501124'),(15,'core','0001_initial','2025-06-10 03:37:15.682875'),(16,'account','0001_initial','2025-06-10 03:37:15.756977'),(17,'account','0002_email_max_length','2025-06-10 03:37:15.778599'),(18,'account','0003_alter_emailaddress_create_unique_verified_email','2025-06-10 03:37:15.793813'),(19,'account','0004_alter_emailaddress_drop_unique_email','2025-06-10 03:37:15.809423'),(20,'account','0005_emailaddress_idx_upper_email','2025-06-10 03:37:15.829319'),(21,'account','0006_emailaddress_lower','2025-06-10 03:37:15.836850'),(22,'account','0007_emailaddress_idx_email','2025-06-10 03:37:15.856191'),(23,'account','0008_emailaddress_unique_primary_email_fixup','2025-06-10 03:37:15.860706'),(24,'account','0009_emailaddress_unique_primary_email','2025-06-10 03:37:15.866689'),(25,'admin','0001_initial','2025-06-10 03:37:15.932953'),(26,'admin','0002_logentry_remove_auto_add','2025-06-10 03:37:15.938513'),(27,'admin','0003_logentry_add_action_flag_choices','2025-06-10 03:37:15.944542'),(28,'mainadmin','0001_initial','2025-06-10 03:37:15.951455'),(29,'mainadmin','0002_rename_dashboardmodel_analyticsdashboardmodel_and_more','2025-06-10 03:37:15.955505'),(30,'mainadmin','0003_dashboardmodel_delete_analyticsdashboardmodel','2025-06-10 03:37:15.971822'),(31,'sessions','0001_initial','2025-06-10 03:37:15.984571'),(32,'sites','0001_initial','2025-06-10 03:37:15.990552'),(33,'sites','0002_alter_domain_unique','2025-06-10 03:37:16.000258'),(34,'socialaccount','0001_initial','2025-06-10 03:37:16.156110'),(35,'socialaccount','0002_token_max_lengths','2025-06-10 03:37:16.180764'),(36,'socialaccount','0003_extra_data_default_dict','2025-06-10 03:37:16.189852'),(37,'socialaccount','0004_app_provider_id_settings','2025-06-10 03:37:16.241744'),(38,'socialaccount','0005_socialtoken_nullable_app','2025-06-10 03:37:16.302219'),(39,'socialaccount','0006_alter_socialaccount_extra_data','2025-06-10 03:37:16.331962'),(40,'subscription_module','0001_initial','2025-06-10 03:37:16.580251'),(41,'subscription_module','0002_paymenttransaction','2025-06-10 03:37:16.647215'),(42,'subscription_module','0003_basecolor','2025-06-10 03:37:16.659935'),(43,'subscription_module','0004_remove_subscriptionplan_price_and_more','2025-06-10 03:37:17.120859'),(44,'subscription_module','0005_remove_usersubscription_max_devices_and_more','2025-06-10 03:37:17.242513'),(45,'subscription_module','0006_remove_subscriptionplan_max_devices_and_more','2025-06-10 03:37:17.356401'),(46,'tif_to_picker','0001_initial','2025-06-10 03:37:17.390558'),(47,'tif_to_picker','0002_delete_mockup','2025-06-10 03:37:17.397996'),(48,'subscription_module','0007_referralcode_remove_usersubscription_max_devices_and_more','2025-08-04 05:03:10.421688'),(49,'tif_to_picker','0003_initial','2025-08-04 05:09:03.117849');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
INSERT INTO `django_session` VALUES ('20v59nfdhxhuqb7j4497y8c4x646a66c','.eJxVkM1uxCAMhN_F5wgFAgFy6vY1qipygBTUBFaB9Eerffcu21xys2bGn0e-ARqT9lhG3It3sQSDJaQ4rq74ZDMMbzf4n2GAK-b8nTYLDWCBgUrRKq4U74igsteyAbdiWB7JYozHL4xa65ePqhGTVri_N_A8NO7ZbWOoTAonbULz6WI1cFmqTI6C5Jk57Ewup7qvx9YJ5TH7B6cV0immhaVSdXZmmiPtHeOKaqG4EBIZOjsZNhsrJLOyY0rRyQqU09xprNDscq5fcT_XsP3CoHretvc_HsppNw:1uUNlT:7UNOe8HbRuw8lSeBarEcWAMLzvkJ9k8KG86sgBnNvx8','2025-06-26 10:54:03.529424'),('hwuwrj3vc067yvj2lgwjf1vs5k7fmfd0','.eJxVkEtuhDAQRO_Sa4TwD9usMrlGFKHGNrEVsEfY5KPR3D3jCRt2rarq16W-ARqT9lhG3It3sQSDJaQ4rq74ZDMMbzf4n2GAK-b8nTYLDWCBgUjBmaRKypYK1lPCGnArhuURLcZ4_MKotX75qFpr0gr39wael8Y9u20MFUrgpE1oPl2sBi5LldujYfvMHHZuL6e-r8fWCeUx-wenE9IpqoUlUjE7U82R9I5yRbRQXAiJFJ2dDJ2NFZJayahSZLIC5TQzjRWaXc71Le7nGrZfGFTPu-7-B1xhaV0:1ujAWj:RO-ztaHooP4k-4biOFkaQG9uNlM7uYr-aj0Kl0BkKKw','2025-08-06 05:47:57.260621'),('kqdvbgavdxviuyuyulns7j87suweosh9','.eJxVkEtuhDAQRO_Sa4Sw8ZdVJteIItTYJrYC9gibfDSau2c8YcOuVVX9utQ3QGPSHsuIe_EulmCwhBTH1RWfbIbh7Qb_MwxwxZy_02ahASwwEMkZVYJ0vBWaCy37BtyKYXlEizEevzBqrV8-qtaatML9vYHnpXHPbhtDhRI4aROaTxergctS5fZo2D4zh53by6nv67F1QnnM_sHpuHSKam6JVL2dqWZIhKNMEc0V41wiRWcnQ2djuaRW9lQpMlmOcpp7jRWaXc71Le7nGrZfGJRgXXf_A2aPaWg:1uinxB:2usGptl5qBVuA9aO_MS5RjK1XFezNmcofxYKqwvbR2A','2025-08-05 05:41:45.710649'),('tfanlvkax1546o8fi9n3ylf5tu3mgf7u','.eJxVjDEOAiEQRe9CbYgMjIClvWcgAwOyaiBZdivj3XWTLbT9773_EoHWpYZ15DlMLM5CicPvFik9ctsA36nduky9LfMU5abInQ557Zyfl939O6g06rc-os0OPLKyTnMBb0idMhinPDqDaAkoc0xQEqMFthqcU5GRbCzak3h_AMEKN4U:1uOprs:_6Ag0jqaQp6oZLfmokdMkBifl2PHzVEf2kVIKoMr4pI','2025-06-11 03:41:44.007573'),('xj5cbctw0nxdcpdn5g3y256ipty8nyp9','.eJxVjDEOAiEQRe9CbYgMjIClvWcgAwOyaiBZdivj3XWTLbT9773_EoHWpYZ15DlMLM5CicPvFik9ctsA36nduky9LfMU5abInQ557Zyfl939O6g06rc-os0OPLKyTnMBb0idMhinPDqDaAkoc0xQEqMFthqcU5GRbCzak3h_AMEKN4U:1uPJEz:wma8RmosH2rTyPFaHij9f5cbTxey5QR8_9OaCJo4xRk','2025-06-12 11:03:33.694494');
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_site`
--

DROP TABLE IF EXISTS `django_site`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_site` (
  `id` int NOT NULL AUTO_INCREMENT,
  `domain` varchar(100) NOT NULL,
  `name` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_site_domain_a2e37b91_uniq` (`domain`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_site`
--

LOCK TABLES `django_site` WRITE;
/*!40000 ALTER TABLE `django_site` DISABLE KEYS */;
INSERT INTO `django_site` VALUES (1,'example.com','example.com');
/*!40000 ALTER TABLE `django_site` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `mainadmin_dashboardmodel`
--

DROP TABLE IF EXISTS `mainadmin_dashboardmodel`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `mainadmin_dashboardmodel` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `title` varchar(100) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `mainadmin_dashboardmodel`
--

LOCK TABLES `mainadmin_dashboardmodel` WRITE;
/*!40000 ALTER TABLE `mainadmin_dashboardmodel` DISABLE KEYS */;
/*!40000 ALTER TABLE `mainadmin_dashboardmodel` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `socialaccount_socialaccount`
--

DROP TABLE IF EXISTS `socialaccount_socialaccount`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `socialaccount_socialaccount` (
  `id` int NOT NULL AUTO_INCREMENT,
  `provider` varchar(200) NOT NULL,
  `uid` varchar(191) NOT NULL,
  `last_login` datetime(6) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  `extra_data` json NOT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `socialaccount_socialaccount_provider_uid_fc810c6e_uniq` (`provider`,`uid`),
  KEY `socialaccount_social_user_id_8146e70c_fk_core_cust` (`user_id`),
  CONSTRAINT `socialaccount_social_user_id_8146e70c_fk_core_cust` FOREIGN KEY (`user_id`) REFERENCES `core_customuser` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `socialaccount_socialaccount`
--

LOCK TABLES `socialaccount_socialaccount` WRITE;
/*!40000 ALTER TABLE `socialaccount_socialaccount` DISABLE KEYS */;
/*!40000 ALTER TABLE `socialaccount_socialaccount` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `socialaccount_socialapp`
--

DROP TABLE IF EXISTS `socialaccount_socialapp`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `socialaccount_socialapp` (
  `id` int NOT NULL AUTO_INCREMENT,
  `provider` varchar(30) NOT NULL,
  `name` varchar(40) NOT NULL,
  `client_id` varchar(191) NOT NULL,
  `secret` varchar(191) NOT NULL,
  `key` varchar(191) NOT NULL,
  `provider_id` varchar(200) NOT NULL,
  `settings` json NOT NULL DEFAULT (_utf8mb3'{}'),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `socialaccount_socialapp`
--

LOCK TABLES `socialaccount_socialapp` WRITE;
/*!40000 ALTER TABLE `socialaccount_socialapp` DISABLE KEYS */;
/*!40000 ALTER TABLE `socialaccount_socialapp` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `socialaccount_socialapp_sites`
--

DROP TABLE IF EXISTS `socialaccount_socialapp_sites`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `socialaccount_socialapp_sites` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `socialapp_id` int NOT NULL,
  `site_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `socialaccount_socialapp_sites_socialapp_id_site_id_71a9a768_uniq` (`socialapp_id`,`site_id`),
  KEY `socialaccount_socialapp_sites_site_id_2579dee5_fk_django_site_id` (`site_id`),
  CONSTRAINT `socialaccount_social_socialapp_id_97fb6e7d_fk_socialacc` FOREIGN KEY (`socialapp_id`) REFERENCES `socialaccount_socialapp` (`id`),
  CONSTRAINT `socialaccount_socialapp_sites_site_id_2579dee5_fk_django_site_id` FOREIGN KEY (`site_id`) REFERENCES `django_site` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `socialaccount_socialapp_sites`
--

LOCK TABLES `socialaccount_socialapp_sites` WRITE;
/*!40000 ALTER TABLE `socialaccount_socialapp_sites` DISABLE KEYS */;
/*!40000 ALTER TABLE `socialaccount_socialapp_sites` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `socialaccount_socialtoken`
--

DROP TABLE IF EXISTS `socialaccount_socialtoken`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `socialaccount_socialtoken` (
  `id` int NOT NULL AUTO_INCREMENT,
  `token` longtext NOT NULL,
  `token_secret` longtext NOT NULL,
  `expires_at` datetime(6) DEFAULT NULL,
  `account_id` int NOT NULL,
  `app_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `socialaccount_socialtoken_app_id_account_id_fca4e0ac_uniq` (`app_id`,`account_id`),
  KEY `socialaccount_social_account_id_951f210e_fk_socialacc` (`account_id`),
  CONSTRAINT `socialaccount_social_account_id_951f210e_fk_socialacc` FOREIGN KEY (`account_id`) REFERENCES `socialaccount_socialaccount` (`id`),
  CONSTRAINT `socialaccount_social_app_id_636a42d7_fk_socialacc` FOREIGN KEY (`app_id`) REFERENCES `socialaccount_socialapp` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `socialaccount_socialtoken`
--

LOCK TABLES `socialaccount_socialtoken` WRITE;
/*!40000 ALTER TABLE `socialaccount_socialtoken` DISABLE KEYS */;
/*!40000 ALTER TABLE `socialaccount_socialtoken` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `subscription_module_basecolor`
--

DROP TABLE IF EXISTS `subscription_module_basecolor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `subscription_module_basecolor` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `red` smallint unsigned NOT NULL,
  `green` smallint unsigned NOT NULL,
  `blue` smallint unsigned NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  CONSTRAINT `subscription_module_basecolor_chk_1` CHECK ((`red` >= 0)),
  CONSTRAINT `subscription_module_basecolor_chk_2` CHECK ((`green` >= 0)),
  CONSTRAINT `subscription_module_basecolor_chk_3` CHECK ((`blue` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `subscription_module_basecolor`
--

LOCK TABLES `subscription_module_basecolor` WRITE;
/*!40000 ALTER TABLE `subscription_module_basecolor` DISABLE KEYS */;
/*!40000 ALTER TABLE `subscription_module_basecolor` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `subscription_module_color`
--

DROP TABLE IF EXISTS `subscription_module_color`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `subscription_module_color` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `red` int NOT NULL,
  `green` int NOT NULL,
  `blue` int NOT NULL,
  `palette_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `subscription_module__palette_id_8e7e45ec_fk_subscript` (`palette_id`),
  CONSTRAINT `subscription_module__palette_id_8e7e45ec_fk_subscript` FOREIGN KEY (`palette_id`) REFERENCES `subscription_module_palette` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1283 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `subscription_module_color`
--

LOCK TABLES `subscription_module_color` WRITE;
/*!40000 ALTER TABLE `subscription_module_color` DISABLE KEYS */;
INSERT INTO `subscription_module_color` VALUES (1190,'',135,138,120,35),(1191,'',88,98,70,35),(1192,'',139,202,119,35),(1193,'',191,198,141,35),(1194,'',65,73,48,35),(1195,'',179,205,167,35),(1196,'',49,60,87,35),(1197,'',172,178,197,35),(1198,'',212,227,203,35),(1199,'',149,164,46,35),(1200,'',123,171,105,35),(1201,'',39,43,28,35),(1202,'',196,240,133,35),(1203,'',147,229,75,35),(1204,'',160,176,93,35),(1205,'',145,147,157,35),(1206,'',109,103,98,35),(1207,'',128,140,74,35),(1208,'',221,183,139,35),(1209,'',236,255,180,35),(1210,'',171,134,121,35),(1211,'',211,228,114,35),(1212,'',90,101,130,35),(1213,'',150,188,56,35),(1214,'',178,224,71,35),(1215,'',104,73,101,35),(1216,'',97,125,36,35),(1217,'',67,37,72,35),(1218,'',162,117,153,35),(1219,'',90,142,78,35),(1220,'',210,185,182,35),(1221,'',120,138,123,36),(1222,'',70,98,80,36),(1223,'',119,202,182,36),(1224,'',141,198,148,36),(1225,'',48,73,56,36),(1226,'',167,205,193,36),(1227,'',76,49,87,36),(1228,'',191,172,197,36),(1229,'',203,227,218,36),(1230,'',46,164,61,36),(1231,'',105,171,153,36),(1232,'',28,43,32,36),(1233,'',133,240,177,36),(1234,'',75,229,157,36),(1235,'',93,176,109,36),(1236,'',155,145,157,36),(1237,'',104,109,98,36),(1238,'',74,140,86,36),(1239,'',177,221,139,36),(1240,'',180,255,199,36),(1241,'',158,171,121,36),(1242,'',114,228,131,36),(1243,'',119,90,130,36),(1244,'',56,188,94,36),(1245,'',71,224,117,36),(1246,'',104,76,73,36),(1247,'',36,125,64,36),(1248,'',72,37,42,36),(1249,'',162,126,117,36),(1250,'',78,142,130,36),(1251,'',207,210,182,36),(1252,'',123,120,138,37),(1253,'',80,70,98,37),(1254,'',182,119,202,37),(1255,'',148,141,198,37),(1256,'',56,48,73,37),(1257,'',193,167,205,37),(1258,'',87,76,49,37),(1259,'',197,191,172,37),(1260,'',218,203,227,37),(1261,'',61,46,164,37),(1262,'',153,105,171,37),(1263,'',32,28,43,37),(1264,'',177,133,240,37),(1265,'',157,75,229,37),(1266,'',109,93,176,37),(1267,'',157,155,145,37),(1268,'',98,104,109,37),(1269,'',86,74,140,37),(1270,'',139,177,221,37),(1271,'',199,180,255,37),(1272,'',121,158,171,37),(1273,'',131,114,228,37),(1274,'',130,119,90,37),(1275,'',94,56,188,37),(1276,'',117,71,224,37),(1277,'',73,104,76,37),(1278,'',64,36,125,37),(1279,'',42,72,37,37),(1280,'',117,162,126,37),(1281,'',130,78,142,37),(1282,'',182,207,210,37);
/*!40000 ALTER TABLE `subscription_module_color` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `subscription_module_device`
--

DROP TABLE IF EXISTS `subscription_module_device`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `subscription_module_device` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `device_id` varchar(255) NOT NULL,
  `device_name` varchar(100) NOT NULL,
  `last_login` datetime(6) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `device_id` (`device_id`),
  KEY `subscription_module__user_id_a7f4b4c6_fk_core_cust` (`user_id`),
  CONSTRAINT `subscription_module__user_id_a7f4b4c6_fk_core_cust` FOREIGN KEY (`user_id`) REFERENCES `core_customuser` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `subscription_module_device`
--

LOCK TABLES `subscription_module_device` WRITE;
/*!40000 ALTER TABLE `subscription_module_device` DISABLE KEYS */;
INSERT INTO `subscription_module_device` VALUES (1,'session_0ks24eixuzktzbic3hk60kbvqs73grhs','Browser Session (2025-08-04)','2025-08-04 05:14:28.765607',0,1),(2,'session_kqdvbgavdxviuyuyulns7j87suweosh9','Browser Session (2025-08-04)','2025-08-04 05:41:45.723659',1,1),(3,'session_hwuwrj3vc067yvj2lgwjf1vs5k7fmfd0','Browser Session (2025-08-05)','2025-08-05 05:47:57.273995',1,1);
/*!40000 ALTER TABLE `subscription_module_device` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `subscription_module_inspirationpdf`
--

DROP TABLE IF EXISTS `subscription_module_inspirationpdf`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `subscription_module_inspirationpdf` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `title` varchar(200) NOT NULL,
  `pdf_file` varchar(100) NOT NULL,
  `preview_image` varchar(100) NOT NULL,
  `likes_count` int NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `subscription_module_inspirationpdf`
--

LOCK TABLES `subscription_module_inspirationpdf` WRITE;
/*!40000 ALTER TABLE `subscription_module_inspirationpdf` DISABLE KEYS */;
/*!40000 ALTER TABLE `subscription_module_inspirationpdf` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `subscription_module_palette`
--

DROP TABLE IF EXISTS `subscription_module_palette`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `subscription_module_palette` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `num_colors` int NOT NULL,
  `base_color` varchar(50) NOT NULL,
  `base_color_r` int NOT NULL,
  `base_color_g` int NOT NULL,
  `base_color_b` int NOT NULL,
  `type` varchar(2) NOT NULL,
  `favorites_count` int unsigned NOT NULL,
  `creator_id` bigint NOT NULL,
  `source_image_colors` json DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `subscription_module__creator_id_ab6e04de_fk_core_cust` (`creator_id`),
  CONSTRAINT `subscription_module__creator_id_ab6e04de_fk_core_cust` FOREIGN KEY (`creator_id`) REFERENCES `core_customuser` (`id`),
  CONSTRAINT `subscription_module_palette_chk_1` CHECK ((`favorites_count` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=38 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `subscription_module_palette`
--

LOCK TABLES `subscription_module_palette` WRITE;
/*!40000 ALTER TABLE `subscription_module_palette` DISABLE KEYS */;
INSERT INTO `subscription_module_palette` VALUES (35,'TRENDING Palette 0','2025-08-05 05:58:08.543108','2025-08-05 05:58:08.543108',31,'Generated',135,138,120,'TR',1,1,'[[138, 123, 120], [98, 80, 70], [202, 182, 119], [73, 56, 48], [198, 148, 141], [205, 193, 167], [47, 86, 75], [156, 63, 48], [171, 153, 104], [44, 33, 29], [238, 151, 74], [226, 220, 202], [177, 193, 202], [165, 85, 85], [98, 104, 111], [207, 121, 82], [169, 169, 169], [246, 194, 149], [140, 115, 72], [227, 145, 112], [191, 86, 44], [128, 153, 150], [226, 134, 168]]'),(36,'TRENDING Palette 1','2025-08-05 06:02:09.338942','2025-08-05 06:02:09.338942',31,'Generated',120,138,123,'TR',1,1,'[[138, 123, 120], [98, 80, 70], [202, 182, 119], [73, 56, 48], [198, 148, 141], [205, 193, 167], [47, 86, 75], [156, 63, 48], [171, 153, 104], [44, 33, 29], [238, 151, 74], [226, 220, 202], [177, 193, 202], [165, 85, 85], [98, 104, 111], [207, 121, 82], [169, 169, 169], [246, 194, 149], [140, 115, 72], [227, 145, 112], [191, 86, 44], [128, 153, 150], [226, 134, 168]]'),(37,'TRENDING Palette 3','2025-08-05 06:19:23.134493','2025-08-05 06:19:23.134493',31,'Generated',123,120,138,'TR',1,1,'[[138, 123, 120], [98, 80, 70], [202, 182, 119], [73, 56, 48], [198, 148, 141], [205, 193, 167], [47, 86, 75], [156, 63, 48], [171, 153, 104], [44, 33, 29], [238, 151, 74], [226, 220, 202], [177, 193, 202], [165, 85, 85], [98, 104, 111], [207, 121, 82], [169, 169, 169], [246, 194, 149], [140, 115, 72], [227, 145, 112], [191, 86, 44], [128, 153, 150], [226, 134, 168]]');
/*!40000 ALTER TABLE `subscription_module_palette` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `subscription_module_palettefavorite`
--

DROP TABLE IF EXISTS `subscription_module_palettefavorite`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `subscription_module_palettefavorite` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL,
  `palette_id` bigint NOT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `subscription_module_pale_user_id_palette_id_c1ac42f7_uniq` (`user_id`,`palette_id`),
  KEY `subscription_module__palette_id_751d4245_fk_subscript` (`palette_id`),
  CONSTRAINT `subscription_module__palette_id_751d4245_fk_subscript` FOREIGN KEY (`palette_id`) REFERENCES `subscription_module_palette` (`id`),
  CONSTRAINT `subscription_module__user_id_6281dfcc_fk_core_cust` FOREIGN KEY (`user_id`) REFERENCES `core_customuser` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=38 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `subscription_module_palettefavorite`
--

LOCK TABLES `subscription_module_palettefavorite` WRITE;
/*!40000 ALTER TABLE `subscription_module_palettefavorite` DISABLE KEYS */;
INSERT INTO `subscription_module_palettefavorite` VALUES (35,'2025-08-05 05:58:08.571218',35,1),(36,'2025-08-05 06:02:09.364983',36,1),(37,'2025-08-05 06:19:23.163529',37,1);
/*!40000 ALTER TABLE `subscription_module_palettefavorite` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `subscription_module_paymenttransaction`
--

DROP TABLE IF EXISTS `subscription_module_paymenttransaction`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `subscription_module_paymenttransaction` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `transaction_id` char(32) NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  `status` varchar(20) NOT NULL,
  `payment_gateway_reference` varchar(255) DEFAULT NULL,
  `payment_method` varchar(50) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `subscription_plan_id` bigint NOT NULL,
  `user_id` bigint NOT NULL,
  `metadata` json NOT NULL DEFAULT (_utf8mb3'{}'),
  `transaction_type` varchar(20) NOT NULL,
  `referral_code_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `transaction_id` (`transaction_id`),
  KEY `subscription_module__user_id_b1b0c0cc_fk_core_cust` (`user_id`),
  KEY `subscription_module__subscription_plan_id_7149568b_fk_subscript` (`subscription_plan_id`),
  KEY `subscription_module__referral_code_id_4f16092e_fk_subscript` (`referral_code_id`),
  CONSTRAINT `subscription_module__referral_code_id_4f16092e_fk_subscript` FOREIGN KEY (`referral_code_id`) REFERENCES `subscription_module_referralcode` (`id`),
  CONSTRAINT `subscription_module__subscription_plan_id_7149568b_fk_subscript` FOREIGN KEY (`subscription_plan_id`) REFERENCES `subscription_module_subscriptionplan` (`id`),
  CONSTRAINT `subscription_module__user_id_b1b0c0cc_fk_core_cust` FOREIGN KEY (`user_id`) REFERENCES `core_customuser` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `subscription_module_paymenttransaction`
--

LOCK TABLES `subscription_module_paymenttransaction` WRITE;
/*!40000 ALTER TABLE `subscription_module_paymenttransaction` DISABLE KEYS */;
/*!40000 ALTER TABLE `subscription_module_paymenttransaction` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `subscription_module_pdflike`
--

DROP TABLE IF EXISTS `subscription_module_pdflike`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `subscription_module_pdflike` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL,
  `pdf_id` bigint NOT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `subscription_module_pdflike_user_id_pdf_id_a54ffb0d_uniq` (`user_id`,`pdf_id`),
  KEY `subscription_module__pdf_id_b73b3c62_fk_subscript` (`pdf_id`),
  CONSTRAINT `subscription_module__pdf_id_b73b3c62_fk_subscript` FOREIGN KEY (`pdf_id`) REFERENCES `subscription_module_inspirationpdf` (`id`),
  CONSTRAINT `subscription_module__user_id_a16da570_fk_core_cust` FOREIGN KEY (`user_id`) REFERENCES `core_customuser` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `subscription_module_pdflike`
--

LOCK TABLES `subscription_module_pdflike` WRITE;
/*!40000 ALTER TABLE `subscription_module_pdflike` DISABLE KEYS */;
/*!40000 ALTER TABLE `subscription_module_pdflike` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `subscription_module_referralcode`
--

DROP TABLE IF EXISTS `subscription_module_referralcode`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `subscription_module_referralcode` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `code` varchar(20) NOT NULL,
  `discount_percentage` int unsigned NOT NULL,
  `expiration_date` datetime(6) DEFAULT NULL,
  `max_uses` int unsigned NOT NULL,
  `current_uses` int unsigned NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `created_by_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`),
  KEY `subscription_module__created_by_id_0f5725d8_fk_core_cust` (`created_by_id`),
  CONSTRAINT `subscription_module__created_by_id_0f5725d8_fk_core_cust` FOREIGN KEY (`created_by_id`) REFERENCES `core_customuser` (`id`),
  CONSTRAINT `subscription_module_referralcode_chk_1` CHECK ((`discount_percentage` >= 0)),
  CONSTRAINT `subscription_module_referralcode_chk_2` CHECK ((`max_uses` >= 0)),
  CONSTRAINT `subscription_module_referralcode_chk_3` CHECK ((`current_uses` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `subscription_module_referralcode`
--

LOCK TABLES `subscription_module_referralcode` WRITE;
/*!40000 ALTER TABLE `subscription_module_referralcode` DISABLE KEYS */;
/*!40000 ALTER TABLE `subscription_module_referralcode` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `subscription_module_referralcode_applicable_plans`
--

DROP TABLE IF EXISTS `subscription_module_referralcode_applicable_plans`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `subscription_module_referralcode_applicable_plans` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `referralcode_id` bigint NOT NULL,
  `subscriptionplan_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `subscription_module_refe_referralcode_id_subscrip_fdb199e5_uniq` (`referralcode_id`,`subscriptionplan_id`),
  KEY `subscription_module__subscriptionplan_id_0ff0b4df_fk_subscript` (`subscriptionplan_id`),
  CONSTRAINT `subscription_module__referralcode_id_0ef76803_fk_subscript` FOREIGN KEY (`referralcode_id`) REFERENCES `subscription_module_referralcode` (`id`),
  CONSTRAINT `subscription_module__subscriptionplan_id_0ff0b4df_fk_subscript` FOREIGN KEY (`subscriptionplan_id`) REFERENCES `subscription_module_subscriptionplan` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `subscription_module_referralcode_applicable_plans`
--

LOCK TABLES `subscription_module_referralcode_applicable_plans` WRITE;
/*!40000 ALTER TABLE `subscription_module_referralcode_applicable_plans` DISABLE KEYS */;
/*!40000 ALTER TABLE `subscription_module_referralcode_applicable_plans` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `subscription_module_subscriptionplan`
--

DROP TABLE IF EXISTS `subscription_module_subscriptionplan`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `subscription_module_subscriptionplan` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `duration_in_days` int NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `description` longtext,
  `discounted_price` decimal(10,2) DEFAULT NULL,
  `file_upload_limit` int NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `original_price` decimal(10,2) NOT NULL,
  `storage_limit_mb` int NOT NULL,
  `subscription_type` varchar(20) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `max_devices` int NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `subscription_module_subscriptionplan`
--

LOCK TABLES `subscription_module_subscriptionplan` WRITE;
/*!40000 ALTER TABLE `subscription_module_subscriptionplan` DISABLE KEYS */;
INSERT INTO `subscription_module_subscriptionplan` VALUES (1,'Legacy Default Plan',30,'2025-08-04 05:11:39.546590','Default plan for existing users',NULL,100,1,0.00,102400,'monthly','2025-08-04 05:54:49.266681',1);
/*!40000 ALTER TABLE `subscription_module_subscriptionplan` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `subscription_module_usersubscription`
--

DROP TABLE IF EXISTS `subscription_module_usersubscription`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `subscription_module_usersubscription` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `start_date` datetime(6) NOT NULL,
  `end_date` datetime(6) NOT NULL,
  `active` tinyint(1) NOT NULL,
  `plan_id` bigint DEFAULT NULL,
  `user_id` bigint NOT NULL,
  `file_uploads_used` int NOT NULL,
  `storage_used_mb` int NOT NULL,
  `devices_used_count` int unsigned NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  UNIQUE KEY `unique_user_subscription` (`user_id`),
  KEY `subscription_module__plan_id_5bbe4cf8_fk_subscript` (`plan_id`),
  CONSTRAINT `subscription_module__plan_id_5bbe4cf8_fk_subscript` FOREIGN KEY (`plan_id`) REFERENCES `subscription_module_subscriptionplan` (`id`),
  CONSTRAINT `subscription_module__user_id_086762d5_fk_core_cust` FOREIGN KEY (`user_id`) REFERENCES `core_customuser` (`id`),
  CONSTRAINT `subscription_module_usersubscription_chk_1` CHECK ((`devices_used_count` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `subscription_module_usersubscription`
--

LOCK TABLES `subscription_module_usersubscription` WRITE;
/*!40000 ALTER TABLE `subscription_module_usersubscription` DISABLE KEYS */;
INSERT INTO `subscription_module_usersubscription` VALUES (1,'2025-08-04 05:11:58.628690','2025-09-03 05:11:58.627691',1,1,1,61,987,2);
/*!40000 ALTER TABLE `subscription_module_usersubscription` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `subscription_module_usersubscription_devices`
--

DROP TABLE IF EXISTS `subscription_module_usersubscription_devices`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `subscription_module_usersubscription_devices` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `usersubscription_id` bigint NOT NULL,
  `device_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `subscription_module_user_usersubscription_id_devi_b107c50b_uniq` (`usersubscription_id`,`device_id`),
  KEY `subscription_module__device_id_ef284652_fk_subscript` (`device_id`),
  CONSTRAINT `subscription_module__device_id_ef284652_fk_subscript` FOREIGN KEY (`device_id`) REFERENCES `subscription_module_device` (`id`),
  CONSTRAINT `subscription_module__usersubscription_id_9930a039_fk_subscript` FOREIGN KEY (`usersubscription_id`) REFERENCES `subscription_module_usersubscription` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `subscription_module_usersubscription_devices`
--

LOCK TABLES `subscription_module_usersubscription_devices` WRITE;
/*!40000 ALTER TABLE `subscription_module_usersubscription_devices` DISABLE KEYS */;
INSERT INTO `subscription_module_usersubscription_devices` VALUES (4,1,1),(2,1,2),(3,1,3);
/*!40000 ALTER TABLE `subscription_module_usersubscription_devices` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tif_to_picker_mockup`
--

DROP TABLE IF EXISTS `tif_to_picker_mockup`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tif_to_picker_mockup` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `image` varchar(100) NOT NULL,
  `description` longtext,
  `is_active` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `created_by_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `tif_to_picker_mockup_created_by_id_1eab0771_fk_core_cust` (`created_by_id`),
  CONSTRAINT `tif_to_picker_mockup_created_by_id_1eab0771_fk_core_cust` FOREIGN KEY (`created_by_id`) REFERENCES `core_customuser` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tif_to_picker_mockup`
--

LOCK TABLES `tif_to_picker_mockup` WRITE;
/*!40000 ALTER TABLE `tif_to_picker_mockup` DISABLE KEYS */;
INSERT INTO `tif_to_picker_mockup` VALUES (1,'Shirt','mockups/shirt-mask_dQ9iljq.png','Shirt mask',1,'2025-08-04 05:54:17.855276','2025-08-04 05:54:17.855276',1),(2,'Girl Hoody mask','mockups/girls-hoody-mask_INv4qRS.png','asdsa',1,'2025-08-04 05:56:25.855976','2025-08-04 05:56:25.855976',1),(3,'Dress Mask','mockups/dress-mask_6ElRCJo.png','asdsa',1,'2025-08-04 05:56:39.399480','2025-08-04 05:56:39.399480',1),(4,'Kaftan Masl','mockups/kaftan-mask_tEU31t7.png','sds',1,'2025-08-04 05:56:57.775395','2025-08-04 05:56:57.775395',1),(5,'Leggings Mask','mockups/leggings-mask_VKYffQx.png','adssa',1,'2025-08-04 05:57:14.801953','2025-08-04 05:57:14.801953',NULL);
/*!40000 ALTER TABLE `tif_to_picker_mockup` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-08-05 14:30:24
