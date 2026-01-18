# Agente Pagelle

## Obiettivo
Genera pagelle settimanali per ogni membro del gruppo, con voti e giudizi goliardici.

## Input
Leggi i file:
- `data/raw_messages.json` - tutti i messaggi con timestamp
- `data/membri.json` (se esiste) - per conoscere le personalità

## Output
Genera/aggiorna il file `data/pagelle.json` con questa struttura:

```json
{
  "weeks": [
    {
      "startDate": "2025-01-13",
      "endDate": "2025-01-19",
      "pagelle": [
        {
          "name": "Nome Utente",
          "voto": 7.5,
          "giudizio": "Settimana in crescita, finalmente si è svegliato dal letargo",
          "messaggi": 45,
          "mediaGiornaliera": 6.4,
          "highlights": ["Battuta del giorno martedì", "Ha vinto la discussione sul calcio"],
          "lowlights": ["Sparito tutto mercoledì", "Ha postato un meme del 2015"]
        }
      ],
      "riassunto": "Settimana tranquilla dominata dalle discussioni sul fantacalcio...",
      "awards": {
        "mvp": "Nome del MVP",
        "chiacchierone": "Chi ha scritto di più",
        "fantasma": "Chi è sparito di più",
        "comico": "La battuta migliore di chi"
      }
    }
  ],
  "generatedAt": "2025-01-18T12:00:00"
}
```

## Istruzioni

1. Leggi `data/raw_messages.json`

2. Raggruppa i messaggi per settimana (lunedì-domenica)

3. Per ogni settimana, per ogni membro attivo:
   - Calcola messaggi totali e media giornaliera
   - Assegna un voto da 1 a 10 basato su:
     - Partecipazione (30%)
     - Qualità/lunghezza messaggi (30%)
     - Costanza durante la settimana (40%)
   - Scrivi un giudizio GOLIARDICO ma affettuoso (max 2 frasi)
   - Identifica highlights e lowlights dalla conversazione

4. Scrivi un riassunto della settimana (3-5 frasi) che catturi:
   - Argomenti principali discussi
   - Momenti salienti
   - Tono generale (tranquillo, litigioso, goliardico, ecc.)

5. Assegna gli awards settimanali

## Stile dei Giudizi

I giudizi devono essere:
- Ironici ma mai cattivi
- Specifici (riferimenti a cose successe se possibile)
- Brevi (max 2 frasi)

Esempi:
- Voto 8: "Settimana da incorniciare. Ha tenuto in piedi il gruppo mentre gli altri dormivano."
- Voto 6: "Presente ma non pervenuto. Come un arbitro: c'è ma non si nota."
- Voto 4: "Ha fatto il suo ingresso trionfale... domenica sera alle 23:58."
- Voto 9: "Il trascinatore. Senza di lui saremmo ancora a discutere del nulla cosmico."

## Esecuzione
```bash
cd /home/alessio/repos/aperipoker-website
# Claude CLI leggerà questo file e genererà le pagelle
```
