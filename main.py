# Script per la steganografia testuale con menu interattivo.
# Permette di nascondere e recuperare stringhe di testo da immagini.
from funzioni.text_in_image import handle_hide_text, handle_recover_text, clear_screen
from funzioni.image_in_image import handle_hide_image, handle_recover_image

# --- GESTIONE MENU E INPUT UTENTE ---

def sub_menu(action: str):
    """Mostra il sottomenu per la scelta del tipo di dato."""
    while True:
        clear_screen()
        print(f"--- Cosa vuoi {action}? ---")
        print("1) Stringa di testo")
        print("2) Immagine")
        print("3) Torna indietro")
        choice = input("Scegli un'opzione: ")

        if choice == '1':
            return 1
        elif choice == '2':
            return 2
        elif choice == '3':
            return None # Per tornare indietro
        else:
            print("Scelta non valida. Riprova.")
            input("Premi Invio per continuare...")

def main_menu():
    """Menu Principale"""
    while True:
        clear_screen()
        print("--- Steganografia su Immagini ---")
        print("Scegli un'operazione:")
        print("1) Nascondi dati")
        print("2) Recupera dati")
        print("3) Esci")
        main_choice = input("La tua scelta: ")

        if main_choice == '1':
            sub_choice = sub_menu("Nascondere")
            if sub_choice == 1:
                handle_hide_text()
            elif sub_choice == 2:
                handle_hide_image()
        elif main_choice == '2':
            sub_choice = sub_menu("Recuperare")
            if sub_choice == 1:
                handle_recover_text()
            elif sub_choice == 2:
                handle_recover_image()
        elif main_choice == '3':
            print("Arrivederci!")
            break
        else:
            print("Scelta non valida. Riprova.")

        # Pausa prima di tornare al menu principale
        if main_choice in ['1', '2']:
            input("\nPremi Invio per tornare al menu principale...")

if __name__ == "__main__":
    main_menu()
