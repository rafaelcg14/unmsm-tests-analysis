# Data Analysis of UNMSM Admission Tests (2024 - 2025)

This project is a **Streamlit-based dashboard** for analyzing admission exam data. It provides various insights such as applicant performance, trends over the years, and career-specific statistics through interactive visualizations.

![Dashboard](https://res.cloudinary.com/dtzfvm1m9/image/upload/v1733852224/portfolio/unmsm-analysis/yyo2luimdibqnnvdkgd3.png "Dashboard")

---

## Technologies Used

- **Python**: Core language for processing and analysis.
- **Streamlit**: Framework for creating interactive web applications.
- **Altair**: For creating visualizations.
- **Pandas**: Data manipulation and analysis.
- **BeautifulSoup**: For scraping data.

---

## Project Structure

```
unmsm-tests-analysis/
│
├── data/
│   ├── processed                   # Processed data (fullname removed for privacy)
│   │   ├── 2024-1
│   │   ├── 2024-2
│   │   └── 2025-1
│   └── raw                         # Raw data
│       ├── 2024-1
│       ├── 2024-2
│       └── 2025-1
│
├── src/
│   ├── utils
│   │   ├── generate_plots.py       # Generate plots for displaying in the dashboard
│   │   └── handle_data.py          # Loading, cleaning and transforming data, and generate analysis
│   └── webscraping
│       ├── processing_data.py      # Processing data
│       └── scraping_data.py        # Scraping data from unmsm admission test results pages
│
├── .gitignore
├── LICENSE.md
├── README.md
├── requirements.txt
├── styles.css                      # Apply styles to the streamlit webpage
└── main.py                         # Entry point for running the Streamlit app
```

---

## Setup and Installation

### Prerequisites
- Python 3.8 or higher
- Recommended: Virtual environment tools (`venv` or `conda`)

### Installation Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/rafaelcg14/unmsm-tests-analysis.git
   cd unmsm-tests-analysis
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   streamlit run main.py
   ```

4. Access the dashboard in your browser at `http://localhost:8501`.

---

## Usage

1. Select the **year** and **career** from the dropdown filters.
2. View key metrics and visualizations for the selected data.
3. Analyze trends over multiple years for specific careers.
4. Use the insights to identify patterns in applicant performance.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Contact

For questions or support, contact:
- **Name**: Rafael Castellanos
- **Email**: rafaelcg2718@gmail.com
- **LinkedIn**: [Rafael Castellanos](https://www.linkedin.com/in/rafael-castellanos-guzman/)