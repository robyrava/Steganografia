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
        available_chars = (max_bits - 16) // 8  # Sottrae il terminatore
        message_chars = len(message)
        print(f"\nERRORE: L'immagine è troppo piccola per contenere il messaggio.")
        print(f"Spazio richiesto: {len(binary_message)} bit ({message_chars:,} caratteri)")
        print(f"Spazio disponibile: {max_bits} bit ({available_chars:,} caratteri max)")
        print(f"Ridurre il messaggio di {message_chars - available_chars:,} caratteri.")
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
    
    # Mostra la capacità dell'immagine
    max_chars = calculate_text_capacity(source_img)
    if max_chars == 0:
        return
    
    print(f"\nNota: Per evitare distorsioni visibili, mantieni il messaggio sotto i {max_chars//10:,} caratteri.")
    
    message = input("\nInserisci il messaggio da nascondere: ")
    if not message:
        print("ERRORE: il messaggio non può essere vuoto.")
        return
    
    # Verifica che il messaggio non sia troppo lungo
    message_length = len(message)
    if message_length > max_chars:
        print(f"\nERRORE: Il messaggio è troppo lungo!")
        print(f"Lunghezza del messaggio: {message_length:,} caratteri")
        print(f"Capacità massima: {max_chars:,} caratteri")
        print(f"Eccesso: {message_length - max_chars:,} caratteri")
        return
    
    # Mostra statistiche del messaggio
    usage_percentage = (message_length / max_chars) * 100
    print(f"\nStatistiche del messaggio:")
    print(f"Lunghezza: {message_length:,} caratteri")
    print(f"Utilizzo capacità: {usage_percentage:.1f}%")
    
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
        print(f"\n Messaggio recuperato con successo!")             
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

def calculate_text_capacity(image_path: str):
    """Calcola e mostra la capacità massima di caratteri che l'immagine può contenere."""
    try:
        img = Image.open(image_path)
        if img.mode != "RGB":
            img = img.convert("RGB")
        
        # Calcola la capacità totale in bit (3 canali RGB × 1 bit LSB per canale)
        total_bits = img.width * img.height * 3
        
        # Sottrae i bit per il terminatore (16 bit = "0000000000000000")
        terminator_bits = 16
        available_bits = total_bits - terminator_bits
        
        # Ogni carattere UTF-8 può occupare da 1 a 4 byte (8-32 bit)
        # Per essere sicuri, calcoliamo basandoci su caratteri a 1 byte (8 bit)
        max_chars_safe = available_bits // 8
        
        # Calcola anche la capacità teorica massima per caratteri ASCII (7 bit effettivi)
        max_chars_ascii = available_bits // 7
        
        print(f"\n--- Capacità dell'immagine contenitore ({img.width}x{img.height} pixel) ---")
        print(f"Capacità totale disponibile: {available_bits:,} bit ({available_bits/8:.1f} KB)")
        print(f"Caratteri massimi (UTF-8 sicuro): {max_chars_safe:,} caratteri")
        print(f"Caratteri massimi (solo ASCII): {max_chars_ascii:,} caratteri")
        print(f"Pagine di testo approssimative: ~{max_chars_safe//2000:.1f} pagine (2000 caratteri/pagina)")
        
        return max_chars_safe
        
    except Exception as e:
        print(f"ERRORE nel calcolare la capacità: {e}")
        return 0

def handle_show_text_capacity():
    """Gestisce il flusso per mostrare solo la capacità di testo di un'immagine."""
    clear_screen()
    print("--- Analisi Capacità Testo Immagine ---")
    source_img = get_image_path("Percorso dell'immagine da analizzare: ")
    calculate_text_capacity(source_img)
