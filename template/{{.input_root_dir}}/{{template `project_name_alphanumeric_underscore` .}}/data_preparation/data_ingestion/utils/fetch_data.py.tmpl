"""
This sample module contains data ingestion logic for ingesting data from a URL and parsing the HTML content. 
You should adapt the code based ont the HTML structure of your own data. The function returns a DataFrame with the parsed content.
"""


from pyspark.sql.types import StringType
from pyspark.sql.functions import col, udf, length, pandas_udf


from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import pandas as pd


retries = Retry(
    total=3,
    backoff_factor=3,
    status_forcelist=[429],
)


def fetch_data_from_url(spark, data_source_url, max_documents=None):
    # Fetch the XML content from sitemap
    response = requests.get(data_source_url)
    root = ET.fromstring(response.content)

    # Find all 'loc' elements (URLs) in the XML
    urls = [loc.text for loc in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
    if max_documents:
        urls = urls[:max_documents]

    # Create DataFrame from URLs
    df_urls = spark.createDataFrame(urls, StringType()).toDF("url").repartition(10)

    # Pandas UDF to fetch HTML content for a batch of URLs
    @pandas_udf("string")
    def fetch_html_udf(urls: pd.Series) -> pd.Series:
        adapter = HTTPAdapter(max_retries=retries)
        http = requests.Session()
        http.mount("http://", adapter)
        http.mount("https://", adapter)
        def fetch_html(url):
            try:
                response = http.get(url)
                if response.status_code == 200:
                    return response.content
            except requests.RequestException:
                return None
            return None

        with ThreadPoolExecutor(max_workers=200) as executor:
            results = list(executor.map(fetch_html, urls))
        return pd.Series(results)

    # Pandas UDF to process HTML content and extract text
    @pandas_udf("string")
    def download_web_page_udf(html_contents: pd.Series) -> pd.Series:
        def extract_text(html_content):
            if html_content:
                soup = BeautifulSoup(html_content, "html.parser")
                article_div = soup.find("div", class_="theme-doc-markdown markdown")
                if article_div:
                    return str(article_div).strip()
            return None

        return html_contents.apply(extract_text)

    # Apply UDFs to DataFrame
    df_with_html = df_urls.withColumn("html_content", fetch_html_udf("url"))
    final_df = df_with_html.withColumn("text", download_web_page_udf("html_content"))

    # Select and filter non-null results
    final_df = final_df.select("url", "text").filter("text IS NOT NULL")
    if final_df.isEmpty():
      raise Exception("""Dataframe is empty, couldn't download Databricks documentation. 
                      This is most likely caused by article_div = soup.find("div", class_="theme-doc-markdown markdown") in download_web_page_udf. 
                      Please check the html of the documentation page you are trying to download and chance the filter accordingly.
                      """)

    return final_df