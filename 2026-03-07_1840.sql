/*M!999999\- enable the sandbox mode */ 
-- MariaDB dump 10.19  Distrib 10.5.29-MariaDB, for debian-linux-gnueabihf (armv8l)
--
-- Host: localhost    Database: physical_music
-- ------------------------------------------------------
-- Server version	10.5.29-MariaDB-0+deb11u1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `lookup_album`
--

DROP TABLE IF EXISTS `lookup_album`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `lookup_album` (
  `album_id` int(11) NOT NULL,
  `album` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`album_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `lookup_album`
--

LOCK TABLES `lookup_album` WRITE;
/*!40000 ALTER TABLE `lookup_album` DISABLE KEYS */;
INSERT INTO `lookup_album` VALUES (3,'Aja'),(12,'Selling England By The Pound'),(51,'A Rush of Blood to the Head'),(184,'Soul Box'),(204,'Glittering Prize');
/*!40000 ALTER TABLE `lookup_album` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `lookup_artist`
--

DROP TABLE IF EXISTS `lookup_artist`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `lookup_artist` (
  `id` int(11) NOT NULL,
  `artist` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `lookup_artist`
--

LOCK TABLES `lookup_artist` WRITE;
/*!40000 ALTER TABLE `lookup_artist` DISABLE KEYS */;
INSERT INTO `lookup_artist` VALUES (5,'Steely Dan'),(10,'Genesis'),(28,'Coldplay'),(114,'Grover Washington Jr.'),(131,'Simple Minds');
/*!40000 ALTER TABLE `lookup_artist` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `lookup_bit_depth`
--

DROP TABLE IF EXISTS `lookup_bit_depth`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `lookup_bit_depth` (
  `id` int(11) NOT NULL,
  `bit_depth` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `lookup_bit_depth`
--

LOCK TABLES `lookup_bit_depth` WRITE;
/*!40000 ALTER TABLE `lookup_bit_depth` DISABLE KEYS */;
INSERT INTO `lookup_bit_depth` VALUES (1,'16-bit'),(2,'24-bit'),(3,'1-bit (DSD)');
/*!40000 ALTER TABLE `lookup_bit_depth` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `lookup_digital_format_type`
--

DROP TABLE IF EXISTS `lookup_digital_format_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `lookup_digital_format_type` (
  `id` int(11) NOT NULL,
  `digital_format_type` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `lookup_digital_format_type`
--

LOCK TABLES `lookup_digital_format_type` WRITE;
/*!40000 ALTER TABLE `lookup_digital_format_type` DISABLE KEYS */;
INSERT INTO `lookup_digital_format_type` VALUES (1,'FLAC'),(2,'DSF'),(3,'DFF'),(4,'ALAC');
/*!40000 ALTER TABLE `lookup_digital_format_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `lookup_label`
--

DROP TABLE IF EXISTS `lookup_label`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `lookup_label` (
  `id` int(11) NOT NULL,
  `label` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `lookup_label`
--

LOCK TABLES `lookup_label` WRITE;
/*!40000 ALTER TABLE `lookup_label` DISABLE KEYS */;
INSERT INTO `lookup_label` VALUES (1,'Apple'),(5,'MCA'),(10,'Charisma'),(12,'Parlophone'),(86,'Vocalion');
/*!40000 ALTER TABLE `lookup_label` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `lookup_physical_format_type`
--

DROP TABLE IF EXISTS `lookup_physical_format_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `lookup_physical_format_type` (
  `id` int(11) NOT NULL,
  `physical_format_type` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `lookup_physical_format_type`
--

LOCK TABLES `lookup_physical_format_type` WRITE;
/*!40000 ALTER TABLE `lookup_physical_format_type` DISABLE KEYS */;
INSERT INTO `lookup_physical_format_type` VALUES (1,'CD'),(2,'CD [REPACK]'),(3,'DVD-AUDIO [STEREO]'),(4,'DVD-AUDIO [SURROUND]'),(5,'DVD-VIDEO [STEREO]'),(6,'DVD-VIDEO [SURROUND]'),(7,'SACD'),(8,'SACD [REPACK]'),(9,'VINYL'),(10,'DIGITAL DOWNLOAD'),(11,'SACD POLYPOD'),(12,'CD POLYPOD'),(13,'BUBBLE UPnP'),(14,'CD POLYPOD [REPACK]'),(15,'BLU-RAY-VIDEO');
/*!40000 ALTER TABLE `lookup_physical_format_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `lookup_sample_rate`
--

DROP TABLE IF EXISTS `lookup_sample_rate`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `lookup_sample_rate` (
  `id` int(11) NOT NULL,
  `sample_rate` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `lookup_sample_rate`
--

LOCK TABLES `lookup_sample_rate` WRITE;
/*!40000 ALTER TABLE `lookup_sample_rate` DISABLE KEYS */;
INSERT INTO `lookup_sample_rate` VALUES (1,'44.1 kHz'),(2,'88.2 kHz'),(3,'96 kHz'),(4,'176.4 kHz'),(5,'192 kHz'),(6,'2.8 MHz (DSD64)');
/*!40000 ALTER TABLE `lookup_sample_rate` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `lookup_storage_location`
--

DROP TABLE IF EXISTS `lookup_storage_location`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `lookup_storage_location` (
  `id` int(11) NOT NULL,
  `storage_location` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `lookup_storage_location`
--

LOCK TABLES `lookup_storage_location` WRITE;
/*!40000 ALTER TABLE `lookup_storage_location` DISABLE KEYS */;
/*!40000 ALTER TABLE `lookup_storage_location` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `master_release_entry`
--

DROP TABLE IF EXISTS `master_release_entry`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `master_release_entry` (
  `id` int(11) NOT NULL,
  `artist` int(11) DEFAULT NULL,
  `album` int(11) DEFAULT NULL,
  `label` int(11) DEFAULT NULL,
  `catalogue_no` varchar(255) DEFAULT NULL,
  `original_release_year` int(11) DEFAULT NULL,
  `this_release_year` int(11) DEFAULT NULL,
  `physical_format_type` int(11) DEFAULT NULL,
  `storage_location` int(11) DEFAULT NULL,
  `this_release_duration` varchar(20) DEFAULT NULL,
  `average_album_dynamic_range` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `master_release_entry`
--

LOCK TABLES `master_release_entry` WRITE;
/*!40000 ALTER TABLE `master_release_entry` DISABLE KEYS */;
INSERT INTO `master_release_entry` VALUES (2,28,51,12,'543 977-2',2002,2002,1,2,'00:54:12',7),(150,114,184,86,'CDSML 8580',1973,2021,7,3,NULL,NULL),(159,5,3,5,'811 745-2',1977,1982,1,3,'00:39:59',12);
/*!40000 ALTER TABLE `master_release_entry` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `media_interaction_log`
--

DROP TABLE IF EXISTS `media_interaction_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `media_interaction_log` (
  `interaction_id` int(11) NOT NULL AUTO_INCREMENT,
  `master_release_id_(lkp)` int(11) DEFAULT NULL,
  `interaction_type` int(11) DEFAULT NULL,
  `interaction_date` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`interaction_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `media_interaction_log`
--

LOCK TABLES `media_interaction_log` WRITE;
/*!40000 ALTER TABLE `media_interaction_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `media_interaction_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `other_version_entry`
--

DROP TABLE IF EXISTS `other_version_entry`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `other_version_entry` (
  `version_id` int(11) NOT NULL AUTO_INCREMENT,
  `id` int(11) DEFAULT NULL,
  `digital_format_type` int(11) DEFAULT NULL,
  `sample_rate` int(11) DEFAULT NULL,
  `bit_depth` int(11) DEFAULT NULL,
  `rip_complete` tinyint(1) DEFAULT 0,
  PRIMARY KEY (`version_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `other_version_entry`
--

LOCK TABLES `other_version_entry` WRITE;
/*!40000 ALTER TABLE `other_version_entry` DISABLE KEYS */;
/*!40000 ALTER TABLE `other_version_entry` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-03-07 18:40:35
