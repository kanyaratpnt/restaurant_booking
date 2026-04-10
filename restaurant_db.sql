/*M!999999\- enable the sandbox mode */ 
-- MariaDB dump 10.19-12.2.2-MariaDB, for osx10.21 (arm64)
--
-- Host: 192.168.1.41    Database: restaurant_db
-- ------------------------------------------------------
-- Server version	12.2.2-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*M!100616 SET @OLD_NOTE_VERBOSITY=@@NOTE_VERBOSITY, NOTE_VERBOSITY=0 */;

--
-- Table structure for table `customers`
--

DROP TABLE IF EXISTS `customers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `customers` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `phone` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `customers`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `customers` WRITE;
/*!40000 ALTER TABLE `customers` DISABLE KEYS */;
INSERT INTO `customers` VALUES
(1,'0863799742','0863799742'),
(2,'0987899876','0987899876'),
(3,'beam','0865788975'),
(5,'Moowan','0876455678'),
(7,'Moonlight','000-000-0000'),
(8,'ShuShu','0895742215'),
(9,'0852799742','0852799742'),
(11,'086356678','086356678'),
(12,'0876899765','0876899765'),
(13,'0863755246','0863755246'),
(14,'0987889863','0987889863'),
(15,'096788987','096788987'),
(16,'0863255412','0863255412'),
(17,'085422563','085422563'),
(18,'0854255638','0854255638');
/*!40000 ALTER TABLE `customers` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `otp_sessions`
--

DROP TABLE IF EXISTS `otp_sessions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `otp_sessions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `phone` varchar(20) NOT NULL,
  `otp_code` varchar(6) NOT NULL,
  `is_used` tinyint(1) DEFAULT 0,
  `created_at` datetime DEFAULT current_timestamp(),
  `expires_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `otp_sessions`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `otp_sessions` WRITE;
