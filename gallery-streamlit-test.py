import streamlit as st

# Funkcja do dodawania nowego zdjęcia
def add_new_photo():
    st.header("Dodaj nowe zdjęcie:")
    uploaded_file = st.file_uploader("Wybierz plik", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        st.image(uploaded_file, caption="Załadowane zdjęcie", use_column_width=True)
        st.success("Zdjęcie zostało załadowane!")

# Funkcja do usuwania zdjęć
def delete_file():
    st.header("Usuń zdjęcie:")
    st.warning("Funkcja usuwania zdjęć nie jest obecnie dostępna.")

# Funkcja do obsługi interfejsu aplikacji Streamlit
def main():
    st.title("Galeria Zdjęć")
    add_new_photo()
    st.header("Wszystkie zdjęcia:")
    st.warning("Brak połączenia z Azure Blob Storage.")
    st.header("Usuń zdjęcie:")
    delete_file()

if __name__ == "__main__":
    main()
