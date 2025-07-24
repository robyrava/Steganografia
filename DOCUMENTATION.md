# Documentazione Tecnica - Steganografia su Immagini

## 📋 Panoramica dei File

### 1. `main.py` - File Principale e Menu Interattivo

**Scopo**: Entry point dell'applicazione con interfaccia utente a menu.

**Componenti principali**:
- `main_menu()`: Menu principale con le opzioni principali (Nascondi/Recupera/Esci)
- `sub_menu(action)`: Sottomenu per scegliere il tipo di contenuto (Testo/Immagine/File)

**Funzionalità**:
- ✅ Navigazione intuitiva tra le diverse modalità di steganografia
- ✅ Gestione del flusso dell'applicazione
- ✅ Importazione e orchestrazione di tutti i moduli specifici
- ✅ Schermata pulita con clear_screen() tra le operazioni

**Struttura del flusso**:
```
Menu Principale → Sottomenu Tipo → Funzione Specifica → Ritorno al Menu
```

---

### 2. `utility.py` - Funzioni di Utilità Generali

**Scopo**: Raccolta di funzioni helper utilizzate da tutti i moduli.

**Funzioni**:
- `clear_screen()`: Pulisce il terminale (compatibile Windows/Unix)

**Caratteristiche**:
- ✅ Cross-platform (Windows: `cls`, Unix: `clear`)
- ✅ Funzioni riutilizzabili
- ✅ Separazione delle responsabilità

---

### 3. `funzioni/text_in_image.py` - Steganografia Testuale

**Scopo**: Nasconde e recupera stringhe di testo nelle immagini usando LSB.

#### 🔧 Funzioni Core

**`binaryConvert(text: str) → str`**
- Converte testo UTF-8 in stringa binaria
- Gestisce caratteri internazionali e simboli speciali

**`binaryConvertBack(binary_str: str) → str`**
- Converte stringa binaria in testo UTF-8
- Gestione robusta degli errori di decodifica

**`setLastBit(value: int, bit: str) → int`**
- Modifica il LSB di un valore (0-255)
- Operazione fondamentale della steganografia LSB

#### 🎯 Funzioni Principali

**`hideMessage(image_path, message, output_path) → bool`**
- Nasconde un messaggio di testo in un'immagine
- **Terminatore robusto**: 16 bit consecutivi di zeri
- **Controlli di capacità**: Verifica spazio disponibile
- **Conversione RGB**: Automatica se necessario

**`getMessage(image_path) → str|None`**
- Recupera un messaggio nascosto
- **Estrazione completa**: Prima estrae tutti i LSB, poi cerca il terminatore
- **Gestione errori**: Ritorna None se non trova messaggi

#### 📊 Funzioni di Analisi

**`calculate_text_capacity(image_path) → int`**
- Calcola capacità massima in caratteri
- **Doppio calcolo**: UTF-8 sicuro (8 bit) e ASCII (7 bit)
- **Visualizzazione**: Bit, KB, caratteri, pagine di testo
- **Raccomandazioni**: Soglia del 10% per evitare distorsioni

#### 🎮 Funzioni UI

**`handle_hide_text()`**
- Flusso completo per nascondere testo
- **Analisi preventiva**: Mostra capacità prima dell'input
- **Validazione**: Controlla lunghezza del messaggio
- **Statistiche**: Mostra utilizzo della capacità

**`handle_recover_text()`**
- Flusso completo per recuperare testo
- **Salvataggio automatico**: Crea file .txt con il testo estratto

---

### 4. `funzioni/image_in_image.py` - Steganografia di Immagini

**Scopo**: Nasconde un'immagine dentro un'altra con parametri LSB/MSB configurabili.

#### ⚙️ Parametri e Costanti

- `METADATA_HEADER_MAX_BITS = 4096`: Spazio riservato per metadati (512 byte)
- `METADATA_LEN_BITS = 16`: Bit per memorizzare lunghezza metadati

#### 🔧 Funzioni di Manipolazione Bit

**`setLastNBits(value, bits, n) → int`**
- Modifica gli ultimi N bit di un valore
- Più flessibile del setLastBit per múltipli bit

**`_binary_string_to_bytes(bin_str) → bytes`**
- Conversione efficiente da stringa binaria a bytes

#### 💾 Gestione Metadati

**`_hide_metadata(image_array, params)`**
- Nasconde parametri dell'immagine (dimensioni, LSB, MSB, divisore)
- **Formato**: [Lunghezza(16bit)][Dati metadati]
- **Controlli**: Verifica che i metadati non superino lo spazio riservato

**`_get_metadata(image_array) → dict`**
- Recupera metadati dall'immagine
- **Validazione**: Controlli di integrità sui dati letti
- **Parsing**: Estrae larghezza, altezza, LSB, MSB, divisore

#### 🎯 Funzioni Principali

**`hideImage(img1, img2, new_img, lsb=4, msb=4)`**
- Nasconde img2 dentro img1
- **Algoritmo adattivo**: Calcola divisore per distribuzione ottimale
- **Coda di bit**: Gestisce bit parziali per efficienza
- **Controlli spazio**: Verifica compatibilità parametri/dimensioni

**`getImage(img, new_img) → Image`**
- Recupera immagine nascosta
- **Lettura metadati**: Acquisisce parametri di occultamento
- **Ricostruzione**: Usa divisore per leggere bit nella posizione corretta

#### 📊 Funzioni di Analisi

**`show_container_capacity(container_img)`**
- **Tabella comparativa**: Capacità per ogni valore LSB (1-8)
- **Metriche multiple**: Bit totali, KB disponibili, dimensioni immagine nascosta
- **Approssimazioni**: Calcoli basati su MSB=8 (caso peggiore)

