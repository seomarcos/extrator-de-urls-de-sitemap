
# Developed and distributed by UpSEO Academy
import logging
import threading
import time
import xml.etree.ElementTree as ET
import requests
from io import BytesIO
import easygui
from retrying import retry

# Configuração do logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def extract_urls_from_sitemap(url):
    logging.info(f"Processando o sitemap: {url}")

    @retry(stop_max_attempt_number=3, wait_fixed=2000)
    def get_sitemap_content():
        response = requests.get(url)
        response.raise_for_status()
        return response.content

    try:
        content = get_sitemap_content()

        tree = ET.parse(BytesIO(content))
        root = tree.getroot()

        namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        urls = [url.text for url in root.findall('ns:url/ns:loc', namespace)]

        logging.info(f"Extraídas {len(urls)} URLs do sitemap: {url}")
        return urls

    except Exception as e:
        logging.error(f"Erro ao processar {url}: {str(e)}")
        return []

def process_sitemaps(sitemap_files, output_file_name):
    extracted_urls = []

    def process_and_store(url):
        urls = extract_urls_from_sitemap(url)
        extracted_urls.extend(urls)
        time.sleep(1)  # Pausa para evitar sobrecarga

    threads = []
    for url in sitemap_files:
        thread = threading.Thread(target=process_and_store, args=(url,))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    with open(output_file_name, 'w') as file:
        for url in extracted_urls:
            file.write(url + '')

    logging.info(f"Finalizado a extração de todas as URLs dos sitemaps. As URLs foram salvas em {output_file_name}")

def main():
    logging.info("Iniciando o Extrator de URLs de Sitemaps")

    sitemap_files_name = easygui.fileopenbox("Selecione o arquivo com os nomes dos sitemaps")
    output_file_name = easygui.enterbox("Digite o nome do arquivo .txt para salvar as URLs extraídas")

    with open(sitemap_files_name, 'r') as file:
        sitemap_files = [line.strip() for line in file]

    process_sitemaps(sitemap_files, output_file_name)

if __name__ == "__main__":
    main()
