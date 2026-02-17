## VELOXIS QUANT: SYSTEM DOCUMENTATION & EXECUTION GUIDE
### ℹ️ About the Project
This project is a part of the Infosys Springboard Virtual Internship 6.0.

The aim of the project is to analyze the volatility and risk levels of various cryptocurrencies using data analytics and machine learning techniques.

**Team Members:**
- Durga Prasad Bhogavilli -> [@git-dpDevOps](https://github.com/git-dpDevOps)
- BOMMISETTY V K L VYSHNAVI -> [@Bommisetty-Vyshnavi](https://github.com/Bommisetty-Vyshnavi)
- Kirti Joshi -> [@joshikirti1](https://github.com/joshikirti1)
- Arti Kushwaha -> [@arti8965](https://github.com/arti8965)
- Gorji Manasa -> [@Manasagorji](https://github.com/Manasagorji)
- Rithicka M -> [@Rithicka54](https://github.com/Rithicka54)
### 1.📋 PROJECT OVERVIEW
Veloxis Quant is an advanced quantitative risk management terminal designed to bridge the gap between fragmented market signals and institutional-grade investment intelligence. Developed as a centralized Asset Intelligence Hub, it translates complex, 24/7 market data into actionable risk scores using statistical learning and probabilistic simulations.

The platform has evolved from a fundamental Python script into a fully authenticated, secure web application with persistent database storage. It specifically addresses the needs of investors who face information overload and high volatility by providing professional-grade risk quantification tools.

### 2.🏗️ SYSTEM ARCHITECTURE & ALGORITHMS   
The platform is built on a modular four-layer architecture

  ***User Layer***  : Secure registration and authentication handling via Streamlit UI.
  
  ***Logic Layer*** : Core Risk Engine executing Monte Carlo simulations and volatility logic.
  
  ***Data Layer***  : Automated CSV ingestion and SQLite persistence for user history.
  
  ***Output Layer***: Interactive Plotly visualizations and automated PDF reporting. 
  
  #### 📊 Probabilistic Generative Algorithm: 
  Monte Carlo Simulation (MCS)To move beyond static historical data, the engine utilizes Geometric Brownian Motion (GBM) to     execute 1,000+ random-sampling iterations. This creates a "Probability Space" to identify:
  
   ***Worst Case (5th Percentile):*** Defines the statistical "Floor" risk.
   
   ***Median Case:*** The most likely statistical outcome based on current drift.
   
   ***Best Case (95th Percentile):*** The projected "Ceiling" potential.
  #### 📉 Statistical Learning: 
  Annualized VolatilityThe system calculates a 30-day rolling standard deviation of historical log returns. This baseline is    then annualized ($\sigma*\sqrt{365}$) to programmatically categorize assets into Stable, Moderate, or Critical risk states.


### 3.🚀 USER EXECUTION JOURNEY(Step-by-Step)
•	***Step 1: The Secure Gateway:*** A Zero-Trust landing page restricts access until the user initializes the system via the sidebar.

•	***Step 2: Authentication:*** Users register an Entity ID and Security Key, which are stored in SQLite using Bcrypt hashing for total data integrity.

•	***Step 3: Market Hub Analysis:*** Users run real-time scans on assets to generate volatility metrics and attach custom Strategic Notes to their findings.

•	***Step 4: Risk Divergence:*** A comparative benchmarking tool to view the volatility gap between "Safe Haven" and "High Growth" assets.

•	***Step 5: Probability Forecasting:*** Execution of the Monte Carlo engine and heuristic Pattern Intelligence Decoder to evaluate market uncertainty.

•	***Step 6: Data Persistence & Reporting:*** Users save records to the "Strategic Vault" and export a professional PDF Audit Report via the FPDF2 engine.

•	***Step 7: Institutional Oversight (Admin):*** Privileged login grants access to System Diagnostics and global history management.

### 4.🛠️ INSTALLATION GUIDE (README.md)

***Step 1: Environment Setup:*** python -m venv venv

***Step 2: Activation***

***Windows***:
 .\venv\Scripts\activate

***macOS/Linux***:
source venv/bin/activate

***Step 3: Install Dependencies:*** pip install -r requirements.txt

***Step 4: Launch Terminal***:streamlit run app.py

