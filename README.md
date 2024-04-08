
# BizCardX - Automating Business Card Data Extraction with EasyOCR

## Introduction:
In today's dynamic business landscape, efficient management and organization of contact information are essential for effective networking and communication. Traditional methods of manually inputting business card details into databases are time-consuming and prone to errors. To address these challenges, developers can harness the capabilities of optical character recognition (OCR) technology and databases to automate the extraction and storage of pertinent information from business cards.

EasyOCR stands out as a robust OCR library for extracting text from images. Leveraging deep learning models, EasyOCR offers accurate text recognition across multiple languages. By integrating EasyOCR with MySQL, developers can streamline the process of capturing business card data and storing it systematically for easy retrieval.

## ETL Process:
### a) Extract Data:
Utilize EasyOCR to extract relevant information from business cards.

### b) Process and Transform Data:
Process the extracted data, including Company Name, Card Holder, Designation, Mobile Number, Email, Website, Area, City, State, and Pincode, and convert it into a structured data frame.

### c) Load Data:
Store the transformed data into a MySQL database for efficient storage and retrieval.
