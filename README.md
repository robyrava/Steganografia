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
├── DOCUMENTATION.md        # Documentazione tecnica dettagliata
├── funzioni/               # Moduli specifici per ogni tipo di steganografia
│   ├── text_in_image.py    # Steganografia testuale
│   ├── image_in_image.py   # Steganografia di immagini
│   └── file_in_image.py    # Steganografia di file generici
└── __pycache__/            # File Python compilati (generati automaticamente)
    └── utility.cpython-312.pyc
```

## Caratteristiche Principali

### ✨ Analisi della Capacità (NUOVO!)
- **Calcolo automatico** della capacità massima per ogni tipo di contenuto
- **Visualizzazione in KB** per maggiore chiarezza
- **Raccomandazioni anti-distorsione** (utilizzo consigliato al 10% della capacità)
- **Validazione preventiva** delle dimensioni prima dell'occultamento
- **Tabelle comparative** per diversi parametri LSB
- **Esempi pratici** di file supportati con dimensioni

### 🔍 Steganografia Testuale
- Supporto completo per caratteri **UTF-8**
- Terminatore robusto per il recupero affidabile
- **Analisi capacità automatica** prima dell'inserimento del messaggio
- Calcolo della capacità in caratteri e pagine di testo
- **Statistiche dettagliate** sull'utilizzo della capacità
- **Validazione preventiva** della lunghezza del messaggio

### 🖼️ Steganografia di Immagini
- **Parametri LSB/MSB configurabili** per ottimizzare qualità vs capacità
- **Modalità automatica** per il calcolo dei parametri ottimali
- **Modalità manuale** per utenti esperti con controllo del divisore
- **Tabella comparativa** della capacità per ogni valore LSB (1-8)
- **Calcolo automatico del divisore** per distribuzione ottimale
- **Controllo personalizzabile del divisore** in modalità manuale

### 📁 Steganografia di File
- Supporto per **qualsiasi tipo di file** (documenti, audio, video, archivi)
- **Metadati automatici** (nome file e dimensione)
- **Analisi capacità con esempi** di tipi di file supportati
- **Avvisi di sicurezza** per file che potrebbero causare distorsioni
- **Conferma utente** per file grandi (>10% capacità)
- **Statistiche dettagliate** del file da nascondere

### 🛡️ Sicurezza e Affidabilità
- **Gestione robusta degli errori** con messaggi informativi in KB
- **Controlli di integrità** per i metadati
- **Validazione preventiva** dello spazio disponibile
- **Salvataggio automatico** in formato PNG per preservare i dati
- **Messaggi di errore migliorati** con dettagli su spazio richiesto/disponibile

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

4. **Visualizza l'analisi della capacità** (automatica)

5. **Segui le istruzioni interattive**

## Esempi di Capacità

Per un'immagine **1920x1080 pixel**:

### Testo
- **777,599 caratteri** UTF-8 sicuri
- **888,685 caratteri** solo ASCII
- **777.6 KB** di capacità totale
- **~388 pagine** di testo (2000 caratteri/pagina)
- **Raccomandazione**: Massimo 77,759 caratteri per evitare distorsioni

### File
- **758.38 KB** di capacità totale
- **75.84 KB** raccomandati per evitare distorsioni
- **Esempi supportati**:
  - ✅ Documenti di testo (fino a 50 KB)
  - ✅ Immagini piccole (fino a 200 KB)
  - ✅ Documenti PDF (fino a 500 KB)
  - ❌ Audio MP3 (richiede 1 MB)
  - ❌ Video brevi (richiede 5 MB)

### Immagini (LSB=4)
- **Capacità**: 3,109.9 KB disponibili
- Immagini fino a **1019x1019 pixel**
- **~1,036,324 pixel** totali
- **Tabella comparativa** per LSB 1-8 con dimensioni massime

## Tecnologia

### Algoritmo LSB (Least Significant Bit)
- Modifica i bit meno significativi dei pixel RGB
- **Distorsioni minime** nell'immagine contenitore
- **Recupero perfetto** dei dati nascosti
- **Parametri configurabili** per bilanciare qualità vs capacità

### Formato dei Metadati
- **Header con prefisso di lunghezza** per robustezza
- **Codifica UTF-8** per il supporto internazionale
- **Controlli di integrità** per prevenire corruzioni
- **Spazio riservato**: 512 byte (immagini), 1 KB (file)

### Calcolo del Divisore (Immagini)
- **Calcolo automatico** per distribuzione ottimale dei dati
- **Controllo manuale** disponibile per utenti esperti
- **Range di sicurezza** (10%-200% del valore ottimale)
- **Conferma richiesta** per valori fuori range

## Nuove Funzionalità v2.0

### 📊 Analisi Capacità Avanzata
- **Calcolo preventivo** prima di ogni operazione
- **Visualizzazione in KB** per tutte le unità di misura
- **Tabelle comparative** per parametri LSB
- **Esempi pratici** di contenuti supportati

### 🎯 Validazione Intelligente
- **Controlli automatici** delle dimensioni
- **Avvisi personalizzati** per file grandi
- **Raccomandazioni dinamiche** anti-distorsione
- **Statistiche in tempo reale** dell'utilizzo

### 🔧 Controlli Avanzati (Immagini)
- **Modalità automatica migliorata** con solo visualizzazione parametri
- **Modalità manuale espansa** con controllo divisore
- **Calcolo ottimale** del divisore per ogni combinazione LSB/MSB
- **Range di sicurezza** per parametri personalizzati

## Limitazioni

- **Solo immagini RGB** (conversione automatica se necessario)
- **Salvataggio in PNG** per preservare i dati (formato lossless)
- **Dimensione massima** limitata dalla capacità dell'immagine contenitore
- **Raccomandazione 10%** della capacità per qualità ottimale

## Contributi

Questo progetto è stato sviluppato come strumento educativo per comprendere i principi della steganografia digitale.

## Licenza

Progetto educativo - Uso libero per scopi didattici e di ricerca.
