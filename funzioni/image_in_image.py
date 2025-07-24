import numpy as np
from PIL import Image
import os

# Spazio massimo riservato in bit per l'header dei metadati (lunghezza + dati).
# 4096 bit = 512 byte.
METADATA_HEADER_MAX_BITS = 4096
# Bit usati per memorizzare la lunghezza dei metadati (2 byte = 16 bit).
METADATA_LEN_BITS = 16

def setLastNBits(value: int, bits: str, n: int) -> int:
    """Setta gli ultimi n bits di un numero."""
    value = format(value, '08b')
    if len(bits) < n:
        bits = '0' * (n - len(bits)) + bits
    value = value[:-n] + bits
    return int(value, 2)

def _binary_string_to_bytes(bin_str: str) -> bytes:
    """Converte una stringa di bit (es. '0100100001101001') in bytes."""
    return int(bin_str, 2).to_bytes((len(bin_str) + 7) // 8, 'big')

def _hide_metadata(image_array, params):
    """
    Nasconde i metadati usando un prefisso di lunghezza.
    Formato: [Lunghezza dei metadati (16 bit)] [Dati dei metadati (N*8 bit)]
    """
    metadata_string = f"{params['w']},{params['h']},{params['lsb']},{params['msb']},{params['div']}"
    metadata_bytes = metadata_string.encode('utf-8')
    
    # Controlla se i metadati sono troppo grandi
    if len(metadata_bytes) * 8 + METADATA_LEN_BITS > METADATA_HEADER_MAX_BITS:
        raise ValueError("I metadati sono troppo grandi per lo spazio riservato.")

    # Crea il prefisso di lunghezza (16 bit)
    len_prefix_bin = format(len(metadata_bytes), f'0{METADATA_LEN_BITS}b')
    
    # Crea il payload binario dei metadati
    metadata_bin = ''.join(format(byte, '08b') for byte in metadata_bytes)
    
    # Unisci prefisso e dati
    full_header_bin = len_prefix_bin + metadata_bin
    
    # Scrivi l'header bit per bit nel LSB dell'array dell'immagine
    for i in range(len(full_header_bin)):
        image_array[i] = (image_array[i] & 254) | int(full_header_bin[i])
        
    return image_array

def _get_metadata(image_array):
    """Recupera i metadati leggendo prima il prefisso di lunghezza."""
    # 1. Leggi il prefisso di lunghezza (i primi 16 bit)
    len_prefix_bin = "".join(str(image_array[i] & 1) for i in range(METADATA_LEN_BITS))
    metadata_len_bytes = int(len_prefix_bin, 2)
    
    # Controllo di sanità
    if metadata_len_bytes * 8 + METADATA_LEN_BITS > METADATA_HEADER_MAX_BITS:
        raise ValueError("Lunghezza dei metadati non valida o corrotta.")
        
    # 2. Leggi i dati dei metadati della lunghezza specificata
    start_index = METADATA_LEN_BITS
    end_index = start_index + (metadata_len_bytes * 8)
    
    metadata_bin = "".join(str(image_array[i] & 1) for i in range(start_index, end_index))
    
    # 3. Converti da binario a stringa e analizza
    metadata_bytes = _binary_string_to_bytes(metadata_bin)
    metadata_string = metadata_bytes.decode('utf-8')
    
    parts = metadata_string.split(',')
    if len(parts) < 5:
        raise ValueError("Metadati corrotti o incompleti.")

    return {
        "w": int(parts[0]),
        "h": int(parts[1]),
        "lsb": int(parts[2]),
        "msb": int(parts[3]),
        "div": float(parts[4])
    }

def hideImage(img1: Image, img2: Image, new_img: str, lsb=4, msb=4, custom_div=None):
    """Nasconde un'immagine in un'altra."""
    if img1.mode != "RGB": img1 = img1.convert("RGB")
    if img2.mode != "RGB": img2 = img2.convert("RGB")

    required_space_bits = (img2.width * img2.height * 3 * msb) + METADATA_HEADER_MAX_BITS
    available_space_bits = (img1.width * img1.height * 3 * lsb)
    if available_space_bits < required_space_bits:
        raise ValueError("L'immagine contenitore è troppo piccola per i parametri scelti.")

    arr1 = np.array(img1).flatten().copy()
    arr2 = np.array(img2).flatten().copy()

    payload_offset = METADATA_HEADER_MAX_BITS
    payload_space_len = len(arr1) - payload_offset
    
    # Usa il div personalizzato se fornito, altrimenti calcola automaticamente
    if custom_div is not None:
        div = custom_div
    else:
        div = (payload_space_len * lsb) / (len(arr2) * msb) if (len(arr2) * msb) > 0 else 0

    i = 0
    pos = 0.0
    bit_queue = ""
    
    while i < len(arr2):
        r, g, b = arr2[i], arr2[i + 1], arr2[i + 2]
        bit_queue += format(r, '08b')[:msb]
        bit_queue += format(g, '08b')[:msb]
        bit_queue += format(b, '08b')[:msb]
        
        while len(bit_queue) >= lsb * 3:
            j_abs = round(pos) + payload_offset
            if j_abs + 2 < len(arr1):
                bits_to_hide = bit_queue[:lsb*3]
                bit_queue = bit_queue[lsb*3:]
                r_bits, g_bits, b_bits = bits_to_hide[:lsb], bits_to_hide[lsb:2*lsb], bits_to_hide[2*lsb:3*lsb]
                arr1[j_abs] = setLastNBits(arr1[j_abs], r_bits, lsb)
                arr1[j_abs + 1] = setLastNBits(arr1[j_abs + 1], g_bits, lsb)
                arr1[j_abs + 2] = setLastNBits(arr1[j_abs + 2], b_bits, lsb)
                pos += div * 3
            else:
                bit_queue = ""
                break
        i += 3

    params = {"w": img2.width, "h": img2.height, "lsb": lsb, "msb": msb, "div": div}
    arr1 = _hide_metadata(arr1, params)

    Image.fromarray(arr1.reshape(img1.height, img1.width, 3)).save(new_img)

def getImage(img: Image, new_img: str) -> Image:
    """Recupera un'immagine da un'altra."""
    if img.mode != "RGB": img = img.convert("RGB")
    arr = np.array(img).flatten().copy()
    
    params = _get_metadata(arr)
    width, height, lsb, msb, div = params['w'], params['h'], params['lsb'], params['msb'], params['div']

    payload_offset = METADATA_HEADER_MAX_BITS
    work_array = arr[payload_offset:]
    size = width * height * 3
    res = np.zeros(size, dtype=np.uint8)
    
    bits = ""
    pos = 0.0
    n = 0

    while n < size:
        j = round(pos)
        if j + 2 >= len(work_array): break
        r_bits = format(work_array[j], '08b')[-lsb:]
        g_bits = format(work_array[j+1], '08b')[-lsb:]
        b_bits = format(work_array[j+2], '08b')[-lsb:]
        bits += r_bits + g_bits + b_bits
        
        while len(bits) >= msb:
            if n >= size: break
            byte_bits = bits[:msb]
            bits = bits[msb:]
            res[n] = int(byte_bits.ljust(8, '0'), 2)
            n += 1
        pos += div * 3

    res_img = Image.fromarray(res.reshape(height, width, 3))
    res_img.save(new_img)
    return res_img

def find_optimal_params(container_img: Image, secret_img: Image):
    """Calcola i parametri lsb e msb ottimali."""
    container_pixels = container_img.width * container_img.height
    secret_pixels = secret_img.width * secret_img.height
    
    for lsb in range(1, 9):
        for msb in range(8, 0, -1):
            available_space = (container_pixels * 3 * lsb)
            required_space = (secret_pixels * 3 * msb) + METADATA_HEADER_MAX_BITS
            if available_space >= required_space:
                return lsb, msb
    return None, None

def calculate_optimal_div(container_img: Image, secret_img: Image, lsb: int, msb: int):
    """Calcola il valore di div ottimale per i parametri dati."""
    arr1_len = container_img.width * container_img.height * 3
    arr2_len = secret_img.width * secret_img.height * 3
    
    payload_offset = METADATA_HEADER_MAX_BITS
    payload_space_len = arr1_len - payload_offset
    
    optimal_div = (payload_space_len * lsb) / (arr2_len * msb) if (arr2_len * msb) > 0 else 0
    return optimal_div

def get_image_path(prompt: str) -> str:
    """Chiede all'utente un percorso per un'immagine e controlla se esiste."""
    while True:
        path = input(prompt)
        if os.path.exists(path):
            return path
        else:
            print("ERRORE: File non trovato. Riprova.")

def handle_hide_image():
    """Gestisce il flusso per nascondere un'immagine in un'altra."""
    print("--- Nascondi Immagine in Immagine ---")
    container_img_path = get_image_path("Percorso dell'immagine contenitore: ")
    
    container_img = Image.open(container_img_path)
    
    # Mostra la capacità dell'immagine contenitore
    show_container_capacity(container_img)
    
    secret_img_path = get_image_path("\nPercorso dell'immagine da nascondere: ")
    secret_img = Image.open(secret_img_path)
    lsb, msb = None, None

    print("\nScegli la modalità di occultamento:")
    print("1) Automatica (consigliato)")
    print("2) Manuale (per utenti esperti)")
    mode = input("Scelta: ").strip()

    if mode == '1':
        print("\nCalcolo dei parametri ottimali in corso...")
        lsb, msb = find_optimal_params(container_img, secret_img)
        if lsb is None:
            print("\nERRORE: L'immagine contenitore è troppo piccola.")
            return
        
        # Calcola il div ottimale
        optimal_div = calculate_optimal_div(container_img, secret_img, lsb, msb)
        print(f"Parametri ottimali calcolati: lsb={lsb}, msb={msb}")
        print(f"Valore div ottimale: {optimal_div:.6f}")
        
        custom_div = None  # Usa il valore calcolato automaticamente
    elif mode == '2':
        try:
            lsb = int(input("Numero di bit LSB da usare (1-8): ") or "4")
            msb = int(input("Numero di bit MSB da usare (1-8): ") or "4")
            if not (1 <= lsb <= 8 and 1 <= msb <= 8):
                raise ValueError("LSB e MSB devono essere tra 1 e 8")
                
            # Calcola il div ottimale per i parametri scelti
            optimal_div = calculate_optimal_div(container_img, secret_img, lsb, msb)
            print(f"\nValore div ottimale per LSB={lsb}, MSB={msb}: {optimal_div:.6f}")
            
            custom_div = None
            modify_div = input("Vuoi modificare il valore div? (s/n): ").lower().strip()
            if modify_div in ['s', 'si', 'sì', 'y', 'yes']:
                try:
                    min_div = optimal_div * 0.1
                    max_div = optimal_div * 2.0
                    print(f"Inserisci un valore tra {min_div:.6f} e {max_div:.6f}")
                    custom_div = float(input(f"Valore div (premere Invio per {optimal_div:.6f}): ") or optimal_div)
                    if not (min_div <= custom_div <= max_div):
                        print(f"ATTENZIONE: Valore fuori dal range raccomandato.")
                        confirm = input("Continuare comunque? (s/n): ").lower().strip()
                        if confirm not in ['s', 'si', 'sì', 'y', 'yes']:
                            custom_div = optimal_div
                except ValueError:
                    print("Valore non valido. Usando il valore ottimale.")
                    custom_div = optimal_div
                    
        except ValueError as e:
            print(f"Input non valido: {e}")
            return
    else:
        print("Scelta non valida.")
        return

    output_path = os.path.join(os.path.dirname(container_img_path), f"{os.path.splitext(os.path.basename(container_img_path))[0]}_steg_img.png")
    
    print("\nInizio occultamento dell'immagine...")
    try:
        hideImage(container_img, secret_img, output_path, lsb, msb, custom_div)
        print(f"\nSUCCESSO: Immagine nascosta e salvata in '{output_path}'.")
    except ValueError as e:
        print(f"\nERRORE: {e}")

def handle_recover_image():
    """Gestisce il flusso per recuperare un'immagine da un'altra."""
    print("--- Recupera Immagine da Immagine ---")
    source_img_path = get_image_path("Percorso dell'immagine con i dati nascosti: ")
    source_img = Image.open(source_img_path)
    output_path = os.path.join(os.path.dirname(source_img_path), f"recovered_image.png")

    print("\nInizio recupero automatico dell'immagine...")
    try:
        getImage(source_img, output_path)
        print(f"\nSUCCESSO: Immagine recuperata e salvata in '{output_path}'.")
    except Exception as e:
        print(f"\nERRORE durante il recupero: {e}")

def show_container_capacity(container_img: Image):
    """Mostra la capacità dell'immagine contenitore per ogni valore di LSB possibile."""
    container_pixels = container_img.width * container_img.height
    
    print(f"\n--- Capacità dell'immagine contenitore ({container_img.width}x{container_img.height} pixel) ---")
    print("LSB | Capacità disponibile | Dimensione max immagine nascosta")
    print("----|---------------------|--------------------------------")
    
    for lsb in range(1, 9):
        # Capacità totale in bit (3 canali RGB)
        total_capacity_bits = container_pixels * 3 * lsb
        
        # Capacità disponibile sottraendo lo spazio per i metadati
        available_capacity_bits = total_capacity_bits - METADATA_HEADER_MAX_BITS
        
        # Capacità in KB (1 KB = 1024 byte)
        available_capacity_kb = (available_capacity_bits // 8) / 1024
        
        # Dimensione massima dell'immagine nascosta (assumendo MSB=8 per il caso peggiore)
        # Ogni pixel dell'immagine nascosta richiede 3*8=24 bit
        max_hidden_pixels = available_capacity_bits // 24
        max_hidden_width = int(max_hidden_pixels ** 0.5)  # Approssimazione quadrata
        
        print(f" {lsb}  | {available_capacity_kb:>18.1f} KB | {max_hidden_width}x{max_hidden_width} pixel (~{max_hidden_pixels:,} pixel)")
    
    print("\nNota: Le dimensioni mostrate sono approssimative e assumono MSB=8 (caso peggiore).")
    print("Con valori di MSB più bassi, è possibile nascondere immagini più grandi.")

def handle_show_capacity():
    """Gestisce il flusso per mostrare solo la capacità di un'immagine contenitore."""
    print("--- Analisi Capacità Immagine Contenitore ---")
    container_img_path = get_image_path("Percorso dell'immagine da analizzare: ")
    container_img = Image.open(container_img_path)
    show_container_capacity(container_img)