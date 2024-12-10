from bs4 import BeautifulSoup
import requests, csv, os
from urllib.parse import urljoin

"""
urls = {
    "2024-1": "https://admision.unmsm.edu.pe/Website20241/A.html",
    "2024-2": "https://admision.unmsm.edu.pe/Website20242/A.html",
    "2025-1": "https://admision.unmsm.edu.pe/Website20251/A.html",
}
"""

def get_careers( url: str ):
    careers_list = []

    page = requests.get( url )
    page.encoding = 'utf-8' # Avoiding language decodifitacion errors

    soup = BeautifulSoup( page.text, 'html.parser' )
    table = soup.find_all( 'table' )
    tr_tags = table[0].find_all('tr')[1:]

    for row in tr_tags:
        single_row = row.find_all('td')
        row_value = [ data.text.strip() for data in single_row ]
        careers_list.append( *row_value )

    return careers_list

def get_career_data( url: str ):
    careers_href_list = []

    page = requests.get( url )
    page.encoding = 'utf-8' # Avoiding language decodifitacion errors

    # Remove file path from the url
    base_url = url.rsplit( '/', 1 )[0] + '/'

    soup = BeautifulSoup( page.text, 'html.parser' )
    table = soup.find_all('table')
    a_tags = table[0].find_all('a')[1:]

    for a in a_tags:
        href_attr = a.get('href')
        if href_attr:
            full_url = urljoin( base_url, href_attr.lstrip('./') )
            careers_href_list.append(full_url)

    return careers_href_list


def get_career_info(url):
    edition_raw = url.split("/")[3][-5:]
    edition = f"{edition_raw[:4]}-{edition_raw[-1]}"

    # Get the list of careers and their URLs
    careers_list = get_careers(url)
    careers_href_list = get_career_data(url)

    # Ensure the directory for the edition exists
    output_dir = f"./data/raw/{edition}"
    os.makedirs(output_dir, exist_ok=True)

    for career, career_url in zip(careers_list, careers_href_list):
        filepath = os.path.join(output_dir, f"{edition}-{career}.csv")

        # Create the CSV file and write the headers
        with open(filepath, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            headers = ["id", "nombre_completo", "carrera", "puntaje", "vacante", "observacion", "segunda_opcion"]
            writer.writerow(headers)

            # Fetch the data from the career URL
            try:
                response = requests.get(career_url, timeout=10)
                response.encoding = "utf-8"

                soup = BeautifulSoup(response.text, 'html.parser')
                table = soup.find_all('table')

                # Ensure the table exists
                if table:
                    tr_tags = table[0].find_all('tr')[1:]

                    for row in tr_tags:
                        # Extract the data from the table
                        single_row = row.find_all('td')
                        row_value = [data.text.strip() for data in single_row]
                        writer.writerow(row_value)
                else:
                    print(f"No table found for career: {career_url}")
            except requests.exceptions.RequestException as e:
                print(f"Error fetching data for {career}: {e}")
    

# get_career_info( "https://admision.unmsm.edu.pe/Website20241/A.html" )
# get_career_info( "https://admision.unmsm.edu.pe/Website20242/A.html" )
# get_career_info( "https://admision.unmsm.edu.pe/Website20251/A.html" )