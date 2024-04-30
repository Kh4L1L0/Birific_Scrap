# BirificScrap Application

## Overview
BirificScrap is a specialized web scraping tool designed to extract frequency interval data from the BRIFIC (Space Circular) database hosted by ITU (International Telecommunication Union). The application targets specific frequency ranges that overlap with predetermined intervals and checks them against the S-band and UHF frequency ranges specified in the configuration.

## Purpose
The main objective of the AnrtScrap application is to automate the process of identifying satellite frequency allocations that intersect with critical frequency bands of interest. This tool is particularly useful for telecommunications researchers and professionals who need to monitor frequency allocations and ensure compliance with regulatory requirements or study frequency band usage.

## Requirements
- **Microsoft Edge Browser**: The application uses Selenium WebDriver with Edge, so having Microsoft Edge Version 124.0.2477.0 installed on your system is essential (you can change the MS Edge Driver in the file to suite Microsoft Edge browser Version).
- **Python Environment**: AnrtScrap is a Python-based application. Ensure that Python is installed on your system.

## Configuration
he application uses a `config.json` file to manage its settings and operational parameters. Below is the structure of the `config.json` file, which should be placed in the same directory as the executable:

```json
{
  "spaceCircularDB": "https://www.itu.int/sns/wic/demowic23.html",
  "email": "user@example.com",
  "password": "password123",
  "band_freq": [
    [2094.875, 2095.125],
    [2092.875, 2093.125],
    [2207.675, 2208.325],
    [2209.675, 2210.325]
  ],
  "uhf_freq": [
    [401.2375, 401.3125],
    [401.3875, 401.4625],
    [401.0625, 401.1375],
    [401.2125, 401.2875],
    [401.59, 401.61],
    [401.74, 401.76]
  ],
  "output_file": "output.csv"
}
```

### Important Configuration Notes :
- **spaceCircularDb** : URL to the ITU's Space Circular database.
- **email & password** : Credentials for accessing restricted parts of the ITU website.
- **band_freq & uhf_freq** : Lists of frequency ranges to check against the BRIFIC data.
- **output_file** : Name and path of the CSV file to store the results.

## Usage 

To run `BirificScrap`, navigate to the directory containing `BirificScrap.exe` and execute it. Make sure `msedgedriver.exe` and `config.json` are in the same directory as the executable:
```
./BirificScrap.exe
```

## Output
The application outputs the results in a CSV file specified in the configuration. The CSV file will include the following columns:

- **adm**: Administration or entity managing the satellite.
- **band**: Frequency band classification (S-band, UHF).
- **Satellite** name: The name of the satellite.
- **Date** of receipt: The date the satellite frequency data was recorded.
- **ssn_ref**: The reference number associated with the satellite.
- **WIC/IFIC**: International Frequency Information Circular (IFIC) number.
- **WIC/IFIC date**: The date associated with the IFIC entry.


