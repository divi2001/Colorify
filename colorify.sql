-- MySQL dump 10.13  Distrib 9.2.0, for Win64 (x86_64)
--
-- Host: localhost    Database: colorify
-- ------------------------------------------------------
-- Server version	9.2.0

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
  `email` varchar(254) COLLATE utf8mb4_unicode_ci NOT NULL,
  `verified` tinyint(1) NOT NULL,
  `primary` tinyint(1) NOT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `account_emailaddress_user_id_email_987c8728_uniq` (`user_id`,`email`),
  KEY `account_emailaddress_email_03be32b2` (`email`),
  CONSTRAINT `account_emailaddress_user_id_2c513194_fk_core_customuser_id` FOREIGN KEY (`user_id`) REFERENCES `core_customuser` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `account_emailaddress`
--

LOCK TABLES `account_emailaddress` WRITE;
/*!40000 ALTER TABLE `account_emailaddress` DISABLE KEYS */;
INSERT INTO `account_emailaddress` VALUES (1,'deepashok20@gmail.com',1,1,1);
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
  `key` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email_address_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `key` (`key`),
  KEY `account_emailconfirm_email_address_id_5b7f8c58_fk_account_e` (`email_address_id`),
  CONSTRAINT `account_emailconfirm_email_address_id_5b7f8c58_fk_account_e` FOREIGN KEY (`email_address_id`) REFERENCES `account_emailaddress` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
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
  `name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
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
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=93 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add log entry',1,'add_logentry'),(2,'Can change log entry',1,'change_logentry'),(3,'Can delete log entry',1,'delete_logentry'),(4,'Can view log entry',1,'view_logentry'),(5,'Can add permission',2,'add_permission'),(6,'Can change permission',2,'change_permission'),(7,'Can delete permission',2,'delete_permission'),(8,'Can view permission',2,'view_permission'),(9,'Can add group',3,'add_group'),(10,'Can change group',3,'change_group'),(11,'Can delete group',3,'delete_group'),(12,'Can view group',3,'view_group'),(13,'Can add content type',4,'add_contenttype'),(14,'Can change content type',4,'change_contenttype'),(15,'Can delete content type',4,'delete_contenttype'),(16,'Can view content type',4,'view_contenttype'),(17,'Can add session',5,'add_session'),(18,'Can change session',5,'change_session'),(19,'Can delete session',5,'delete_session'),(20,'Can view session',5,'view_session'),(21,'Can add site',6,'add_site'),(22,'Can change site',6,'change_site'),(23,'Can delete site',6,'delete_site'),(24,'Can view site',6,'view_site'),(25,'Can add email address',7,'add_emailaddress'),(26,'Can change email address',7,'change_emailaddress'),(27,'Can delete email address',7,'delete_emailaddress'),(28,'Can view email address',7,'view_emailaddress'),(29,'Can add email confirmation',8,'add_emailconfirmation'),(30,'Can change email confirmation',8,'change_emailconfirmation'),(31,'Can delete email confirmation',8,'delete_emailconfirmation'),(32,'Can view email confirmation',8,'view_emailconfirmation'),(33,'Can add social account',9,'add_socialaccount'),(34,'Can change social account',9,'change_socialaccount'),(35,'Can delete social account',9,'delete_socialaccount'),(36,'Can view social account',9,'view_socialaccount'),(37,'Can add social application',10,'add_socialapp'),(38,'Can change social application',10,'change_socialapp'),(39,'Can delete social application',10,'delete_socialapp'),(40,'Can view social application',10,'view_socialapp'),(41,'Can add social application token',11,'add_socialtoken'),(42,'Can change social application token',11,'change_socialtoken'),(43,'Can delete social application token',11,'delete_socialtoken'),(44,'Can view social application token',11,'view_socialtoken'),(45,'Can add user',12,'add_customuser'),(46,'Can change user',12,'change_customuser'),(47,'Can delete user',12,'delete_customuser'),(48,'Can view user',12,'view_customuser'),(49,'Can add project',13,'add_project'),(50,'Can change project',13,'change_project'),(51,'Can delete project',13,'delete_project'),(52,'Can view project',13,'view_project'),(53,'Can add contact',14,'add_contact'),(54,'Can change contact',14,'change_contact'),(55,'Can delete contact',14,'delete_contact'),(56,'Can view contact',14,'view_contact'),(57,'Can add device',15,'add_device'),(58,'Can change device',15,'change_device'),(59,'Can delete device',15,'delete_device'),(60,'Can view device',15,'view_device'),(61,'Can add inspiration pdf',16,'add_inspirationpdf'),(62,'Can change inspiration pdf',16,'change_inspirationpdf'),(63,'Can delete inspiration pdf',16,'delete_inspirationpdf'),(64,'Can view inspiration pdf',16,'view_inspirationpdf'),(65,'Can add palette',17,'add_palette'),(66,'Can change palette',17,'change_palette'),(67,'Can delete palette',17,'delete_palette'),(68,'Can view palette',17,'view_palette'),(69,'Can add subscription plan',18,'add_subscriptionplan'),(70,'Can change subscription plan',18,'change_subscriptionplan'),(71,'Can delete subscription plan',18,'delete_subscriptionplan'),(72,'Can view subscription plan',18,'view_subscriptionplan'),(73,'Can add user subscription',19,'add_usersubscription'),(74,'Can change user subscription',19,'change_usersubscription'),(75,'Can delete user subscription',19,'delete_usersubscription'),(76,'Can view user subscription',19,'view_usersubscription'),(77,'Can add payment transaction',20,'add_paymenttransaction'),(78,'Can change payment transaction',20,'change_paymenttransaction'),(79,'Can delete payment transaction',20,'delete_paymenttransaction'),(80,'Can view payment transaction',20,'view_paymenttransaction'),(81,'Can add color',21,'add_color'),(82,'Can change color',21,'change_color'),(83,'Can delete color',21,'delete_color'),(84,'Can view color',21,'view_color'),(85,'Can add pdf like',22,'add_pdflike'),(86,'Can change pdf like',22,'change_pdflike'),(87,'Can delete pdf like',22,'delete_pdflike'),(88,'Can view pdf like',22,'view_pdflike'),(89,'Can add palette favorite',23,'add_palettefavorite'),(90,'Can change palette favorite',23,'change_palettefavorite'),(91,'Can delete palette favorite',23,'delete_palettefavorite'),(92,'Can view palette favorite',23,'view_palettefavorite');
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
  `first_name` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `last_name` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(254) COLLATE utf8mb4_unicode_ci NOT NULL,
  `phone_number` varchar(15) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `subject` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `message` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `core_contact_user_id_2570c512_fk_core_customuser_id` (`user_id`),
  CONSTRAINT `core_contact_user_id_2570c512_fk_core_customuser_id` FOREIGN KEY (`user_id`) REFERENCES `core_customuser` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
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
  `password` varchar(128) COLLATE utf8mb4_unicode_ci NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `first_name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `last_name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(254) COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  `gender` varchar(1) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `designation` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `phone_number` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `address_line` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `city` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `state` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `country` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `profile_photo` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `core_customuser`
--

LOCK TABLES `core_customuser` WRITE;
/*!40000 ALTER TABLE `core_customuser` DISABLE KEYS */;
INSERT INTO `core_customuser` VALUES (1,'pbkdf2_sha256$600000$UsmAECOsIrUbKy6OhdAjWg$1gf8tguamqj8nHhdBs3mnGCZsvvf9hDfLEq3FBmOgWc=','2025-05-11 07:35:43.130238',1,'divyang20','','','deepashok20@gmail.com',1,1,'2025-05-02 02:52:08.641347',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'');
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
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
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `slug` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `modified_at` datetime(6) NOT NULL,
  `exported_at` datetime(6) DEFAULT NULL,
  `original_file` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `exported_image` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `original_filename` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `slug` (`slug`),
  KEY `core_project_user_id_8670f2b9_fk_core_customuser_id` (`user_id`),
  CONSTRAINT `core_project_user_id_8670f2b9_fk_core_customuser_id` FOREIGN KEY (`user_id`) REFERENCES `core_customuser` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `core_project`
--

LOCK TABLES `core_project` WRITE;
/*!40000 ALTER TABLE `core_project` DISABLE KEYS */;
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
  `object_id` longtext COLLATE utf8mb4_unicode_ci,
  `object_repr` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `action_flag` smallint unsigned NOT NULL,
  `change_message` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_core_customuser_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_core_customuser_id` FOREIGN KEY (`user_id`) REFERENCES `core_customuser` (`id`),
  CONSTRAINT `django_admin_log_chk_1` CHECK ((`action_flag` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_cache_table`
--

DROP TABLE IF EXISTS `django_cache_table`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_cache_table` (
  `cache_key` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `value` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `expires` datetime(6) NOT NULL,
  PRIMARY KEY (`cache_key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_cache_table`
--

LOCK TABLES `django_cache_table` WRITE;
/*!40000 ALTER TABLE `django_cache_table` DISABLE KEYS */;
INSERT INTO `django_cache_table` VALUES (':1:allauth:rl:login:ip:127.0.0.1','gAWVDQAAAAAAAABdlEdB2ggU070lmmEu','2025-05-11 07:36:42.000000'),(':1:django.contrib.sessions.cached_dbic0bkbsjm5e8esw1mntji6zxrzf8o9e7','gAWVOgEAAAAAAAB9lCiMHmFjY291bnRfYXV0aGVudGljYXRpb25fbWV0aG9kc5RdlH2UKIwGbWV0aG9klIwIcGFzc3dvcmSUjAJhdJRHQdoIFNPH56mMBWVtYWlslIwVZGVlcGFzaG9rMjBAZ21haWwuY29tlHVhjA1fYXV0aF91c2VyX2lklIwBMZSMEl9hdXRoX3VzZXJfYmFja2VuZJSMM2FsbGF1dGguYWNjb3VudC5hdXRoX2JhY2tlbmRzLkF1dGhlbnRpY2F0aW9uQmFja2VuZJSMD19hdXRoX3VzZXJfaGFzaJSMQDI3Nzk4NWIzZDYzMDgxNTM1NzZmZGI4ODI0NWNhNzg5Yjg0YTBmNzZjYjU1YTIzODRmNzE0MDJjMzNkYTNiNTeUjA9fc2Vzc2lvbl9leHBpcnmUSoBRAQB1Lg==','2025-05-12 07:35:43.000000'),(':1:django.contrib.sessions.cached_dbsz5ygf21wjrt0izamjciq58zu0e2mxa3','gAWVrwAAAAAAAAB9lCiMDV9hdXRoX3VzZXJfaWSUjAExlIwSX2F1dGhfdXNlcl9iYWNrZW5klIwpZGphbmdvLmNvbnRyaWIuYXV0aC5iYWNrZW5kcy5Nb2RlbEJhY2tlbmSUjA9fYXV0aF91c2VyX2hhc2iUjEAyNzc5ODViM2Q2MzA4MTUzNTc2ZmRiODgyNDVjYTc4OWI4NGEwZjc2Y2I1NWEyMzg0ZjcxNDAyYzMzZGEzYjU3lHUu','2025-05-03 02:54:45.000000'),(':1:last_activity_1','gAWVVwAAAAAAAACMCGRhdGV0aW1llIwIZGF0ZXRpbWWUk5RDCgfpBQsHKiIEpTuUaACMCHRpbWV6b25llJOUaACMCXRpbWVkZWx0YZSTlEsASwBLAIeUUpSFlFKUhpRSlC4=','9999-12-31 23:59:59.000000'),(':1:user_session_1','gAWVJAAAAAAAAACMIGljMGJrYnNqbTVlOGVzdzFtbnRqaTZ6eHJ6ZjhvOWU3lC4=','9999-12-31 23:59:59.000000');
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
  `app_label` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `model` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (7,'account','emailaddress'),(8,'account','emailconfirmation'),(1,'admin','logentry'),(3,'auth','group'),(2,'auth','permission'),(4,'contenttypes','contenttype'),(14,'core','contact'),(12,'core','customuser'),(13,'core','project'),(5,'sessions','session'),(6,'sites','site'),(9,'socialaccount','socialaccount'),(10,'socialaccount','socialapp'),(11,'socialaccount','socialtoken'),(21,'subscription_module','color'),(15,'subscription_module','device'),(16,'subscription_module','inspirationpdf'),(17,'subscription_module','palette'),(23,'subscription_module','palettefavorite'),(20,'subscription_module','paymenttransaction'),(22,'subscription_module','pdflike'),(18,'subscription_module','subscriptionplan'),(19,'subscription_module','usersubscription');
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
  `app` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=41 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (1,'contenttypes','0001_initial','2025-05-02 02:28:31.721570'),(2,'contenttypes','0002_remove_content_type_name','2025-05-02 02:28:31.777117'),(3,'auth','0001_initial','2025-05-02 02:28:31.960070'),(4,'auth','0002_alter_permission_name_max_length','2025-05-02 02:28:32.007309'),(5,'auth','0003_alter_user_email_max_length','2025-05-02 02:28:32.010749'),(6,'auth','0004_alter_user_username_opts','2025-05-02 02:28:32.010749'),(7,'auth','0005_alter_user_last_login_null','2025-05-02 02:28:32.010749'),(8,'auth','0006_require_contenttypes_0002','2025-05-02 02:28:32.010749'),(9,'auth','0007_alter_validators_add_error_messages','2025-05-02 02:28:32.010749'),(10,'auth','0008_alter_user_username_max_length','2025-05-02 02:28:32.029080'),(11,'auth','0009_alter_user_last_name_max_length','2025-05-02 02:28:32.032424'),(12,'auth','0010_alter_group_name_max_length','2025-05-02 02:28:32.039648'),(13,'auth','0011_update_proxy_permissions','2025-05-02 02:28:32.043545'),(14,'auth','0012_alter_user_first_name_max_length','2025-05-02 02:28:32.049741'),(15,'core','0001_initial','2025-05-02 02:28:32.354306'),(16,'account','0001_initial','2025-05-02 02:28:32.490483'),(17,'account','0002_email_max_length','2025-05-02 02:28:32.509987'),(18,'account','0003_alter_emailaddress_create_unique_verified_email','2025-05-02 02:28:32.546248'),(19,'account','0004_alter_emailaddress_drop_unique_email','2025-05-02 02:28:32.571217'),(20,'account','0005_emailaddress_idx_upper_email','2025-05-02 02:28:32.587594'),(21,'account','0006_emailaddress_lower','2025-05-02 02:28:32.593605'),(22,'account','0007_emailaddress_idx_email','2025-05-02 02:28:32.623047'),(23,'account','0008_emailaddress_unique_primary_email_fixup','2025-05-02 02:28:32.630852'),(24,'account','0009_emailaddress_unique_primary_email','2025-05-02 02:28:32.636940'),(25,'admin','0001_initial','2025-05-02 02:28:32.719941'),(26,'admin','0002_logentry_remove_auto_add','2025-05-02 02:28:32.735734'),(27,'admin','0003_logentry_add_action_flag_choices','2025-05-02 02:28:32.743332'),(28,'sessions','0001_initial','2025-05-02 02:28:32.765756'),(29,'sites','0001_initial','2025-05-02 02:28:32.781940'),(30,'sites','0002_alter_domain_unique','2025-05-02 02:28:32.793315'),(31,'socialaccount','0001_initial','2025-05-02 02:28:33.085953'),(32,'socialaccount','0002_token_max_lengths','2025-05-02 02:28:33.116666'),(33,'socialaccount','0003_extra_data_default_dict','2025-05-02 02:28:33.121508'),(34,'socialaccount','0004_app_provider_id_settings','2025-05-02 02:28:33.234833'),(35,'socialaccount','0005_socialtoken_nullable_app','2025-05-02 02:28:33.315009'),(36,'socialaccount','0006_alter_socialaccount_extra_data','2025-05-02 02:28:33.371691'),(37,'subscription_module','0001_initial','2025-05-02 02:28:34.094180'),(38,'subscription_module','0002_auto_20250510_1238','2025-05-10 07:12:40.935307'),(39,'subscription_module','0003_make_subscription_plan_non_nullable','2025-05-10 07:12:41.079614'),(40,'subscription_module','0004_remove_usersubscription_max_devices_and_more','2025-05-10 07:18:31.531268');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) COLLATE utf8mb4_unicode_ci NOT NULL,
  `session_data` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
INSERT INTO `django_session` VALUES ('ic0bkbsjm5e8esw1mntji6zxrzf8o9e7','.eJxVkM1ugzAQhN9lzwj534ZT09eoIrT-oaAAjrBRWkV59-KUC7fVzOy3o30COhe3JXe45SEseXSYx7h0c8hD9Anaryf8z9DCHVN6xNVDBZihpVqoRphG8JoyLqkQFYQZx2mP-hD29BBvjHx8F612cYbXtYL3pW5LYe3GAqVw0iy6W1iKgdNU5PpoWL8zh53qy6nv57F1Qg17gZ3DtG6MtNwrTgyVXGrVe2sME9KhNo01AkmvlbNSIuNG9JoKwhznHrmVukBTSKm8Jfzcx_UXWqMEIa8_Wplovg:1uE1Dr:7BnxA0RPzk3gptnwPlHH-2ZFc-7OX_QMBsdGfstBnzQ','2025-05-12 07:35:43.142586'),('sz5ygf21wjrt0izamjciq58zu0e2mxa3','.eJxVjEEOgjAQRe_StWmg0-kMLt17BjLTUosaSCisjHdXEha6_e-9_zK9bGvptzos_ZjM2bTm9LupxMcw7SDdZbrNNs7Tuoxqd8UetNrrnIbn5XD_DorU8q0dUceokAI03CIghZyU2XmMQtwpe2kyhaiI4oB9ptY3LgIkAUUy7w-xeTbB:1uAgY1:8jClI0ojk6Qy7P0V8sf0xaPB7RPwP_dImBKeZCpxyv4','2025-05-03 02:54:45.919569');
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
  `domain` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_site_domain_a2e37b91_uniq` (`domain`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
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
-- Table structure for table `socialaccount_socialaccount`
--

DROP TABLE IF EXISTS `socialaccount_socialaccount`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `socialaccount_socialaccount` (
  `id` int NOT NULL AUTO_INCREMENT,
  `provider` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `uid` varchar(191) COLLATE utf8mb4_unicode_ci NOT NULL,
  `last_login` datetime(6) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  `extra_data` json NOT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `socialaccount_socialaccount_provider_uid_fc810c6e_uniq` (`provider`,`uid`),
  KEY `socialaccount_social_user_id_8146e70c_fk_core_cust` (`user_id`),
  CONSTRAINT `socialaccount_social_user_id_8146e70c_fk_core_cust` FOREIGN KEY (`user_id`) REFERENCES `core_customuser` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
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
  `provider` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(40) COLLATE utf8mb4_unicode_ci NOT NULL,
  `client_id` varchar(191) COLLATE utf8mb4_unicode_ci NOT NULL,
  `secret` varchar(191) COLLATE utf8mb4_unicode_ci NOT NULL,
  `key` varchar(191) COLLATE utf8mb4_unicode_ci NOT NULL,
  `provider_id` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `settings` json NOT NULL DEFAULT (_utf8mb3'{}'),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
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
  `token` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `token_secret` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `expires_at` datetime(6) DEFAULT NULL,
  `account_id` int NOT NULL,
  `app_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `socialaccount_socialtoken_app_id_account_id_fca4e0ac_uniq` (`app_id`,`account_id`),
  KEY `socialaccount_social_account_id_951f210e_fk_socialacc` (`account_id`),
  CONSTRAINT `socialaccount_social_account_id_951f210e_fk_socialacc` FOREIGN KEY (`account_id`) REFERENCES `socialaccount_socialaccount` (`id`),
  CONSTRAINT `socialaccount_social_app_id_636a42d7_fk_socialacc` FOREIGN KEY (`app_id`) REFERENCES `socialaccount_socialapp` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `socialaccount_socialtoken`
--

LOCK TABLES `socialaccount_socialtoken` WRITE;
/*!40000 ALTER TABLE `socialaccount_socialtoken` DISABLE KEYS */;
/*!40000 ALTER TABLE `socialaccount_socialtoken` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `subscription_module_color`
--

DROP TABLE IF EXISTS `subscription_module_color`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `subscription_module_color` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `red` int NOT NULL,
  `green` int NOT NULL,
  `blue` int NOT NULL,
  `palette_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `subscription_module__palette_id_8e7e45ec_fk_subscript` (`palette_id`),
  CONSTRAINT `subscription_module__palette_id_8e7e45ec_fk_subscript` FOREIGN KEY (`palette_id`) REFERENCES `subscription_module_palette` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=34 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `subscription_module_color`
--

LOCK TABLES `subscription_module_color` WRITE;
/*!40000 ALTER TABLE `subscription_module_color` DISABLE KEYS */;
INSERT INTO `subscription_module_color` VALUES (1,'',0,32,46,1),(2,'',0,63,92,1),(3,'',44,72,117,1),(4,'',138,80,143,1),(5,'',188,80,144,1),(6,'',255,99,97,1),(7,'',255,133,49,1),(8,'',255,166,0,1),(9,'',255,211,128,1),(10,'',233,233,233,2),(11,'',224,179,132,2),(12,'',107,221,176,2),(13,'',160,138,111,2),(14,'',35,61,46,2),(15,'',80,107,92,2),(16,'',20,23,3,2),(17,'',157,221,231,2),(18,'',242,242,242,3),(19,'',161,227,148,3),(20,'',122,128,223,3),(21,'',125,165,120,3),(22,'',37,43,64,3),(23,'',85,91,112,3),(24,'',3,23,12,3),(25,'',203,174,234,3),(26,'',242,242,242,4),(27,'',229,200,227,4),(28,'',212,218,175,4),(29,'',174,151,172,4),(30,'',67,66,48,4),(31,'',122,121,103,4),(32,'',19,7,11,4),(33,'',230,241,225,4);
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
  `device_id` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `device_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `last_login` datetime(6) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `device_id` (`device_id`),
  KEY `subscription_module__user_id_a7f4b4c6_fk_core_cust` (`user_id`),
  CONSTRAINT `subscription_module__user_id_a7f4b4c6_fk_core_cust` FOREIGN KEY (`user_id`) REFERENCES `core_customuser` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `subscription_module_device`
--

LOCK TABLES `subscription_module_device` WRITE;
/*!40000 ALTER TABLE `subscription_module_device` DISABLE KEYS */;
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
  `title` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `pdf_file` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `preview_image` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `likes_count` int NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
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
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `num_colors` int NOT NULL,
  `base_color` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `base_color_r` int NOT NULL,
  `base_color_g` int NOT NULL,
  `base_color_b` int NOT NULL,
  `type` varchar(2) COLLATE utf8mb4_unicode_ci NOT NULL,
  `favorites_count` int unsigned NOT NULL,
  `creator_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `subscription_module__creator_id_ab6e04de_fk_core_cust` (`creator_id`),
  CONSTRAINT `subscription_module__creator_id_ab6e04de_fk_core_cust` FOREIGN KEY (`creator_id`) REFERENCES `core_customuser` (`id`),
  CONSTRAINT `subscription_module_palette_chk_1` CHECK ((`favorites_count` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `subscription_module_palette`
--

LOCK TABLES `subscription_module_palette` WRITE;
/*!40000 ALTER TABLE `subscription_module_palette` DISABLE KEYS */;
INSERT INTO `subscription_module_palette` VALUES (1,'TRENDING Palette 0','2025-05-11 07:36:02.667922','2025-05-11 07:36:02.667922',9,'Generated',0,32,46,'TR',0,1),(2,'TRENDING Palette 1','2025-05-11 07:36:10.715936','2025-05-11 07:36:10.715936',8,'Generated',233,233,233,'TR',0,1),(3,'TRENDING Palette 7','2025-05-11 07:36:41.775953','2025-05-11 07:36:41.775953',8,'Generated',242,242,242,'TR',1,1),(4,'TRENDING Palette 8','2025-05-11 07:37:06.001993','2025-05-11 07:37:06.001993',8,'Generated',242,242,242,'TR',1,1);
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
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `subscription_module_palettefavorite`
--

LOCK TABLES `subscription_module_palettefavorite` WRITE;
/*!40000 ALTER TABLE `subscription_module_palettefavorite` DISABLE KEYS */;
INSERT INTO `subscription_module_palettefavorite` VALUES (3,'2025-05-11 07:36:41.800710',3,1),(4,'2025-05-11 07:37:06.026438',4,1);
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
  `transaction_id` char(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  `transaction_type` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `payment_gateway_reference` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `payment_method` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `metadata` json NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `subscription_plan_id` bigint NOT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `transaction_id` (`transaction_id`),
  KEY `subscription_module__user_id_b1b0c0cc_fk_core_cust` (`user_id`),
  KEY `subscription_module__subscription_plan_id_7149568b_fk_subscript` (`subscription_plan_id`),
  CONSTRAINT `subscription_module__subscription_plan_id_7149568b_fk_subscript` FOREIGN KEY (`subscription_plan_id`) REFERENCES `subscription_module_subscriptionplan` (`id`),
  CONSTRAINT `subscription_module__user_id_b1b0c0cc_fk_core_cust` FOREIGN KEY (`user_id`) REFERENCES `core_customuser` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `subscription_module_pdflike`
--

LOCK TABLES `subscription_module_pdflike` WRITE;
/*!40000 ALTER TABLE `subscription_module_pdflike` DISABLE KEYS */;
/*!40000 ALTER TABLE `subscription_module_pdflike` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `subscription_module_subscriptionplan`
--

DROP TABLE IF EXISTS `subscription_module_subscriptionplan`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `subscription_module_subscriptionplan` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` longtext COLLATE utf8mb4_unicode_ci,
  `subscription_type` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `duration_in_days` int NOT NULL,
  `original_price` decimal(10,2) NOT NULL,
  `discounted_price` decimal(10,2) DEFAULT NULL,
  `file_upload_limit` int NOT NULL,
  `storage_limit_mb` int NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `max_devices` int NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `subscription_module_subscriptionplan`
--

LOCK TABLES `subscription_module_subscriptionplan` WRITE;
/*!40000 ALTER TABLE `subscription_module_subscriptionplan` DISABLE KEYS */;
INSERT INTO `subscription_module_subscriptionplan` VALUES (1,'Legacy Default Plan','Default plan for legacy payment transactions','monthly',30,0.00,0.00,1,100,0,'2025-05-10 07:12:40.961261','2025-05-10 07:12:40.961261',1);
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
  `file_uploads_used` int NOT NULL,
  `storage_used_mb` int NOT NULL,
  `plan_id` bigint DEFAULT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  KEY `subscription_module__plan_id_5bbe4cf8_fk_subscript` (`plan_id`),
  CONSTRAINT `subscription_module__plan_id_5bbe4cf8_fk_subscript` FOREIGN KEY (`plan_id`) REFERENCES `subscription_module_subscriptionplan` (`id`),
  CONSTRAINT `subscription_module__user_id_086762d5_fk_core_cust` FOREIGN KEY (`user_id`) REFERENCES `core_customuser` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `subscription_module_usersubscription`
--

LOCK TABLES `subscription_module_usersubscription` WRITE;
/*!40000 ALTER TABLE `subscription_module_usersubscription` DISABLE KEYS */;
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `subscription_module_usersubscription_devices`
--

LOCK TABLES `subscription_module_usersubscription_devices` WRITE;
/*!40000 ALTER TABLE `subscription_module_usersubscription_devices` DISABLE KEYS */;
/*!40000 ALTER TABLE `subscription_module_usersubscription_devices` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-05-11 13:14:47
