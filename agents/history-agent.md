# Agente History

## Obiettivo
Genera la storia del gruppo AperiPoker, analizzando TUTTA la chat dal 2013/2019 ad oggi.

## Input
Leggi il file `data/raw_messages_all.json` che contiene tutti i messaggi storici.

## Output
Genera il file `data/history.json` con questa struttura:

```json
{
  "yearsActive": 11,
  "totalMessages": 33000,
  "foundingDate": "3 Settembre 2013",
  "founder": "Giacomo Dolfi",
  "timeline": [
    {
      "date": "Settembre 2013",
      "title": "La Fondazione",
      "description": "Giacomo Dolfi crea il gruppo 'Aperipoker?' con un punto interrogativo profetico"
    },
    {
      "date": "Aprile 2019",
      "title": "L'Espansione",
      "description": "Il gruppo riprende vita con nuovi membri..."
    }
  ],
  "yearlyStats": {
    "2019": {
      "messages": 1234,
      "activeMembers": 5,
      "mvp": "Nome più attivo",
      "highlight": "Una frase o evento memorabile dell'anno"
    },
    "2020": { ... },
    "2025": { ... },
    "2026": { ... }
  },
  "evolutionNarrative": "Una descrizione narrativa di 3-5 paragrafi che racconta l'evoluzione del gruppo...",
  "generatedAt": "2026-01-18T12:00:00"
}
```

## Istruzioni

1. Leggi `data/raw_messages_all.json`

2. Identifica momenti chiave nella storia del gruppo:
   - Creazione del gruppo
   - Arrivo/uscita di membri significativi
   - Cambiamenti nel tono/attività del gruppo
   - Eventi esterni che hanno influenzato le discussioni
   - Periodi di picco e di silenzio

3. Per ogni anno, calcola:
   - Numero totale messaggi
   - Membri attivi (chi ha scritto almeno 10 messaggi)
   - MVP (chi ha scritto di più)
   - Un "highlight" rappresentativo dell'anno

4. Scrivi una narrativa che racconti l'evoluzione del gruppo:
   - Come è nato?
   - Come si è evoluto negli anni?
   - Quali sono state le "ere" del gruppo?
   - Cosa rende unico questo gruppo?

## Stile della Narrativa

La narrativa deve essere:
- **Epica ma ironica**: come una saga eroica, ma con autoironia
- **Affettuosa**: celebra il gruppo e i suoi membri
- **Specifica**: usa riferimenti reali quando possibile
- **Divertente**: mantieni il tono goliardico

## Esempio di Narrativa

"L'AperiPoker nacque in un giorno di settembre del 2013, quando Giacomo Dolfi, con la lungimiranza di un visionario e la prudenza di un italiano, creò un gruppo WhatsApp con un nome che era già una domanda esistenziale: 'Aperipoker?'. Quel punto interrogativo avrebbe definito l'essenza stessa del gruppo per i decenni a venire.

I primi anni furono avvolti nel mistero (o forse semplicemente nessuno scriveva). Fu solo nell'aprile 2019 che il gruppo rinacque dalle proprie ceneri, come una fenice toscana che preferisce l'aperitivo al fuoco..."

## Note
- Il gruppo è stato creato il 9/3/13 ma i messaggi partono dal 4/5/19
- Concentrati sui pattern e le dinamiche che emergono dai dati
- Cerca di identificare "ere" o fasi distinte del gruppo

## Esecuzione
```bash
cd /home/alessio/repos/aperipoker-website
# Claude CLI leggerà questo file e genererà la storia
```
