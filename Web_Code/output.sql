-- MySQL dump 10.13  Distrib 5.7.31, for Win64 (x86_64)
--
-- Host: localhost    Database: project
-- ------------------------------------------------------
-- Server version	5.7.31-log

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `course`
--

DROP TABLE IF EXISTS `course`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `course` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `description` text NOT NULL,
  `image_url` varchar(255) NOT NULL,
  `teacher_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_teacher` (`teacher_id`),
  CONSTRAINT `fk_teacher` FOREIGN KEY (`teacher_id`) REFERENCES `teacher` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `course`
--

LOCK TABLES `course` WRITE;
/*!40000 ALTER TABLE `course` DISABLE KEYS */;
INSERT INTO `course` VALUES (1,'Principles of Secure Operating Systems','This course focuses on the security design and architecture of operating systems, aimed at teaching students how to identify and mitigate potential security threats. The curriculum covers the fundamental components of operating systems, such as process management, memory management, and file systems, along with their security implications. Students will learn about the latest security mechanisms and defense strategies, including access control, encryption techniques, and intrusion detection systems. Combining theoretical knowledge with practical application, the course is designed to cultivate students\' abilities to analyze and improve operating system security, preparing them for professional work in the field.','/static/images/PSOP.png',1),(2,'Advanced Object Oriented Programming','This course delves deeper into the concepts and techniques of object-oriented programming (OOP), building on foundational knowledge to explore advanced topics. Students will engage with complex programming scenarios, learning to design and implement scalable and maintainable software systems using OOP principles. Key areas of focus include inheritance, polymorphism, encapsulation, and design patterns such as Singleton, Observer, and Factory. The course also covers best practices for exception handling, testing, and refactoring. Through hands-on projects and case studies, students will develop the skills to architect robust software solutions that effectively utilize object-oriented techniques, preparing them for advanced software development roles.','/static/images/AOOP.png',1),(3,'1','This course focuses on the security design and architecture of operating systems, aimed at teaching students how to identify and mitigate potential security threats. The curriculum covers the fundamental components of operating systems, such as process management, memory management, and file systems, along with their security implications. Students will learn about the latest security mechanisms and defense strategies, including access control, encryption techniques, and intrusion detection systems. Combining theoretical knowledge with practical application, the course is designed to cultivate students\' abilities to analyze and improve operating system security, preparing them for professional work in the field.','/static/images/AOOP.png',2);
/*!40000 ALTER TABLE `course` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `course_comments`
--

DROP TABLE IF EXISTS `course_comments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `course_comments` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `course_id` int(11) NOT NULL,
  `student_id` int(11) NOT NULL,
  `comment` text NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `course_id` (`course_id`),
  KEY `student_id` (`student_id`),
  CONSTRAINT `course_comments_ibfk_1` FOREIGN KEY (`course_id`) REFERENCES `course` (`id`),
  CONSTRAINT `course_comments_ibfk_2` FOREIGN KEY (`student_id`) REFERENCES `student` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=31 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `course_comments`
--

LOCK TABLES `course_comments` WRITE;
/*!40000 ALTER TABLE `course_comments` DISABLE KEYS */;
INSERT INTO `course_comments` VALUES (28,1,1,'Teaching sucks, just read the PowerPoint, it\'s great, I get everything, great teaching. The teacher teaches great and every student feels great','2024-05-02 17:51:32'),(29,2,1,'The teacher never takes attendance during class','2024-05-03 04:28:25'),(30,1,2,'This course provides a solid foundation in the principles of secure operating systems and offers a mix of theoretical and practical knowledge. The curriculum covers a broad range of topics, which can sometimes feel overwhelming due to the dense material and rapid pace of the lectures. The instructor is knowledgeable, though at times the explanations could be clearer and more engaging. The lab sessions are useful, but they require a significant amount of time and effort to complete, which might be challenging for those new to the subject. The course materials are comprehensive, though updates could be beneficial to include the latest developments in the field. Overall, this course is quite informative, though it may be more suitable for students with some prior experience in computer security.','2024-05-03 06:53:01');
/*!40000 ALTER TABLE `course_comments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `course_registration`
--

DROP TABLE IF EXISTS `course_registration`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `course_registration` (
  `course_id` int(11) NOT NULL,
  `teacher_id` int(11) NOT NULL,
  `student_id` int(11) NOT NULL,
  PRIMARY KEY (`course_id`,`teacher_id`,`student_id`),
  KEY `teacher_id` (`teacher_id`),
  KEY `student_id` (`student_id`),
  CONSTRAINT `course_registration_ibfk_1` FOREIGN KEY (`course_id`) REFERENCES `course` (`id`),
  CONSTRAINT `course_registration_ibfk_2` FOREIGN KEY (`teacher_id`) REFERENCES `teacher` (`id`),
  CONSTRAINT `course_registration_ibfk_3` FOREIGN KEY (`student_id`) REFERENCES `student` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `course_registration`
--

LOCK TABLES `course_registration` WRITE;
/*!40000 ALTER TABLE `course_registration` DISABLE KEYS */;
INSERT INTO `course_registration` VALUES (1,1,1),(1,1,2),(2,1,1);
/*!40000 ALTER TABLE `course_registration` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `review_sentiment`
--

DROP TABLE IF EXISTS `review_sentiment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `review_sentiment` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `comment_id` int(11) NOT NULL,
  `negative_probability` float DEFAULT NULL,
  `neutral_probability` float DEFAULT NULL,
  `positive_probability` float DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `comment_id` (`comment_id`),
  CONSTRAINT `review_sentiment_ibfk_1` FOREIGN KEY (`comment_id`) REFERENCES `course_comments` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `review_sentiment`
--

LOCK TABLES `review_sentiment` WRITE;
/*!40000 ALTER TABLE `review_sentiment` DISABLE KEYS */;
INSERT INTO `review_sentiment` VALUES (6,28,0.0541471,0.0639973,0.881856),(7,29,0.85138,0.121195,0.0274252),(8,30,0.0257462,0.611634,0.36262);
/*!40000 ALTER TABLE `review_sentiment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `student`
--

DROP TABLE IF EXISTS `student`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `student` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `student`
--

LOCK TABLES `student` WRITE;
/*!40000 ALTER TABLE `student` DISABLE KEYS */;
INSERT INTO `student` VALUES (1,'1','1','Casper'),(2,'2','2','Bob'),(3,'3','3','Alice'),(4,'4','4','Harris'),(5,'5','5','kaco');
/*!40000 ALTER TABLE `student` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `teacher`
--

DROP TABLE IF EXISTS `teacher`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `teacher` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `teacher`
--

LOCK TABLES `teacher` WRITE;
/*!40000 ALTER TABLE `teacher` DISABLE KEYS */;
INSERT INTO `teacher` VALUES (1,'1','1','Li'),(2,'11','11','huo');
/*!40000 ALTER TABLE `teacher` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-05-06  0:04:40
