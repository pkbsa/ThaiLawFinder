-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Host: localhost
-- Generation Time: Apr 13, 2024 at 06:39 PM
-- Server version: 10.4.21-MariaDB
-- PHP Version: 7.4.29

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `netgluaydb`
--

-- --------------------------------------------------------

--
-- Table structure for table `law`
--
USE `netgluaydb`;

CREATE TABLE `law` (
  `id` int(11) NOT NULL,
  `name` varchar(999) NOT NULL,
  `copy` varchar(999) NOT NULL,
  `status` varchar(999) NOT NULL,
  `date` varchar(999) NOT NULL,
  `currentStatus` int(11) NOT NULL,
  `url` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `law`
--

INSERT INTO `law` (`id`, `name`, `copy`, `status`, `date`, `currentStatus`, `url`) VALUES
(1, 'ประมวลกฎหมายวิธีพิจารณาความแพ่ง', 'ฉบับปรับปรุงล่าสุด', 'ยังมีผลใช้บังคับ', '20 มิถุนายน 2478', 1, 'https://www.ocs.go.th/council-of-state/#/public/doc/MnArd1F2cHJTNXJ2aEl6dEw4cDhaUT09'),
(10, 'ประมวลกฎหมายแพ่งและพาณิชย์', 'ฉบับปรับปรุงล่าสุด', 'ยังมีผลใช้บังคับ', '11 พฤศจิกายน 2468', 1, 'https://www.ocs.go.th/council-of-state/#/public/doc/K2RWdWU3VW11STZ0S3ZybDVEQkdxdz09'),
(11, 'ประมวลกฎหมายอาญา', 'ฉบับปรับปรุงล่าสุด', 'ยังมีผลใช้บังคับ', '15 พฤศจิกายน 2499', 1, 'https://www.ocs.go.th/council-of-state/#/public/doc/Sm1GcGxuUnhXOFhIKzQxc0VBbzRiUT09'),
(12, 'ประมวลกฎหมายวิธีพิจารณาความอาญา', 'ฉบับปรับปรุงล่าสุด', 'ยังมีผลใช้บังคับ', '10 มิถุนายน 2478', 1, 'https://www.ocs.go.th/council-of-state/#/public/doc/UVdzUTNzUFZlT3VBOEw2allVWTZxZz09');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `law`
--
ALTER TABLE `law`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `name` (`name`) USING HASH;

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `law`
--
ALTER TABLE `law`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=33;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
