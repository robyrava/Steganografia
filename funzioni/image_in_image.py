import numpy as np
from PIL import Image
import os

METADATA_TERMINATOR = "0" * 16  # Usiamo un terminatore di 16 bit per sicurezza
METADATA_MAX_LEN_BITS = 4096 # Riserviamo i primi 512 byte (4096 bit) per i metadati

def setLastNBits(value: int, bits: str, n: int) -> int:
    """Setta gli ultimi n bits di un numero"""
    value = format(value, '08b')
    if len(bits) < n:
        bits = '0' * (n - len(bits)) + bits
    value = value[:-n] + bits
    value = int(value, 2)
    value = min(255, max(0, value))
    return value

def _hide_metadata(image_array, params):
    """Nasconde i metadati (dizionario di parametri) all'inizio dell'array di un'immagine."""
    metadata_string = f"{params['w']},{params['h']},{params['lsb']},{params['msb']},{params['div']}"
    binary_metadata = ''.join(format(ord(char), '08b') for char in metadata_string) + METADATA_TERMINATOR

    if len(binary_metadata) > METADATA_MAX_LEN_BITS:
        raise ValueError("I metadati sono troppo grandi per essere nascosti.")

    for i in range(len(binary_metadata)):
        image_array[i] = (image_array[i] & 254) | int(binary_metadata[i])
    
    return image_array

def _get_metadata(image_array):
    """Recupera i metadati dall'inizio dell'array di un'immagine."""
    extracted_bits = ""
    for i in range(METADATA_MAX_LEN_BITS):
        extracted_bits += str(image_array[i] & 1)
        if extracted_bits.endswith(METADATA_TERMINATOR):
            # Trovato il terminatore
            binary_string = extracted_bits[:-len(METADATA_TERMINATOR)]
            metadata_string = ''.join(chr(int(binary_string[i:i+8], 2)) for i in range(0, len(binary_string), 8))
            parts = metadata_string.split(',')
            return {
                "w": int(parts[0]),
                "h": int(parts[1]),
                "lsb": int(parts[2]),
                "msb": int(parts[3]),
                "div": float(parts[4])
            }
    raise ValueError("Terminatore dei metadati non trovato.")


def hideImage(img1: Image, img2: Image, new_img: str, lsb=4, msb=4):
    """Nasconde un'immagine in un'altra, includendo i metadati per il recupero."""
    if img1.mode != "RGB":
        img1 = img1.convert("RGB")
    if img2.mode != "RGB":
        img2 = img2.convert("RGB")

    if (lsb * img1.width * img1.height) < (msb * img2.width * img2.height) + METADATA_MAX_LEN_BITS:
        raise ValueError("L'immagine contenitore è troppo piccola.")

    arr1 = np.array(img1).flatten().copy()
    arr2 = np.array(img2).flatten().copy()

    work_array = arr1[METADATA_MAX_LEN_BITS:]
    
    div = (len(work_array) * lsb) / (len(arr2) * msb)

    i, j = 0, 0
    pos = 0.0
    bit_queue = ""
    
    while i < len(arr2):
        # Estrae msb bit da ogni canale di arr2
        r, g, b = arr2[i], arr2[i + 1], arr2[i + 2]
        bit_queue += format(r, '08b')[:msb]
        bit_queue += format(g, '08b')[:msb]
        bit_queue += format(b, '08b')[:msb]
        
        while len(bit_queue) >= lsb * 3:
            if round(pos) + 2 < len(work_array):
                # Estrae lsb*3 bit dalla coda
                bits_to_hide = bit_queue[:lsb*3]
                bit_queue = bit_queue[lsb*3:]

                j = round(pos)
                # Nasconde i bit in arr1
                r_bits, g_bits, b_bits = bits_to_hide[:lsb], bits_to_hide[lsb:2*lsb], bits_to_hide[2*lsb:3*lsb]
                
                work_array[j] = setLastNBits(work_array[j], r_bits, lsb)
                work_array[j + 1] = setLastNBits(work_array[j + 1], g_bits, lsb)
                work_array[j + 2] = setLastNBits(work_array[j + 2], b_bits, lsb)
                
                pos += div * 3
            else:
                # Se non c'è più spazio in arr1, interrompi
                bit_queue = ""
                break
        i += 3

    # Ora nascondiamo i metadati all'inizio dell'array originale
    params = {"w": img2.width, "h": img2.height, "lsb": lsb, "msb": msb, "div": div}
    arr1 = _hide_metadata(arr1, params)

    img1_copy = Image.fromarray(arr1.reshape(img1.height, img1.width, 3))
    img1_copy.save(new_img)


