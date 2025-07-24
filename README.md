# Steganografia su Immagini

Un'applicazione completa per nascondere e recuperare diversi tipi di dati all'interno di immagini utilizzando tecniche di steganografia LSB (Least Significant Bit).

## Panoramica del Progetto

Questo progetto implementa tre diversi tipi di steganografia:

1. **Steganografia Testuale**: Nasconde stringhe di testo in immagini
2. **Steganografia di Immagini**: Nasconde un'immagine dentro un'altra immagine
3. **Steganografia di File**: Nasconde file generici (documenti, audio, video, ecc.) in immagini

## Struttura del Progetto

```
Steganografia/
├── main.py                 # File principale con il menu interattivo
├── utility.py              # Funzioni di utilità generali
├── README.md               # Questo file di documentazione
├── funzioni/               # Moduli specifici per ogni tipo di steganografia
│   ├── text_in_image.py    # Steganografia testuale
│   ├── image_in_image.py   # Steganografia di immagini
│   └── file_in_image.py    # Steganografia di file generici
└── __pycache__/            # File Python compilati (generati automaticamente)
    └── utility.cpython-312.pyc
```

## Caratteristiche Principali

### ✨ Analisi della Capacità
- **Calcolo automatico** della capacità massima per ogni tipo di contenuto
- **Visualizzazione in KB** per maggiore chiarezza
- **Raccomandazioni anti-distorsione** (utilizzo consigliato al 10% della capacità)
- **Validazione preventiva** delle dimensioni prima dell'occultamento

### 🔍 Steganografia Testuale
- Supporto completo per caratteri **UTF-8**
- Terminatore robusto per il recupero affidabile
- Calcolo della capacità in caratteri e pagine di testo
- Statistiche dettagliate sull'utilizzo della capacità

### 🖼️ Steganografia di Immagini
- **Parametri LSB/MSB configurabili** per ottimizzare qualità vs capacità
- **Modalità automatica** per il calcolo dei parametri ottimali
- **Modalità manuale** per utenti esperti
- Tabella comparativa della capacità per ogni valore LSB

### 📁 Steganografia di File
- Supporto per **qualsiasi tipo di file** (documenti, audio, video, archivi)
- **Metadati automatici** (nome file e dimensione)
- **Avvisi di sicurezza** per file che potrebbero causare distorsioni
- Esempi pratici di tipi di file supportati

### 🛡️ Sicurezza e Affidabilità
- **Gestione robusta degli errori** con messaggi informativi
- **Controlli di integrità** per i metadati
- **Validazione preventiva** dello spazio disponibile
- **Salvataggio automatico** in formato PNG per preservare i dati

## Requisiti di Sistema

- **Python 3.8+**
- **Pillow (PIL)** per la manipolazione delle immagini
- **NumPy** per l'elaborazione degli array
- **Sistema operativo**: Windows, macOS, Linux

## Installazione

```bash
pip install Pillow numpy
```

## Utilizzo Rapido

1. **Avvia l'applicazione**:
   ```bash
   python main.py
   ```

2. **Scegli il tipo di operazione**:
   - Nascondi dati
   - Recupera dati

3. **Seleziona il tipo di contenuto**:
   - Stringa di testo
   - Immagine
   - File generico

4. **Segui le istruzioni interattive**

## Esempi di Capacità

Per un'immagine **1920x1080 pixel**:

### Testo
- **777,599 caratteri** UTF-8 sicuri
- **~388 pagine** di testo (2000 caratteri/pagina)

### File
- **758 KB** di capacità totale
- **75 KB** raccomandati per evitare distorsioni

### Immagini (LSB=4)
- Immagini fino a **1019x1019 pixel**
- **~1,036,324 pixel** totali

## Tecnologia

### Algoritmo LSB (Least Significant Bit)
- Modifica i bit meno significativi dei pixel RGB
- **Distorsioni minime** nell'immagine contenitore
- **Recupero perfetto** dei dati nascosti

### Formato dei Metadati
- **Header con prefisso di lunghezza** per robustezza
- **Codifica UTF-8** per il supporto internazionale
- **Controlli di integrità** per prevenire corruzioni

## Limitazioni

- **Solo immagini RGB** (conversione automatica se necessario)
- **Salvataggio in PNG** per preservare i dati (formato lossless)
- **Dimensione massima** limitata dalla capacità dell'immagine contenitore

## Contributi

Questo progetto è stato sviluppato come strumento educativo per comprendere i principi della steganografia digitale.

## Licenza

Progetto educativo - Uso libero per scopi didattici e di ricerca.