/*!40000 ALTER TABLE `otp_sessions` DISABLE KEYS */;
INSERT INTO `otp_sessions` VALUES
(1,'0863799742','374678',1,'2026-04-05 18:54:59','2026-04-05 18:59:59'),
(2,'0863799742','386931',1,'2026-04-05 19:39:27','2026-04-05 19:44:27'),
(3,'0863799742','745327',1,'2026-04-06 16:34:49','2026-04-06 16:39:49'),
(4,'0863799742','878806',1,'2026-04-06 17:19:53','2026-04-06 17:24:53'),
(5,'0863799742','147638',1,'2026-04-08 06:10:25','2026-04-08 06:15:24'),
(6,'0986890034','661659',0,'2026-04-08 06:12:15','2026-04-08 06:17:15'),
(7,'0863700742','915284',0,'2026-04-08 06:13:14','2026-04-08 06:18:14'),
(8,'0987899876','770254',1,'2026-04-08 16:48:17','2026-04-08 16:53:17'),
(9,'0863799742','957455',1,'2026-04-09 04:53:50','2026-04-09 04:58:50'),
(10,'0852799742','909521',1,'2026-04-09 05:24:31','2026-04-09 05:29:31'),
(11,'086356678','957632',1,'2026-04-09 07:23:23','2026-04-09 07:28:23'),
(12,'0876899765','509726',1,'2026-04-09 14:46:30','2026-04-09 14:51:30'),
(13,'0863755246','196759',1,'2026-04-09 15:11:47','2026-04-09 15:16:47'),
(14,'0987889863','656866',1,'2026-04-09 15:14:48','2026-04-09 15:19:48'),
(15,'096788987','679935',1,'2026-04-09 15:45:55','2026-04-09 15:50:55'),
(16,'0863255412','433752',1,'2026-04-09 15:51:05','2026-04-09 15:56:05'),
(17,'085422563','853773',1,'2026-04-09 15:52:31','2026-04-09 15:57:31'),
(18,'0854255638','581639',1,'2026-04-09 15:56:36','2026-04-09 16:01:36');
/*!40000 ALTER TABLE `otp_sessions` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `reservations`
--

DROP TABLE IF EXISTS `reservations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `reservations` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `table_id` int(11) DEFAULT NULL,
  `customer_id` int(11) DEFAULT NULL,
  `guest_count` int(11) NOT NULL,
  `reservation_time` datetime NOT NULL,
  `status` enum('pending','confirmed','cancelled') DEFAULT 'pending',
  `occasion` varchar(50) DEFAULT NULL,
  `special_requests` text DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `table_id` (`table_id`),
  KEY `customer_id` (`customer_id`),
  CONSTRAINT `1` FOREIGN KEY (`table_id`) REFERENCES `tables` (`id`),
  CONSTRAINT `2` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `reservations`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `reservations` WRITE;
/*!40000 ALTER TABLE `reservations` DISABLE KEYS */;
INSERT INTO `reservations` VALUES
(1,9,3,2,'2026-04-15 20:00:00','cancelled','birthday','[เค้ก: Chocolate Fondant] ',NULL),
(2,1,3,2,'2026-04-14 20:00:00','cancelled','first_date','ขอดอกกุหลาบ 1000 ดอก ตกแต่งรอบโต๊ะ',NULL),
(3,9,5,3,'2026-04-22 19:00:00','cancelled','birthday','[เค้ก: Chocolate Fondant] จัดเตรียมอาหารวีแกน','0876455678'),
(4,10,1,4,'2026-04-26 20:00:00','confirmed','general','ช่วยจัดดอกไม้สีขาวรอบโต๊ะ','0867899963'),
(5,5,1,2,'2026-04-26 20:00:00','cancelled','anniversary','','0863799742'),
(6,6,1,2,'2026-04-12 20:00:00','cancelled','general','แพ้กุ้งและสัตว์มีเปลือก','0863799742'),
(7,1,8,2,'2026-04-13 11:00:00','pending','birthday','[เค้ก: Sweet Strawberry] แพ้แป้งและถั่วทุกชนิด\n','0895742215');
/*!40000 ALTER TABLE `reservations` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `tables`
--

DROP TABLE IF EXISTS `tables`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tables` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `table_number` varchar(10) NOT NULL,
  `capacity` int(11) NOT NULL,
  `status` enum('available','occupied','reserved') DEFAULT 'available',
  `position_x` float DEFAULT 0,
  `position_y` float DEFAULT 0,
  `zone` varchar(50) DEFAULT 'outdoor',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tables`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `tables` WRITE;
/*!40000 ALTER TABLE `tables` DISABLE KEYS */;
INSERT INTO `tables` VALUES
(1,'A1',2,'reserved',280,300,'seaview'),
(2,'A2',2,'available',280,400,'seaview'),
(3,'A3',2,'available',280,500,'seaview'),
(4,'A4',2,'available',280,600,'seaview'),
(5,'B1',4,'available',180,300,'indoor'),
(6,'B2',4,'available',180,400,'indoor'),
(7,'B3',4,'available',180,500,'indoor'),
(8,'B4',4,'available',180,600,'indoor'),
(9,'C1',4,'available',140,20,'outdoor'),
(10,'C2',4,'reserved',250,20,'outdoor'),
(11,'C3',4,'available',140,120,'outdoor'),
(12,'C4',4,'available',250,120,'outdoor'),
(13,'D1',4,'available',140,750,'private'),
(14,'D2',4,'available',250,750,'private'),
(15,'D3',4,'available',140,850,'private'),
(16,'D4',4,'available',250,850,'private'),
(17,'E1',10,'available',10,30,'outdoor'),
(18,'F1',10,'available',10,770,'private');
/*!40000 ALTER TABLE `tables` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `role` varchar(50) NOT NULL DEFAULT 'customer',
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

SET @OLD_AUTOCOMMIT=@@AUTOCOMMIT, @@AUTOCOMMIT=0;
LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES
(1,'restaurant','$2b$12$5ESzjbT03eqsSSTELz/6ouec85m0QJ9kvOI6SkG/WXS9/sDyCjcq6','restaurant'),
(2,'kanyarat','$2b$12$OfelU3tRun1A1w18sYOvnuEqvd7Fqvm8UYuZfJrgY8XGfpQ2gwu5W','customer'),
(3,'beam','$2b$12$xyO6Xm0y5z8Oe6sIoZ9me.l3TVwCoYHxEugnaUp8uJBfuiQ9LxBei','customer'),
(4,'wanwan','$2b$12$OT9p/VY2iMip.IE5VJhH3ePO4T1JFQdBw7vl.BHMNYdvKRxJHCLCq','customer'),
(5,'Moowan','$2b$12$IVeJWp4MC3kmSk.gRohY3O1DEeFM3I3DSSirAynJG7H23vewnw27i','customer'),
(6,'BlueBee','$2b$12$4XtVdBbesW/SK8smDh3CKu1NGjjLz2.I.6NPLr4YUW/dLmcD2UXXK','customer'),
(7,'Moonlight','$2b$12$utzJku5znVrqTFp1r/ufx.UJ2zzzv0VswAeMTJYl5mZp2CKtsh6g2','customer'),
(8,'ShuShu','$2b$12$v218irWIkp1wM1U/1vNEfuBYc1OYSYCFWEHO5IXGyibFICGIP.opu','customer');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
COMMIT;
SET AUTOCOMMIT=@OLD_AUTOCOMMIT;

--
-- Dumping routines for database 'restaurant_db'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*M!100616 SET NOTE_VERBOSITY=@OLD_NOTE_VERBOSITY */;

-- Dump completed on 2026-04-11  0:24:28
