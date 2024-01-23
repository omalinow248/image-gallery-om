import streamlit as st
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient
from azure.cosmos import CosmosClient, PartitionKey
import os
import datetime
import uuid

# Ładowanie zmiennych środowiskowych z pliku .env
load_dotenv()

# Funkcja do połączenia z bazą danych Cosmos DB
def connect_to_cosmos_db():
    cosmos_uri = os.getenv("COSMOS_URI")
    cosmos_key = os.getenv("COSMOS_KEY")
    client = CosmosClient(cosmos_uri, cosmos_key)
    database_name = os.getenv("COSMOS_DATABASE_NAME")
    database = client.get_database_client(database_name)
    container_name = os.getenv("COSMOS_CONTAINER_NAME")
    container = database.get_container_client(container_name)
    return container

# Funkcja do dodawania metadanych zdjęcia do bazy danych Cosmos DB
def add_photo_metadata_to_cosmos(photo_name, description):
    container = connect_to_cosmos_db()
    # Generowanie unikalnego identyfikatora UUID
    unique_id = str(uuid.uuid4())
    item = {
        'id': unique_id,  # Dodanie unikalnego ID
        'photo_name': photo_name,
        'description': description,
        'upload_date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    container.create_item(item)

# Funkcja do pobierania metadanych zdjęć z bazy danych Cosmos DB
def get_photo_metadata_from_cosmos():
    container = connect_to_cosmos_db()
    items = list(container.read_all_items())
    return items

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
        photo_metadata = get_photo_metadata_from_cosmos()
        for item in photo_metadata:
            if item['photo_name'] == blob.name:
                st.write("Opis:", item['description'])
                st.write("Data dodania:", item['upload_date'])
    return blobs_list

#Funkcja do dodawania nowego zdjęcia
def add_new_photo(blob_service_client, container_name):
    st.header("Dodaj nowe zdjęcie:")
    uploaded_file = st.file_uploader("Wybierz plik", type=["jpg", "jpeg", "png"])
    description = st.text_input("Dodaj opis zdjęcia:")
    if uploaded_file is not None:
        st.image(uploaded_file, caption="Załadowane zdjęcie", use_column_width=True)
        if st.button("Załaduj"):
            file_contents = uploaded_file.read()
            container_client = blob_service_client.get_container_client(container_name)
            blob_client = container_client.get_blob_client(uploaded_file.name)
            blob_client.upload_blob(file_contents, overwrite=True)
            add_photo_metadata_to_cosmos(uploaded_file.name, description)
            st.success("Zdjęcie zostało załadowane!")

# Funkcja do aktualizacji rekordu w bazie danych Cosmos DB po usunięciu zdjęcia
def update_photo_metadata_in_cosmos(photo_name):
    container = connect_to_cosmos_db()
    items = list(container.read_all_items())
    for item in items:
        if item['photo_name'] == photo_name:
            item['status'] = "deleted"  # Dodanie nowego pola "status" z wartością "deleted"
            container.upsert_item(item)

# Funkcja do usuwania zdjęć
def delete_file(container_name, blob_service_client):
    container_client = blob_service_client.get_container_client(container_name)
    blobs_list = container_client.list_blobs()

    selected_file = st.selectbox("Wybierz zdjęcie do usunięcia:",
                                 [blob.name for blob in blobs_list])
    if st.button("Usuń"):
        blob_client = container_client.get_blob_client(selected_file)
        blob_client.delete_blob()
        update_photo_metadata_in_cosmos(selected_file)  # Aktualizacja danych w Cosmos DB
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
