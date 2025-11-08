import pandas as pd 
import numpy as np 
from bs4 import BeautifulSoup
import requests

# This script accesses ClinVar's database to find all human genetic variant classifications that the FDA considers 
# to be supported by valid scientific evidence (See https://www.clinicalgenome.org/events-news/clingen-in-the-news/fda-recognizes-clingen-assertions-in-clinvar-twitter-chat/). 
# For those variants with classifications that were downgraded (clinical significance reclassified to a lower significance) 
# after FDA approval of the database, this script then accesses gnomAD's database to determine how many people 
# have been affected by these reclassifications.


################ CREATE DATAFRAME FOR SCRAPED DATA ##############

## column names for scraped data: A = most recent evaluation; B = second most recent evaluation; etc.
cols = pd.Series(['Variant', 'dbSNP_id', 'Classification', 'Stars_of_4', 'A_Clinical_Significance', 'A_Review_Status', 'A_Submitter_Study_Name', 'B_Clinical_Significance', 'B_Review_Status', 'B_Submitter_Study_Name', 'C_Clinical_Significance', 'C_Review_Status', 'C_Submitter_Study_Name'])
data = pd.DataFrame(columns = cols)



############ ACCESS NCBI SEARCH PAGE W/ ALL RELEVANT VARIANTS#############

page =  requests.get('https://www.ncbi.nlm.nih.gov/clinvar/?term=(ClinGen*%5BSubmitter%5D)+AND+%22revstat+expert+panel%22%5BProperties%5D+NOT+BRCA1+NOT+BRCA2+NOT+MSH2+NOT+PMS2+NOT+G6PD')
html = page.text
soup = BeautifulSoup(html, 'html.parser')
#print(soup.prettify())
variants = soup.find_all('a', {'class': 'blocklevelaintable'})


########### ACCESS EACH INDIVIDUAL VARIANT'S PAGE TO GET THEIR DATA#########

for link in variants[0:5]:
    hrefStr = link.get('href')
    fullLink = "https://www.ncbi.nlm.nih.gov" + hrefStr
    newPage = requests.get(fullLink)
    newHtml = newPage.text
    newSoup = BeautifulSoup(newHtml, 'html.parser')
    #print(newSoup.prettify())
    classification = newSoup.find('a', {'class': 'linkinpagenavtoclinassertab'}).text
    variantName = newSoup.find('h2', {'class': ''}).text
    stars = newSoup.find('span', {'class': 'rev_stat_text hide'}).text
    dataList = [variantName, 'dbSNP', classification, stars]
        ## access first table (Clinical Assertion Summary table)
    table = newSoup.find_all('table')[0]
        ## number of rows in table (counts header, so subtract 1)
    numRows = len(table.find_all('tr')) - 1
    tableDataList = []
        ## choosing to keep info for up to 3 variant submissions per variant
    for i in range(1,4):
        try:
            row = table.find_all('tr')[i]
            columns = row.find_all('td')
            tableDataList.append(columns[0].text) ## clinical significance
            tableDataList.append(columns[1].text) ## review status
            tableDataList.append(columns[6].text) ## submitter-study name
        except:
            tableDataList = tableDataList + [np.nan, np.nan, np.nan]
    dataList = dataList + tableDataList
    data.loc[len(data)] = dataList

print(data)
