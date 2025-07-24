import numpy as np
from PIL import Image
import os

# Spazio massimo riservato in bit per l'header dei metadati (lunghezza + dati).
METADATA_HEADER_MAX_BITS = 8192 # 1 KB per sicurezza (nome file lungo)
# Bit usati per memorizzare la lunghezza dei metadati (2 byte = 16 bit).
METADATA_LEN_BITS = 16

def setLastNBits(value: int, bits: str) -> int:
    """Setta l'ultimo bit di un numero."""
    return (value & 254) | int(bits)

def _hide_file_metadata(image_array, filename, filesize):
    """
    Nasconde i metadati del file (nome, dimensione) usando un prefisso di lunghezza.
    Formato: [Lunghezza dei metadati (16 bit)] [Dati dei metadati (N*8 bit)]
    """
    metadata_string = f"{os.path.basename(filename)},{filesize}"
    metadata_bytes = metadata_string.encode('utf-8')

    if len(metadata_bytes) * 8 + METADATA_LEN_BITS > METADATA_HEADER_MAX_BITS:
        raise ValueError("I metadati (nome file troppo lungo?) sono troppo grandi per lo spazio riservato.")

    len_prefix_bin = format(len(metadata_bytes), f'0{METADATA_LEN_BITS}b')
    metadata_bin = ''.join(format(byte, '08b') for byte in metadata_bytes)
    full_header_bin = len_prefix_bin + metadata_bin

    for i in range(len(full_header_bin)):
        image_array[i] = setLastNBits(image_array[i], full_header_bin[i])
        
    return image_array

