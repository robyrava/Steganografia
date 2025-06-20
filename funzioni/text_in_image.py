import os
from PIL import Image

# --- FUNZIONI DI UTILITÀ ---

def clear_screen():
    """Pulisce la schermata del terminale."""
    os.system('cls' if os.name == 'nt' else 'clear')

# --- FUNZIONI DI CONVERSIONE E MANIPOLAZIONE DEI BIT ---

def binaryConvert(text: str) -> str:
    """Converte una stringa di testo in una stringa binaria (UTF-8)."""
    return ''.join(format(byte, '08b') for byte in text.encode('utf-8'))

def binaryConvertBack(binary_str: str) -> str:
    """Converte una stringa binaria in testo (UTF-8)."""
    byte_array = bytearray(int(binary_str[i:i+8], 2) for i in range(0, len(binary_str), 8))
    return byte_array.decode('utf-8', errors='ignore')

def setLastBit(value: int, bit: str) -> int:
    """Modifica l'ultimo bit (LSB) di un valore intero (0-255)."""
    return (value & 254) | int(bit)

# --- FUNZIONI PRINCIPALI DI STEGANOGRAFIA ---

def hideMessage(image_path: str, message: str, output_path: str) -> bool:
    """
    Nasconde una stringa di testo all'interno di un'immagine.
    """
    try:
        img = Image.open(image_path)
    except FileNotFoundError:
        print(f"\nERRORE: Immagine '{image_path}' non trovata.")
        return False
    except Exception as e:
        print(f"\nERRORE: Impossibile aprire l'immagine. Dettagli: {e}")
        return False

    # Aggiunge un "terminatore nullo" (8 bit a zero) per sapere dove finisce il messaggio
    binary_message = binaryConvert(message) + "00000000"
    
    # Controlla se l'immagine è abbastanza grande
    max_bits = img.width * img.height * 3
    if len(binary_message) > max_bits:
        print(f"\nERRORE: L'immagine è troppo piccola per contenere il messaggio.")
        print(f"Spazio richiesto: {len(binary_message)} bits. Spazio disponibile: {max_bits} bits.")
        return False

    if img.mode != "RGB":
        img = img.convert("RGB")

    img_copy = img.copy()
    pixels = img_copy.load()
    
    msg_bits = iter(binary_message)
    
    for y in range(img.height):
        for x in range(img.width):
            try:
                r, g, b = pixels[x, y]
                
                # Modifica il canale Rosso
                r = setLastBit(r, next(msg_bits))
                # Modifica il canale Verde
                g = setLastBit(g, next(msg_bits))
                # Modifica il canale Blu
                b = setLastBit(b, next(msg_bits))
                
                pixels[x, y] = (r, g, b)
            except StopIteration:
                # Tutti i bit sono stati nascosti
                img_copy.save(output_path)
                print(f"\nSUCCESSO: Messaggio nascosto e immagine salvata in '{output_path}'.")
                return True
    return False

def getMessage(image_path: str) -> str | None:
    """
    Recupera un messaggio di testo nascosto da un'immagine.
    """
    try:
        img = Image.open(image_path)
    except FileNotFoundError:
        print(f"\nERRORE: Immagine '{image_path}' non trovata.")
        return None
    except Exception as e:
        print(f"\nERRORE: Impossibile aprire l'immagine. Dettagli: {e}")
        return None
        
    if img.mode != "RGB":
        img = img.convert("RGB")
        
    pixels = img.load()
    extracted_bits = []
    
    for y in range(img.height):
        for x in range(img.width):
            r, g, b = pixels[x, y]
            
            extracted_bits.append(format(r, '08b')[-1])
            extracted_bits.append(format(g, '08b')[-1])
            extracted_bits.append(format(b, '08b')[-1])
            
            # Controlla ogni 8 bit se abbiamo trovato il terminatore nullo
            if len(extracted_bits) % 8 == 0:
                last_byte = "".join(extracted_bits[-8:])
                if last_byte == "00000000":
                    final_bits = "".join(extracted_bits[:-8])
                    return binaryConvertBack(final_bits)

    print("\nERRORE: Nessun messaggio (o terminatore di messaggio) trovato.")
    return None

# --- GESTIONE MENU E INPUT UTENTE ---

def get_image_path(prompt: str) -> str:
    """Chiede all'utente un percorso per un'immagine e controlla se esiste."""
    while True:
        path = input(prompt)
        if os.path.exists(path):
            return path
        else:
            print("ERRORE: File non trovato. Riprova.")

def handle_hide_text():
    """Gestisce il flusso per nascondere una stringa di testo."""
    clear_screen()
    print("--- Nascondi Stringa di Testo in Immagine ---")
    source_img = get_image_path("Percorso dell'immagine sorgente: ")
    message = input("Inserisci il messaggio da nascondere: ")
    if not message:
        print("ERRORE: il messaggio non può essere vuoto.")
        return
    
    # Costruisce il percorso di output nella stessa cartella dell'input
    dir_name = os.path.dirname(source_img)
    base_name = os.path.basename(source_img)
    file_name, _ = os.path.splitext(base_name)
    # Salva sempre come PNG per garantire la compressione senza perdita di dati
    output_img = os.path.join(dir_name, f"{file_name}_steg.png")
    
    print("\nInizio occultamento del messaggio...")
    hideMessage(source_img, message, output_img)

def handle_recover_text():
    """Gestisce il flusso per recuperare una stringa di testo."""
    clear_screen()
    print("--- Recupera Stringa di Testo da Immagine ---")
    source_img = get_image_path("Percorso dell'immagine con il messaggio nascosto: ")
    
    print("\nInizio ricerca del messaggio...")
    message = getMessage(source_img)
    
    if message:
        print(f"\nSUCCESSO: Messaggio recuperato:")
        print("-" * 30)
        print(message)
        print("-" * 30)
