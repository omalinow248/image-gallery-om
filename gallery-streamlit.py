import streamlit as st
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient
import os

# Ładowanie zmiennych środowiskowych z pliku .env
load_dotenv()

# Funkcja do łączenia z kontem Blob Storage
def connect_to_azure_storage():
    connection_string = os.getenv("AZURE_CONNECTION_STRING")
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    return blob_service_client

# Funkcja do pobierania listy plików z Blob Storage
def list_files(container_name, blob_service_client):
    container_client = blob_service_client.get_container_client(container_name)
    blobs_list = container_client.list_blobs()
    for blob in blobs_list:
        blob_client = container_client.get_blob_client(blob.name)
        blob_data = blob_client.download_blob().readall()
        st.image(blob_data, caption=blob.name)
    return blobs_list

#Funkcja do dodawania nowego zdjęcia
def add_new_photo(blob_service_client, container_name):
    st.header("Dodaj nowe zdjęcie:")
    uploaded_file = st.file_uploader("Wybierz plik", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        st.image(uploaded_file, caption="Załadowane zdjęcie", use_column_width=True)
        if st.button("Załaduj"):
            file_contents = uploaded_file.read()
            container_client = blob_service_client.get_container_client(container_name)
            blob_client = container_client.get_blob_client(uploaded_file.name)
            blob_client.upload_blob(file_contents, overwrite=True)
            st.success("Zdjęcie zostało załadowane!")

#Funkcja do usuwania zdjęć
def delete_file(container_name, blob_service_client):
    container_client = blob_service_client.get_container_client(container_name)
    blobs_list = container_client.list_blobs()

    selected_file = st.selectbox("Wybierz zdjęcie do usunięcia:",
                                 [blob.name for blob in blobs_list])
    if st.button("Usuń"):
        blob_client = container_client.get_blob_client(selected_file)
        blob_client.delete_blob()
        st.success(f"Zdjęcie {selected_file} zostało usunięte!")
        st.experimental_rerun()

# Funkcja do obsługi interfejsu aplikacji Streamlit
def main():
    blob_service_client = connect_to_azure_storage()
    container_name = os.getenv("CONTAINER_NAME") 
    st.title("Galeria Zdjęć z Blob Storage")
    add_new_photo(blob_service_client, container_name)
    st.header("Wszystkie zdjęcia:")
    list_files(container_name, blob_service_client)
    st.header("Usuń zdjęcie:")
    delete_file(container_name, blob_service_client)

if __name__ == "__main__":
    main()