def getImage(img: Image, new_img: str) -> Image:
    """Ottieni un'immagine da un'altra, leggendo prima i metadati necessari."""
    if img.mode != "RGB":
        img = img.convert("RGB")
        
    arr = np.array(img).flatten().copy()
    
    # 1. Recupera i metadati
    params = _get_metadata(arr)
    width, height, lsb, msb, div = params['w'], params['h'], params['lsb'], params['msb'], params['div']

    # 2. Estrai l'immagine usando i metadati
    work_array = arr[METADATA_MAX_LEN_BITS:]
    size = width * height * 3
    res = np.zeros(size, dtype=np.uint8)
    
    bits = ""
    pos = 0.0
    n = 0

    while n < size:
        j = round(pos)
        if j + 2 >= len(work_array):
            break

        r_bits = format(work_array[j], '08b')[-lsb:]
        g_bits = format(work_array[j+1], '08b')[-lsb:]
        b_bits = format(work_array[j+2], '08b')[-lsb:]
        bits += r_bits + g_bits + b_bits
        
        while len(bits) >= msb:
            if n >= size:
                break
            
            byte_bits = bits[:msb]
            bits = bits[msb:]
            
            res[n] = int(byte_bits.ljust(8, '0'), 2)
            n += 1
            
        pos += div * 3

    res_img = Image.fromarray(res.reshape(height, width, 3))
    res_img.save(new_img)
    return res_img

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
    secret_img_path = get_image_path("Percorso dell'immagine da nascondere: ")
    
    try:
        lsb = int(input("Numero di bit meno significativi da usare (lsb, 1-8, default 4): ") or "4")
        msb = int(input("Numero di bit più significativi da usare (msb, 1-8, default 4): ") or "4")
        if not (1 <= lsb <= 8 and 1 <= msb <= 8):
            raise ValueError("LSB e MSB devono essere tra 1 e 8")
    except ValueError as e:
        print(f"Input non valido: {e}")
        return

    container_img = Image.open(container_img_path)
    secret_img = Image.open(secret_img_path)
    
    dir_name = os.path.dirname(container_img_path)
    base_name = os.path.basename(container_img_path)
    file_name, _ = os.path.splitext(base_name)
    output_img_path = os.path.join(dir_name, f"{file_name}_steg_img.png")
    
    print("\nInizio occultamento dell'immagine...")
    try:
        hideImage(container_img, secret_img, output_img_path, lsb, msb)
        print(f"\nSUCCESSO: Immagine nascosta e salvata in '{output_img_path}'.")
        print("I parametri di recupero sono stati inclusi nell'immagine.")
    except ValueError as e:
        print(f"\nERRORE: {e}")


def handle_recover_image():
    """Gestisce il flusso per recuperare un'immagine da un'altra in modo automatico."""
    print("--- Recupera Immagine da Immagine ---")
    source_img_path = get_image_path("Percorso dell'immagine con l'immagine nascosta: ")
    
    source_img = Image.open(source_img_path)
    
    dir_name = os.path.dirname(source_img_path)
    output_img_path = os.path.join(dir_name, f"recovered_image_auto.png")

    print("\nInizio recupero automatico dell'immagine...")
    try:
        getImage(source_img, output_img_path)
        print(f"\nSUCCESSO: Immagine recuperata e salvata in '{output_img_path}'.")
    except Exception as e:
        print(f"\nERRORE durante il recupero: {e}")
