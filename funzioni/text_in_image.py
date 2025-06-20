import os
from PIL import Image
from utility import clear_screen

# --- FUNZIONI DI CONVERSIONE E MANIPOLAZIONE DEI BIT ---

def binaryConvert(text: str) -> str:
    """Converte una stringa di testo in una stringa binaria (UTF-8)."""
    return ''.join(format(byte, '08b') for byte in text.encode('utf-8'))

def binaryConvertBack(binary_str: str) -> str:
    """Converte una stringa binaria in testo (UTF-8)."""
    # Assicuriamoci che la lunghezza sia multipla di 8
    if len(binary_str) % 8 != 0:
        binary_str = binary_str[:-(len(binary_str) % 8)]
    
    try:
        byte_array = bytearray(int(binary_str[i:i+8], 2) for i in range(0, len(binary_str), 8))
        return byte_array.decode('utf-8', errors='ignore')
    except:
        return ""

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

    # Aggiunge un terminatore più robusto: 16 zeri consecutivi
    binary_message = binaryConvert(message) + "0000000000000000"
    
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
    
    bit_index = 0
    
    for y in range(img.height):
        for x in range(img.width):
            if bit_index >= len(binary_message):
                # Tutti i bit sono stati nascosti
                img_copy.save(output_path)
                print(f"\nSUCCESSO: Messaggio nascosto e immagine salvata in '{output_path}'.")
                return True
                
            r, g, b = pixels[x, y]
            
            # Modifica il canale Rosso
            if bit_index < len(binary_message):
                r = setLastBit(r, binary_message[bit_index])
                bit_index += 1
            
            # Modifica il canale Verde
            if bit_index < len(binary_message):
                g = setLastBit(g, binary_message[bit_index])
                bit_index += 1
            
            # Modifica il canale Blu
            if bit_index < len(binary_message):
                b = setLastBit(b, binary_message[bit_index])
                bit_index += 1
            
            pixels[x, y] = (r, g, b)
    
    img_copy.save(output_path)
    print(f"\nSUCCESSO: Messaggio nascosto e immagine salvata in '{output_path}'.")
    return True

def getMessage(image_path: str) -> str | None:
    """
    Recupera un messaggio di testo nascosto da un'immagine.
    Questa versione è più robusta: prima estrae tutti i bit, poi cerca il terminatore.
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
    
    # 1. Estrai tutti i bit LSB dall'immagine in un'unica stringa
    extracted_bits_list = []
    for y in range(img.height):
        for x in range(img.width):
            r, g, b = pixels[x, y]
            extracted_bits_list.append(format(r, '08b')[-1])
            extracted_bits_list.append(format(g, '08b')[-1])
            extracted_bits_list.append(format(b, '08b')[-1])
    
    all_bits = "".join(extracted_bits_list)
    
    # 2. Cerca il terminatore del messaggio
    terminator = "0000000000000000"
    terminator_pos = all_bits.find(terminator)
    
    if terminator_pos != -1:
        # 3. Trovato! Prendi tutti i bit *prima* del terminatore
        message_bits = all_bits[:terminator_pos]
        
        # 4. Converti i bit del messaggio in testo
        message = binaryConvertBack(message_bits)
        
        if message:
            return message
        else:
            print("\nERRORE: Dati trovati ma impossibili da decodificare in testo (potrebbe essere un file binario).")
            return None
    else:
        # 5. Se il terminatore non viene trovato, non c'è nessun messaggio nascosto.
        print("\nERRORE: Nessun messaggio (o terminatore di messaggio) trovato nell'immagine.")
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
        # Salva automaticamente il testo in un file
        save_extracted_text(source_img, message)


def save_extracted_text(image_path: str, message: str) -> bool:
    """
    Salva il testo estratto in un file .txt con nome basato sull'immagine sorgente.
    """
    try:
        # Costruisce il percorso del file di output
        dir_name = os.path.dirname(image_path)
        base_name = os.path.basename(image_path)
        file_name, _ = os.path.splitext(base_name)
        output_path = os.path.join(dir_name, f"{file_name}.txt")
        
        # Salva il messaggio nel file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(message)
        
        print(f"\nTesto salvato in: {output_path}")
        return True
        
    except Exception as e:
        print(f"\nERRORE nel salvare il file: {e}")
        return False
