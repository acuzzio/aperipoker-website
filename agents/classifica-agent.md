# Agente Classifica

## Obiettivo
Genera/aggiorna il file `data/classifica.json` con statistiche dettagliate sull'attività dei membri.

## Input
Leggi il file `data/raw_messages.json` che contiene tutti i messaggi parsati.

## Output
Aggiorna il file `data/classifica.json` con questa struttura:

```json
{
  "members": [
    {
      "name": "Nome Utente",
      "messageCount": 1234,
      "wordCount": 5678,
      "avgWordsPerMessage": 4.6,
      "mediaCount": 45,
      "emojiFrequency": 0.23,
      "peakHour": 21,
      "peakDay": "Sabato",
      "streak": 15,
      "funFact": "Una curiosità divertente su questo utente"
    }
  ],
  "hourlyStats": {
    "0": 123,
    "1": 45,
    ...
  },
  "dailyStats": {
    "0": 1234,  // Lunedì
    "1": 1456,  // Martedì
    ...
  },
  "generatedAt": "2025-01-18T12:00:00"
}
```

## Istruzioni

1. Leggi `data/raw_messages.json`
2. Per ogni membro calcola:
   - Conteggio messaggi e parole
   - Media parole per messaggio
   - Ora di punta (quando scrive di più)
   - Giorno di punta
   - Streak più lungo (giorni consecutivi con almeno 1 messaggio)
   - Un "funFact" basato sui dati (es: "Campione delle 3 di notte", "Il re degli audio")

3. Ordina i membri per numero di messaggi (decrescente)

4. Calcola statistiche aggregate (orarie e giornaliere)

5. Scrivi il risultato in `data/classifica.json`

## Esempio di funFacts
- "Non dorme mai - 47% dei messaggi dopo mezzanotte"
- "Il poeta del gruppo - media di 12 parole per messaggio"
- "Speed runner - media di 2 parole per messaggio"
- "Il weekend warrior - 80% messaggi nel weekend"
- "Il pendolare - picco di attività alle 8 e alle 18"

## Esecuzione
```bash
cd /home/alessio/repos/aperipoker-website
# Claude CLI leggerà questo file e genererà l'output
```
