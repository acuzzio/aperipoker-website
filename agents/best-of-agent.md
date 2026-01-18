# Agente Best Of

## Obiettivo
Identifica e cataloga i momenti più memorabili, le battute migliori e gli epic fail della chat.

## Input
Leggi il file `data/raw_messages.json` che contiene tutti i messaggi.

## Output
Genera/aggiorna il file `data/best-of.json` con questa struttura:

```json
{
  "moments": [
    {
      "id": "unique-id-1",
      "category": "battute",
      "quote": "Il testo del messaggio memorabile",
      "author": "Nome Autore",
      "date": "2025-01-15",
      "context": "Breve contesto su cosa stava succedendo",
      "reactions": "Se ci sono state reazioni notevoli"
    }
  ],
  "hallOfFame": [
    // I 5 momenti migliori di sempre
  ],
  "categories": {
    "battute": "Battute e freddure memorabili",
    "fails": "Epic fail e figuracce",
    "quotes": "Citazioni involontariamente profonde o assurde",
    "momenti": "Momenti storici del gruppo"
  },
  "generatedAt": "2025-01-18T12:00:00"
}
```

## Categorie

### battute
Battute, freddure, giochi di parole che hanno fatto ridere il gruppo.
Cerca messaggi seguiti da molte risate ("ahaha", "lol", emoji ridenti) o che sono oggettivamente divertenti.

### fails
Epic fail memorabili:
- Autocorrettore disastroso
- Messaggi mandati nel gruppo sbagliato
- Figuracce epiche
- Previsioni sbagliate clamorosamente

### quotes
Citazioni involontarie, frasi fuori contesto che suonano assurde o profonde:
- Frasi che sembrano filosofiche ma non lo sono
- Affermazioni random ma iconiche
- Perle di saggezza involontaria

### momenti
Momenti storici del gruppo:
- Litigi epici (risolti)
- Decisioni importanti
- Anniversari e celebrazioni
- Eventi che hanno segnato il gruppo

## Istruzioni

1. Leggi tutti i messaggi in `data/raw_messages.json`

2. Identifica momenti notevoli cercando:
   - Messaggi lunghi seguiti da molte reazioni
   - Sequenze di messaggi con molte risate
   - Messaggi con contenuto insolito o memorabile
   - Discussioni particolarmente accese o divertenti

3. Per ogni momento:
   - Classifica nella categoria appropriata
   - Estrai la citazione (può essere un messaggio singolo o uno scambio breve)
   - Aggiungi contesto se necessario
   - Assegna un ID univoco

4. Seleziona i 5 migliori per la Hall of Fame

5. Scrivi il risultato in `data/best-of.json`

## Criteri di Selezione

Un buon momento per il Best Of deve essere:
- **Memorabile**: qualcosa che il gruppo ricorderebbe
- **Quotabile**: ha senso anche fuori contesto (o è divertente proprio perché non ne ha)
- **Rappresentativo**: cattura lo spirito del gruppo
- **Non offensivo**: goliardico ma non cattivo

## Note
- Non includere informazioni troppo personali o sensibili
- Mantieni il tono leggero e affettuoso
- Preferisci qualità a quantità (meglio 20 momenti top che 100 mediocri)

## Esecuzione
```bash
cd /home/alessio/repos/aperipoker-website
# Claude CLI leggerà questo file e identificherà i best moments
```
