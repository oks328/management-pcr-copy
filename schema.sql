-- MariaDB dump 10.19  Distrib 10.4.32-MariaDB, for Win64 (AMD64)
--
-- Host: localhost    Database: ipcr_db
-- ------------------------------------------------------
-- Server version	10.4.32-MariaDB

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
-- Table structure for table `tbl_academic_terms`
--

DROP TABLE IF EXISTS `tbl_academic_terms`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tbl_academic_terms` (
  `term_id` int(11) NOT NULL AUTO_INCREMENT,
  `academic_year` varchar(20) NOT NULL,
  `semester` varchar(20) NOT NULL,
  `deadline_date` date DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT 0,
  PRIMARY KEY (`term_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tbl_auth_credentials`
--

DROP TABLE IF EXISTS `tbl_auth_credentials`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tbl_auth_credentials` (
  `emp_id` varchar(50) NOT NULL,
  `corporate_email` varchar(150) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `verification_status` enum('PENDING','APPROVED','REJECTED') DEFAULT 'PENDING',
  `last_login` datetime DEFAULT NULL,
  PRIMARY KEY (`emp_id`),
  UNIQUE KEY `corporate_email` (`corporate_email`),
  CONSTRAINT `fk_auth_emp` FOREIGN KEY (`emp_id`) REFERENCES `tbl_employee_profiles` (`emp_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tbl_cascaded_quotas`
--

DROP TABLE IF EXISTS `tbl_cascaded_quotas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tbl_cascaded_quotas` (
  `quota_id` int(11) NOT NULL AUTO_INCREMENT,
  `term_id` int(11) DEFAULT NULL,
  `indicator_id` int(11) DEFAULT NULL,
  `total_target_value` int(11) NOT NULL,
  `assigned_to_role` varchar(100) NOT NULL,
  PRIMARY KEY (`quota_id`),
  KEY `fk_quota_term` (`term_id`),
  KEY `fk_quota_indicator` (`indicator_id`),
  CONSTRAINT `fk_quota_indicator` FOREIGN KEY (`indicator_id`) REFERENCES `tbl_master_indicators` (`indicator_id`),
  CONSTRAINT `fk_quota_term` FOREIGN KEY (`term_id`) REFERENCES `tbl_academic_terms` (`term_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tbl_co_authors`
--

DROP TABLE IF EXISTS `tbl_co_authors`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tbl_co_authors` (
  `co_author_id` int(11) NOT NULL AUTO_INCREMENT,
  `evidence_id` int(11) DEFAULT NULL,
  `emp_id` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`co_author_id`),
  KEY `fk_coauthor_evidence` (`evidence_id`),
  KEY `fk_coauthor_emp` (`emp_id`),
  CONSTRAINT `fk_coauthor_emp` FOREIGN KEY (`emp_id`) REFERENCES `tbl_employee_profiles` (`emp_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_coauthor_evidence` FOREIGN KEY (`evidence_id`) REFERENCES `tbl_evidence_repo` (`evidence_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tbl_committed_targets`
--

DROP TABLE IF EXISTS `tbl_committed_targets`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tbl_committed_targets` (
  `target_id` int(11) NOT NULL AUTO_INCREMENT,
  `emp_id` varchar(50) DEFAULT NULL,
  `term_id` int(11) DEFAULT NULL,
  `indicator_id` int(11) DEFAULT NULL,
  `tab_category` enum('Standard','75_Admin','25_Instruction') DEFAULT 'Standard',
  `assigned_quantity` int(11) NOT NULL,
  `status` varchar(50) DEFAULT 'Draft',
  PRIMARY KEY (`target_id`),
  KEY `fk_target_emp` (`emp_id`),
  KEY `fk_target_term` (`term_id`),
  KEY `fk_target_indicator` (`indicator_id`),
  CONSTRAINT `fk_target_emp` FOREIGN KEY (`emp_id`) REFERENCES `tbl_employee_profiles` (`emp_id`),
  CONSTRAINT `fk_target_indicator` FOREIGN KEY (`indicator_id`) REFERENCES `tbl_master_indicators` (`indicator_id`),
  CONSTRAINT `fk_target_term` FOREIGN KEY (`term_id`) REFERENCES `tbl_academic_terms` (`term_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tbl_designation_targets`
--

DROP TABLE IF EXISTS `tbl_designation_targets`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tbl_designation_targets` (
  `template_id` int(11) NOT NULL AUTO_INCREMENT,
  `designation_role` varchar(100) NOT NULL,
  `indicator_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`template_id`),
  KEY `fk_designation_indicator` (`indicator_id`),
  CONSTRAINT `fk_designation_indicator` FOREIGN KEY (`indicator_id`) REFERENCES `tbl_master_indicators` (`indicator_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tbl_employee_profiles`
--

DROP TABLE IF EXISTS `tbl_employee_profiles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tbl_employee_profiles` (
  `emp_id` varchar(50) NOT NULL,
  `first_name` varchar(100) NOT NULL,
  `last_name` varchar(100) NOT NULL,
  `college` varchar(100) NOT NULL DEFAULT 'CICT',
  `assigned_program` varchar(100) NOT NULL,
  `academic_rank` varchar(50) NOT NULL,
  `employment_status` varchar(50) NOT NULL,
  `designation` varchar(100) DEFAULT 'None',
  `leave_status` varchar(50) DEFAULT 'Active',
  PRIMARY KEY (`emp_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tbl_evidence_repo`
--

DROP TABLE IF EXISTS `tbl_evidence_repo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tbl_evidence_repo` (
  `evidence_id` int(11) NOT NULL AUTO_INCREMENT,
  `target_id` int(11) DEFAULT NULL,
  `file_path` varchar(255) NOT NULL,
  `actual_qty_Q` int(11) DEFAULT 0,
  `timeliness_T` decimal(5,2) DEFAULT NULL,
  `efficiency_rating_E` int(11) DEFAULT NULL,
  `verification_status` varchar(50) DEFAULT 'Pending',
  `supervisor_comment` text DEFAULT NULL,
  PRIMARY KEY (`evidence_id`),
  KEY `fk_evidence_target` (`target_id`),
  CONSTRAINT `fk_evidence_target` FOREIGN KEY (`target_id`) REFERENCES `tbl_committed_targets` (`target_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tbl_final_scores`
--

DROP TABLE IF EXISTS `tbl_final_scores`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tbl_final_scores` (
  `score_id` int(11) NOT NULL AUTO_INCREMENT,
  `emp_id` varchar(50) DEFAULT NULL,
  `term_id` int(11) DEFAULT NULL,
  `instruction_weighted` decimal(5,2) DEFAULT 0.00,
  `ret_weighted` decimal(5,2) DEFAULT 0.00,
  `support_weighted` decimal(5,2) DEFAULT 0.00,
  `admin_weighted` decimal(5,2) DEFAULT 0.00,
  `final_score` decimal(5,2) NOT NULL,
  `adjectival_rating` varchar(50) NOT NULL,
  `dean_approval_status` varchar(50) DEFAULT 'Pending',
  PRIMARY KEY (`score_id`),
  KEY `fk_score_emp` (`emp_id`),
  KEY `fk_score_term` (`term_id`),
  CONSTRAINT `fk_score_emp` FOREIGN KEY (`emp_id`) REFERENCES `tbl_employee_profiles` (`emp_id`),
  CONSTRAINT `fk_score_term` FOREIGN KEY (`term_id`) REFERENCES `tbl_academic_terms` (`term_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tbl_master_indicators`
--

DROP TABLE IF EXISTS `tbl_master_indicators`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tbl_master_indicators` (
  `indicator_id` int(11) NOT NULL AUTO_INCREMENT,
  `category_id` int(11) DEFAULT NULL,
  `indicator_description` text NOT NULL,
  `efficiency_type` enum('Adjectival','Client Satisfaction','Quantity-Based') NOT NULL DEFAULT 'Quantity-Based',
  `term_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`indicator_id`),
  KEY `fk_indicator_category` (`category_id`),
  KEY `fk_indicator_term` (`term_id`),
  CONSTRAINT `fk_indicator_category` FOREIGN KEY (`category_id`) REFERENCES `tbl_target_categories` (`category_id`),
  CONSTRAINT `fk_indicator_term` FOREIGN KEY (`term_id`) REFERENCES `tbl_academic_terms` (`term_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tbl_system_access`
--

DROP TABLE IF EXISTS `tbl_system_access`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tbl_system_access` (
  `emp_id` varchar(50) NOT NULL,
  `system_role` varchar(50) NOT NULL,
  `account_status` varchar(50) DEFAULT 'Active',
  PRIMARY KEY (`emp_id`),
  CONSTRAINT `fk_access_emp` FOREIGN KEY (`emp_id`) REFERENCES `tbl_employee_profiles` (`emp_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tbl_target_categories`
--

DROP TABLE IF EXISTS `tbl_target_categories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tbl_target_categories` (
  `category_id` int(11) NOT NULL AUTO_INCREMENT,
  `category_name` varchar(100) NOT NULL,
  PRIMARY KEY (`category_id`),
  UNIQUE KEY `category_name` (`category_name`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-03-30 22:22:52
