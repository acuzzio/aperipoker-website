# Agente Membri

## Obiettivo
Genera profili semiseri per ogni membro del gruppo, descrivendo "chi è questo qua" in modo goliardico.

## Input
Leggi i file:
- `data/raw_messages_all.json` - TUTTA la chat storica (2019-2026) per capire davvero chi è ognuno
- `data/classifica.json` - statistiche correnti (2026)
- `data/best-of.json` (se esiste) - momenti memorabili per arricchire i profili

## Output
Genera/aggiorna il file `data/membri.json` con questa struttura:

```json
{
  "members": [
    {
      "name": "Nome Utente",
      "emoji": "🎭",
      "title": "Il Filosofo del Gruppo",
      "description": "Descrizione semiseria di 2-3 frasi che cattura la personalità",
      "traits": ["Nottambulo", "Re dei meme", "Sempre in ritardo"],
      "catchphrase": "La sua frase tipica o intercalare",
      "superpower": "Il suo superpotere nel gruppo",
      "weakness": "Il suo punto debole",
      "stats": {
        "messageCount": 1234,
        "favoriteEmoji": "😂",
        "peakHour": "23:00",
        "avgResponseTime": "velocissimo | normale | geologico"
      },
      "bestMoment": "Riferimento al suo momento migliore",
      "worstMoment": "Riferimento alla sua figura peggiore",
      "compatibility": {
        "bestFriend": "Nome con cui interagisce di più",
        "nemesis": "Nome con cui litiga di più (scherzosamente)"
      }
    }
  ],
  "groupDynamics": {
    "description": "Descrizione generale delle dinamiche del gruppo",
    "subgroups": ["I nottambuli", "I mattinieri", "I lurker"]
  },
  "generatedAt": "2025-01-18T12:00:00"
}
```

## Istruzioni

1. Leggi i messaggi e le statistiche esistenti

2. Per ogni membro, analizza:
   - **Stile di scrittura**: formale/informale, lungo/breve, emoji-heavy
   - **Orari**: mattiniero, nottambulo, irregolare
   - **Argomenti preferiti**: di cosa parla di più
   - **Interazioni**: con chi interagisce di più, chi cita spesso
   - **Comportamento**: inizia discussioni o risponde? Lurker o protagonista?

3. Assegna a ogni membro:
   - Un **emoji** che lo rappresenta
   - Un **titolo** goliardico (es: "Il Saggio del Nulla", "L'Ombra Silenziosa")
   - Una **descrizione** di 2-3 frasi che catturi la sua essenza
   - **Traits**: 3-5 caratteristiche distintive
   - **Catchphrase**: una frase o intercalare tipico
   - **Superpower/Weakness**: in chiave ironica

4. Analizza le dinamiche di gruppo:
   - Chi risponde a chi più spesso
   - Sottogruppi naturali
   - Pattern di interazione

## Stile

Le descrizioni devono essere:
- **Affettuose**: mai cattive, sempre con affetto
- **Specifiche**: basate su comportamenti reali osservati
- **Divertenti**: goliardiche ma non offensive
- **Riconoscibili**: chi legge deve dire "è proprio lui!"

## Esempi di Profili

### Esempio 1
```json
{
  "name": "Marco",
  "emoji": "🦉",
  "title": "Il Guardiano della Notte",
  "description": "Non si sa se lavori di notte o semplicemente non dorma mai. Appare misteriosamente alle 3 di notte con meme del 2012 che in qualche modo sono ancora rilevanti.",
  "traits": ["Nottambulo cronico", "Archeologo di meme", "Zero filtri dopo mezzanotte"],
  "catchphrase": "Ma che ore sono?",
  "superpower": "Tenere vivo il gruppo quando tutti dormono",
  "weakness": "Qualsiasi cosa prima delle 11 di mattina"
}
```

### Esempio 2
```json
{
  "name": "Giulia",
  "emoji": "📚",
  "title": "La Voce della Ragione",
  "description": "L'unica che legge i messaggi prima di rispondere. Interviene chirurgicamente per sedare le discussioni più accese con la calma di un monaco zen.",
  "traits": ["Pacificatrice", "Grammar nazi pentita", "Always online ma mai spam"],
  "catchphrase": "Raga, calmi",
  "superpower": "Far sentire tutti in torto con una sola frase",
  "weakness": "Le discussioni sul fantacalcio (le ignora sistematicamente)"
}
```

## Note
- Mantieni coerenza con i dati reali (non inventare cose che non emergono dai messaggi)
- Se non hai abbastanza dati su qualcuno, il profilo può essere più generico
- Il tono deve essere quello di amici che si prendono in giro affettuosamente

## Esecuzione
```bash
cd /home/alessio/repos/aperipoker-website
# Claude CLI leggerà questo file e genererà i profili
```
