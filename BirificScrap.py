from selenium import webdriver
from selenium.webdriver.edge.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import datetime
from io import StringIO
import pandas as pd
from urllib.parse import urlparse, parse_qs
import json



# Setup WebDriver correctly using Service
# Ensure that the EdgeChromiumDriverManager is properly called with its executable_path

def generate_unique_filename(base_name):
    now = datetime.datetime.now()
    date_time_str = now.strftime('%Y%m%d_%H%M%S')
    unique_filename = f"{base_name}_{date_time_str}.csv"
    return unique_filename

with open('.\\config.json') as config_file:
    config = json.load(config_file)


options = webdriver.EdgeOptions()
options.add_argument("--enable-chrome-browser-cloud-management")
prefs = {
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "profile.default_content_settings.popups": 0,
    "safebrowsing.enabled": True
}
options.add_experimental_option("prefs", prefs)

service = Service(executable_path='.\\msedgedriver.exe')
driver = webdriver.Edge(service=service)


try:
    # Visit the ITU Space IFIC Databases page
    spaceCircularDB = config['spaceCircularDB']

    driver.get(spaceCircularDB)
    wait = WebDriverWait(driver, 10)

    # Wait for the table to be present
    table = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".table-p.table-striped")))

    # Find all 'View' links within the table
    view_links = driver.find_elements(By.XPATH, "//a[contains(@href,'radvance.asp')]")
    urls = [link.get_attribute('href') for link in view_links]

    # Print the view_links to verify they are captured correctly
    mydict = {}

    for url in urls:
        if url:
            
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)
            sel_ific_value = query_params.get('sel_ific', [None])[0]
            

            df_link = f'https://www.itu.int/net/ITU-R/space/snl/bresult/radvancedw_txt.asp?sel_ific={sel_ific_value}'
            driver.get(df_link)

            pre_element = driver.find_element(By.TAG_NAME, 'pre')
            csv_content = pre_element.text

            csv_data = StringIO(csv_content)
            df = pd.read_csv(csv_data)

            mydict[sel_ific_value] = df[df['ssn_ref'] == 'API/A']


    email = config['email']
    pswrd = config['password']
    band_freq = config['band_freq']
    uhf_freq = config['uhf_freq']
    output_file = config['output_file']

    brific_df = pd.DataFrame(columns=[
        'adm', 
        'band', 
        'Satellite name', 
        'Date of receipt', 
        'ssn_ref', 
        'WIC/IFIC', 
        'WIC/IFIC date'
    ])
        
    for key , df in mydict.items():
            for index , brif in df.iterrows():
                ntc_id = brif['ntc_id'] if pd.isna(brif['tgt_ntc_id']) else brif['tgt_ntc_id']
                freq_link = f'https://{email}:{pswrd}@www.itu.int/online/sns/freqlist.sh?ntc_id={ntc_id}'
                driver.get(freq_link)
                tables = wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "table")))
                target_table = tables[6]
                rows = target_table.find_elements(By.TAG_NAME, 'tr')

                lower_col = None
                upper_col = None 
                skip = False
                uhf =   False
                s_band = False


                for row in rows[4:-2]:
                    
                    if lower_col is None:
                        lower_col = row.find_elements(By.TAG_NAME,'td')
                    else :
                        upper_col = row.find_elements(By.TAG_NAME, 'td')
                        up_beam = upper_col[0].find_element(By.XPATH, ".//font[@size='-1']").text
                        lw_beam = lower_col[0].find_element(By.XPATH, ".//font[@size='-1']").text
                        up_cos = upper_col[0].find_element(By.XPATH, ".//font[@size='-1']").text
                        lw_cos = lower_col[0].find_element(By.XPATH, ".//font[@size='-1']").text

                        if up_beam == lw_beam and up_cos == lw_cos:

                            lower_frequency_element = lower_col[2].find_element(By.XPATH, ".//font[@size='-1']").text
                            lower_frequency = float(lower_frequency_element)

                            upper_frequency_element = upper_col[2].find_element(By.XPATH, ".//font[@size='-1']").text
                            upper_frequency = float(upper_frequency_element)

                        elif lower_col[4].find_element(By.XPATH, ".//font[@size='-1']").text != '':
                            
                            lower_frequency_element = lower_col[4].find_element(By.XPATH, ".//font[@size='-1']").text
                            lower_frequency = float(lower_frequency_element)

                            upper_frequency_element = lower_col[5].find_element(By.XPATH, ".//font[@size='-1']").text
                            upper_frequency = float(upper_frequency_element)
                        
                        else:
                             lower_col = upper_col
                             continue

                        lower_col = upper_col
                        
                        if any(lower <= upper_frequency and lower_frequency <= upper for lower, upper in uhf_freq):
                            uhf = True
                        
                        if any(lower <= upper_frequency and lower_frequency <= upper for lower, upper in band_freq):
                            s_band = True
                

                
                if uhf or s_band:
                    if uhf and s_band:
                        band_label = 'UHF / S-Band'
                            # print(band_label)
                    elif uhf:
                        band_label = 'UHF'
                                # print(band_label)
                    elif s_band:
                        band_label = 'S-Band'


                    row_data = {
                        'adm': brif['adm'],
                        'band': band_label,
                        'Satellite name': brif['sat_name'],
                        'Date of receipt': brif['d_rcv'],
                        'ssn_ref': brif['ssn_ref'],
                        'WIC/IFIC': brif['wic_no'],
                        'WIC/IFIC date': brif['d_wic']
                    }

                    row_data_df = pd.DataFrame([row_data])  
                    brific_df = pd.concat([brific_df, row_data_df], ignore_index=True)

                
    
    brific_df.to_csv(generate_unique_filename(output_file), index=False)
    print('CSV FILE GENERATED!!')

finally:
    driver.quit()