def _get_file_metadata(image_array):
    """Recupera i metadati del file (nome, dimensione)."""
    len_prefix_bin = "".join(str(image_array[i] & 1) for i in range(METADATA_LEN_BITS))
    metadata_len_bytes = int(len_prefix_bin, 2)

    if metadata_len_bytes == 0 or metadata_len_bytes * 8 + METADATA_LEN_BITS > METADATA_HEADER_MAX_BITS:
        raise ValueError("Lunghezza metadati non valida o corrotta. Forse non c'è un file nascosto.")

    start_index = METADATA_LEN_BITS
    end_index = start_index + (metadata_len_bytes * 8)
    
    metadata_bin = "".join(str(image_array[i] & 1) for i in range(start_index, end_index))
    metadata_bytes = int(metadata_bin, 2).to_bytes((len(metadata_bin) + 7) // 8, 'big')
    metadata_string = metadata_bytes.decode('utf-8')
    
    parts = metadata_string.split(',')
    if len(parts) != 2:
        raise ValueError("Formato metadati non corretto.")

    return {"filename": parts[0], "filesize": int(parts[1])}

def hideFile(container_img_path: str, secret_file_path: str, output_img_path: str):
    """Nasconde un file generico in un'immagine."""
    try:
        container_img = Image.open(container_img_path).convert("RGB")
        with open(secret_file_path, 'rb') as f:
            secret_data = f.read()
    except FileNotFoundError as e:
        raise ValueError(f"File non trovato: {e.filename}")

    filesize = len(secret_data)
    required_bits = filesize * 8 + METADATA_HEADER_MAX_BITS
    available_bits = container_img.width * container_img.height * 3 # Usando 1 LSB

    if available_bits < required_bits:
        available_kb = available_bits / 8 / 1024
        required_kb = required_bits / 8 / 1024
        file_kb = filesize / 1024
        raise ValueError(f"Immagine contenitore troppo piccola.\n"
                        f"Dimensione file: {filesize:,} byte ({file_kb:.2f} KB)\n"
                        f"Spazio richiesto: {required_kb:.2f} KB\n" 
                        f"Spazio disponibile: {available_kb:.2f} KB\n"
                        f"Mancano: {required_kb - available_kb:.2f} KB")

    arr = np.array(container_img).flatten().copy()
    
    # 1. Nascondi i metadati
    arr = _hide_file_metadata(arr, secret_file_path, filesize)

    # 2. Nascondi il file
    payload_offset = METADATA_HEADER_MAX_BITS
    secret_data_bin = ''.join(format(byte, '08b') for byte in secret_data)
    
    for i in range(len(secret_data_bin)):
        arr[payload_offset + i] = setLastNBits(arr[payload_offset + i], secret_data_bin[i])
        
    # 3. Salva l'immagine
    steg_img = Image.fromarray(arr.reshape(container_img.height, container_img.width, 3))
    steg_img.save(output_img_path)

def recoverFile(steg_img_path: str, output_dir: str):
    """Recupera un file nascosto da un'immagine."""
    try:
        steg_img = Image.open(steg_img_path).convert("RGB")
    except FileNotFoundError:
        raise ValueError(f"Immagine non trovata: {steg_img_path}")
        
    arr = np.array(steg_img).flatten()
    
    # 1. Recupera i metadati
    metadata = _get_file_metadata(arr)
    filename = metadata["filename"]
    filesize = metadata["filesize"]
    
    # 2. Estrai i bit del file
    payload_offset = METADATA_HEADER_MAX_BITS
    total_bits_to_read = filesize * 8
    
    if payload_offset + total_bits_to_read > len(arr):
        raise ValueError("I metadati indicano una dimensione del file maggiore dello spazio disponibile.")
    
    extracted_bits = "".join(str(arr[i] & 1) for i in range(payload_offset, payload_offset + total_bits_to_read))
    
    # 3. Converti i bit in byte e salva il file
    extracted_bytes = int(extracted_bits, 2).to_bytes(filesize, 'big')
    
    output_path = os.path.join(output_dir, f"recovered_{filename}")
    with open(output_path, 'wb') as f:
        f.write(extracted_bytes)
        
    return output_path

def calculate_file_capacity(container_img_path: str):
    """Calcola e mostra la capacità massima di file che l'immagine può contenere."""
    try:
        container_img = Image.open(container_img_path)
        if container_img.mode != "RGB":
            container_img = container_img.convert("RGB")
        
        # Calcola la capacità totale in bit (3 canali RGB × 1 bit LSB per canale)
        total_bits = container_img.width * container_img.height * 3
        
        # Sottrae lo spazio riservato per i metadati
        available_bits = total_bits - METADATA_HEADER_MAX_BITS
        available_bytes = available_bits // 8
        available_kb = available_bytes / 1024
        
        print(f"\n--- Capacità dell'immagine contenitore ({container_img.width}x{container_img.height} pixel) ---")
        print(f"Capacità totale: {total_bits:,} bit")
        print(f"Spazio riservato metadati: {METADATA_HEADER_MAX_BITS:,} bit ({METADATA_HEADER_MAX_BITS//8:,} byte)")
        print(f"Capacità disponibile per file: {available_bits:,} bit")
        print(f"Capacità disponibile: {available_bytes:,} byte ({available_kb:.2f} KB)")
        
        # Raccomandazione per evitare distorsioni
        safe_capacity_kb = available_kb * 0.1  # 10% per sicurezza
        print(f"\nRaccomandazione: Per evitare distorsioni visibili nell'immagine,")
        print(f"mantieni i file sotto i {safe_capacity_kb:.2f} KB.")
        
        return available_bytes
        
    except Exception as e:
        print(f"ERRORE nel calcolare la capacità: {e}")
        return 0

# --- Funzioni di gestione per l'interfaccia utente ---

def get_existing_file_path(prompt: str) -> str:
    """Chiede all'utente un percorso per un file e controlla se esiste."""
    while True:
        path = input(prompt)
        if os.path.exists(path) and os.path.isfile(path):
            return path
        else:
            print("ERRORE: File non trovato o non è un file valido. Riprova.")

def handle_hide_file():
    """Gestisce il flusso per nascondere un file."""
    print("--- Nascondi File in Immagine ---")
    try:
        container_path = get_existing_file_path("Percorso dell'immagine contenitore: ")
        
        # Mostra la capacità dell'immagine contenitore
        max_capacity_bytes = calculate_file_capacity(container_path)
        if max_capacity_bytes == 0:
            return
        
        secret_path = get_existing_file_path("\nPercorso del file da nascondere (qualsiasi tipo): ")
        
        # Verifica la dimensione del file da nascondere
        file_size = os.path.getsize(secret_path)
        file_size_kb = file_size / 1024
        
        if file_size > max_capacity_bytes:
            print(f"\nERRORE: Il file è troppo grande per essere nascosto!")
            print(f"Dimensione del file: {file_size:,} byte ({file_size_kb:.2f} KB)")
            print(f"Capacità massima: {max_capacity_bytes:,} byte ({max_capacity_bytes/1024:.2f} KB)")
            print(f"Eccesso: {file_size - max_capacity_bytes:,} byte ({(file_size - max_capacity_bytes)/1024:.2f} KB)")
            return
        
        # Mostra statistiche del file
        usage_percentage = (file_size / max_capacity_bytes) * 100
        print(f"\nStatistiche del file da nascondere:")
        print(f"Nome: {os.path.basename(secret_path)}")
        print(f"Dimensione: {file_size:,} byte ({file_size_kb:.2f} KB)")
        print(f"Utilizzo capacità: {usage_percentage:.1f}%")
        
        # Avviso per file grandi
        safe_limit = max_capacity_bytes * 0.1
        if file_size > safe_limit:
            print(f"\nATTENZIONE: Il file è relativamente grande ({usage_percentage:.1f}% della capacità).")
            print("    Potrebbero essere visibili lievi distorsioni nell'immagine risultante.")
            confirm = input("    Continuare comunque? (s/n): ").lower().strip()
            if confirm not in ['s', 'si', 'sì', 'y', 'yes']:
                print("Operazione annullata.")
                return
        
        dir_name = os.path.dirname(container_path)
        base_name, _ = os.path.splitext(os.path.basename(container_path))
        output_path = os.path.join(dir_name, f"{base_name}_steg_file.png")
        
        print("\nInizio occultamento del file...")
        hideFile(container_path, secret_path, output_path)
        print(f"\nSUCCESSO: File nascosto e salvato in '{output_path}'.")
        
    except (ValueError, Exception) as e:
        print(f"\nERRORE: {e}")

def handle_recover_file():
    """Gestisce il flusso per recuperare un file."""
    print("--- Recupera File da Immagine ---")
    try:
        steg_path = get_existing_file_path("Percorso dell'immagine con il file nascosto: ")
        output_dir = os.path.dirname(steg_path)
        
        print("\nInizio recupero del file...")
        recovered_file = recoverFile(steg_path, output_dir)
        print(f"\nSUCCESSO: File recuperato e salvato come '{recovered_file}'.")

    except (ValueError, Exception) as e:
        print(f"\nERRORE durante il recupero: {e}")

def handle_show_file_capacity():
    """Gestisce il flusso per mostrare solo la capacità di file di un'immagine."""
    print("--- Analisi Capacità File Immagine ---")
    try:
        container_path = get_existing_file_path("Percorso dell'immagine da analizzare: ")
        calculate_file_capacity(container_path)
    except Exception as e:
        print(f"ERRORE: {e}")