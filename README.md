GlobalPartners Data Engineering \& Analytics Dashboard



Project Overview



This project demonstrates an end-to-end AWS data engineering and analytics solution using a Medallion Architecture (Bronze, Silver, and Gold).



The objective is to transform restaurant ordering data into analytics-ready datasets and business intelligence insights.



Technology Stack



AWS Glue — ETL pipelines and data transformation



Amazon S3 — Data lake storage



Amazon Athena — SQL analytics and querying



AWS Glue Data Catalog — Table metadata management



Python / PySpark — Data processing



SQL — Business analysis and reporting



Streamlit — Interactive analytics dashboard



GitHub — Source code and project documentation



Data Architecture



Bronze Layer — Raw Data



Ingest source data from SQL Server into the AWS data lake while preserving the original information.



Silver Layer — Cleaned Data



Clean, standardize, and transform Bronze-layer data into structured datasets suitable for analysis.



Gold Layer — Business Analytics



Prepare aggregated datasets and analytical views for reporting and dashboard visualization.



AWS Glue ETL Jobs



GlobalPartners\_SQLServer\_to\_Bronze



GlobalPartners\_Bronze\_to\_Silver



GlobalPartners\_Silver\_to\_Gold



GlobalPartners\_Daily\_Customer\_CLV



GlobalPartners\_RFM\_Customer\_Segmentation



Gold-Layer Analytics Views



Location Performance: Compare restaurant order volumes and rankings.



Restaurant Revenue Performance: Analyze restaurant revenue, order counts, and average order values.



Pricing Performance: Examine average item prices, revenue, and items sold.



Discount Effectiveness: Compare discounted and non-discounted orders.



Loyalty Impact: Analyze loyalty participation, customer value, and repeat purchase behavior.



Project Structure



GlobalPartners\_Dashboard/

├── app.py

├── app\_backup.py

├── test\_athena.py

├── etl/

├── sql/

│   ├── gold\_views/

│   └── analysis/

├── config/

├── docs/

├── screenshots/

├── .github/

│   └── workflows/

└── README.md



Business Value



The solution is designed to support:



Restaurant performance analysis



Revenue and pricing optimization



Customer loyalty analysis



Discount effectiveness measurement



Customer segmentation and lifetime value analysis



Project Status



AWS Glue ETL jobs and Amazon Athena Gold-layer analytical views have been created. Local SQL scripts have been organized for version control. Dashboard validation, deployment, and documentation are ongoing.
## GlobalPartners Medallion Architecture

The project uses a three-layer Medallion Architecture
(Bronze, Silver, and Gold) built with AWS services.

![GlobalPartners Medallion Architecture](GlobalPartners_Medallion_Architecture.png)

### Architecture Diagram

[View or download the editable diagrams.net diagram](GlobalPartners_Medallion_Architecture.drawio)

# GlobalPartners Project Video Presentation

This recorded presentation explains:

- The business problem and project objectives
- AWS Medallion Architecture (Bronze, Silver, Gold)
- AWS Glue ETL pipelines and PySpark transformations
- Amazon Athena and SQL analytics
- Streamlit dashboard and business insights
- GitHub Actions CI and project deliverables

### Watch the Project Presentation

[Watch the GlobalPartners Project Video](https://drive.google.com/file/d/1XXh3cQZjD3iB5D_9Nex3lQbzjFIJhXfk/view?usp=sharing)