**`find_optimal_params(container_img, secret_img) → (lsb, msb)`**
- Calcola automaticamente i parametri ottimali
- **Algoritmo**: Cerca LSB minimo con MSB massimo compatibili
- **Efficienza**: Priorità alla qualità dell'immagine contenitore

#### 🎮 Funzioni UI

**`handle_hide_image()`**
- **Modalità automatica**: Calcolo parametri ottimali
- **Modalità manuale**: Input LSB/MSB personalizzati
- **Analisi capacità**: Mostra tabella prima della selezione

---

### 5. `funzioni/file_in_image.py` - Steganografia di File Generici

**Scopo**: Nasconde qualsiasi tipo di file (documenti, audio, video, archivi) nelle immagini.

#### ⚙️ Configurazione

- `METADATA_HEADER_MAX_BITS = 8192`: Spazio maggiore per nomi file lunghi (1 KB)
- `METADATA_LEN_BITS = 16`: Bit per lunghezza metadati

#### 🔧 Funzioni di Manipolazione

**`setLastNBits(value, bits) → int`**
- Versione semplificata per modificare 1 bit (LSB)

#### 💾 Gestione Metadati File

**`_hide_file_metadata(image_array, filename, filesize)`**
- Nasconde nome file e dimensione
- **Formato**: "nome_file.ext,dimensione_byte"
- **Sicurezza**: Controllo lunghezza nome file

**`_get_file_metadata(image_array) → dict`**
- Recupera nome file e dimensione
- **Validazione**: Controlli su formato e lunghezza
- **Parsing**: Estrae filename e filesize

#### 🎯 Funzioni Principali

**`hideFile(container_img_path, secret_file_path, output_img_path)`**
- Nasconde qualsiasi file nell'immagine
- **Lettura binaria**: Legge file come stream di byte
- **Conversione bit**: Ogni byte → 8 bit da nascondere
- **Offset metadati**: Spazio riservato all'inizio per informazioni file

**`recoverFile(steg_img_path, output_dir) → str`**
- Recupera file nascosto
- **Lettura metadati**: Ottiene nome e dimensione originali
- **Estrazione bit**: Legge esatto numero di bit necessari
- **Ricostruzione**: Converte bit in byte e salva file

#### 📊 Funzioni di Analisi

**`calculate_file_capacity(container_img_path) → int`**
- Calcola capacità in byte per file generici
- **Metriche dettagliate**: Bit totali, spazio metadati, KB disponibili
- **Esempi pratici**: Tipi di file supportati con dimensioni
- **Raccomandazioni**: Soglia 10% per qualità ottimale

#### 🎮 Funzioni UI

**`handle_hide_file()`**
- **Analisi preventiva**: Mostra capacità e esempi
- **Validazione dimensioni**: Controlla compatibilità file
- **Avvisi sicurezza**: Warning per file grandi (>10% capacità)
- **Conferma utente**: Richiede conferma per file che potrebbero causare distorsioni

**`handle_recover_file()`**
- Recupero automatico con nome file originale
- **Prefisso recovered_**: Evita sovrascritture accidentali

---

## 🔬 Algoritmi e Tecniche Utilizzate

### Steganografia LSB (Least Significant Bit)
- **Principio**: Modifica i bit meno significativi dei pixel RGB
- **Impatto visivo**: Minimo, cambiamenti impercettibili all'occhio umano
- **Capacità**: 1 bit per canale colore = 3 bit per pixel

### Gestione Metadati con Prefisso di Lunghezza
- **Struttura**: [Lunghezza(16bit)][Dati(N×8bit)]
- **Robustezza**: Recupero affidabile anche con dati corrotti
- **Flessibilità**: Supporta metadati di lunghezza variabile

### Algoritmo di Distribuzione Adattiva (Image-in-Image)
- **Divisore dinamico**: Calcola spaziatura ottimale per distribuzione uniforme
- **Coda di bit**: Gestisce bit parziali per massima efficienza
- **Posizionamento**: Usa posizioni float per distribuzione precisa

## 🛡️ Gestione Errori e Validazioni

### Controlli Preventivi
- ✅ Verifica esistenza file di input
- ✅ Validazione formato immagini (conversione RGB automatica)
- ✅ Calcolo spazio richiesto vs disponibile
- ✅ Controlli di integrità sui metadati

### Messaggi di Errore Informativi
- ✅ Dimensioni esatte in KB per chiarezza
- ✅ Suggerimenti per risolvere i problemi
- ✅ Indicazioni precise su spazio mancante

### Raccomandazioni Anti-Distorsione
- ✅ Soglia del 10% della capacità massima
- ✅ Avvisi per utilizzi intensivi
- ✅ Conferme utente per operazioni rischiose

## 🎨 Design Pattern Utilizzati

### Separazione delle Responsabilità
- **main.py**: Solo interfaccia utente e navigazione
- **utility.py**: Funzioni helper generiche
- **funzioni/**: Logica specifica per ogni tipo di steganografia

### Template Method Pattern
- Struttura comune per tutte le operazioni:
  1. Analisi capacità
  2. Validazione input
  3. Elaborazione
  4. Salvataggio risultati

### Error Handling Consistente
- Blocchi try-catch uniformi
- Messaggi di errore standardizzati
- Gestione graceful degli errori di I/O

## 📈 Metriche di Performance

### Efficienza Spaziale
- **Testo**: ~1 bit per carattere (con UTF-8)
- **Immagini**: Configurabile tramite parametri LSB/MSB
- **File**: 1 bit per bit del file originale

### Qualità dell'Immagine
- **LSB singolo**: Distorsione minima (< 0.4% per canale)
- **LSB multipli**: Distorsione proporzionale al numero di bit
- **Raccomandazione**: Uso del 10% della capacità per qualità ottimale
