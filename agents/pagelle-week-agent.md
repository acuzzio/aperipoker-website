# Agente Pagelle Settimanali - Valutazione Qualitativa

## Parametri Input
```
ANNO: [anno da analizzare, es. 2024]
SETTIMANA: [numero settimana ISO, es. 15]
```

## Obiettivo
Analizza UNA settimana specifica di messaggi e genera pagelle basate su criteri QUALITATIVI:
- Partecipazione emotiva e sociale
- Qualità umoristica delle interazioni
- Coinvolgimento nelle discussioni
- Supporto agli altri membri

NON basare i voti solo sulla quantità di messaggi.

## File da Leggere

1. **Messaggi della settimana**: `data/raw_messages_{ANNO}.json`
   - Filtra per la settimana ISO specificata
   - Se non esiste, usa `data/raw_messages_all.json` e filtra per anno

2. **Profili membri**: `data/membri.json`
   - Usa per conoscere personalità e stile di ogni membro
   - Adatta i giudizi alla personalità conosciuta

## Come Identificare la Settimana

```python
from datetime import datetime
import json

# Calcola range date per settimana ISO
def get_week_dates(year, week):
    # Primo giorno della settimana ISO (lunedì)
    first_day = datetime.strptime(f'{year}-W{week:02d}-1', '%G-W%V-%u')
    last_day = datetime.strptime(f'{year}-W{week:02d}-7', '%G-W%V-%u')
    return first_day, last_day
```

## Criteri di Valutazione (NON quantitativi)

| Criterio | Peso | Cosa Valutare |
|----------|------|---------------|
| **Partecipazione Sociale** | 30% | Risponde agli altri? Inizia discussioni? Coinvolge il gruppo? |
| **Qualità Umoristica** | 30% | Battute riuscite, ironia, timing comico, reazioni che provoca |
| **Contributo Emotivo** | 20% | Supporto ai compagni, condivisione personale, empatia mostrata |
| **Presenza Attiva** | 20% | Costanza, reattività, non-lurking, partecipazione distribuita |

### Come Assegnare i Voti

**Voto 8-10**: Ha reso la settimana memorabile
- Battute che hanno fatto ridere tutti
- Ha tenuto viva una discussione interessante
- Ha supportato qualcuno in un momento difficile
- Ha creato momenti di gruppo significativi

**Voto 6-7.5**: Partecipazione positiva standard
- Presente e reattivo
- Contributi utili alle discussioni
- Qualche momento divertente
- Interazioni equilibrate

**Voto 4-5.5**: Presente ma non incisivo
- Pochi messaggi di sostanza
- Risposte monosillabiche
- Lurking o partecipazione passiva
- Nessun contributo memorabile

**Voto 1-3.5**: Settimana da dimenticare
- Assente ingiustificato
- Solo messaggi di servizio
- Fantasma totale
- Ha rovinato discussioni (litigate eccessive, negatività)

## Output JSON

Salva in: `data/pagelle/{ANNO}/week-{SETTIMANA}.json`

```json
{
  "anno": 2024,
  "settimana": 15,
  "startDate": "2024-04-08",
  "endDate": "2024-04-14",
  "stats": {
    "totalMessages": 245,
    "activeMembers": 5,
    "avgPerMember": 49.0
  },
  "riassunto": "Narrativa della settimana in 3-5 frasi. Cosa è successo? Qual era il mood? Argomenti principali?",
  "bestQuotes": [
    {
      "quote": "La citazione esatta dal testo",
      "author": "Nome Autore",
      "context": "Perché è memorabile"
    }
  ],
  "pagelle": [
    {
      "name": "Nome Completo",
      "voto": 8.0,
      "giudizio": "Giudizio ironico e personalizzato in 2-3 frasi. Riferimenti specifici a cosa ha fatto questa settimana.",
      "messaggi": 45,
      "mediaGiornaliera": 6.4,
      "highlights": [
        "Cosa ha fatto di positivo/memorabile",
        "Momento specifico degno di nota"
      ],
      "citazioneTop": "La sua migliore frase della settimana (opzionale)"
    }
  ],
  "awards": {
    "mvp": "Chi ha brillato di più",
    "comico": "Il più divertente",
    "cuore": "Il più empatico/supportivo",
    "fantasma": "Il più assente (se applicabile)"
  }
}
```

## Stile dei Giudizi

### Tono
- Goliardico ma affettuoso
- Ironico ma MAI cattivo
- Specifico (cita cose successe nella settimana)
- Adattato alla personalità nota del membro

### Esempi per Personalità

**Adriano (il chiacchierone)**:
- "Ha scritto più lui in un'ora che il resto del gruppo in tre giorni. Ma almeno ci ha fatto ridere con la storia del..."
- "Il solito fiume in piena, ma questa settimana aveva ragione su tutto. Preoccupante."

**Cosimo (il sarcastico)**:
- "Con tre messaggi ha smontato una discussione di 50. Efficienza svizzera."
- "Il suo 'mah' di giovedì valeva più di interi monologhi altrui."

**Fausto (l'organizzatore)**:
- "Ha proposto 7 uscite, ne sono andate in porto 0. Record personale."
- "Il suo entusiasmo è commovente. Peccato che nessuno lo assecondi mai."

**Alessio V. (il giramondo)**:
- "Si è svegliato alle 15 e ha dominato la chat fino a mezzanotte. Time zone: chaos."
- "Internet di merda ma cuore d'oro. Ha consolato tutti dal suo bunker tropicale."

**Alessio M. (il laconico)**:
- "Il suo 'Credo' di mercoledì era carico di significati nascosti. O forse no."
- "Zen master della settimana. Tre parole, zero stress, massima saggezza."

**Giacomo (il fondatore)**:
- "Il Lider ha parlato e il gruppo ha ascoltato. Più o meno."
- "Domanda innocua il lunedì, guerra civile il martedì. Classico."

## Istruzioni di Esecuzione

1. **Leggi i messaggi** della settimana specificata
2. **Identifica i temi** principali discussi
3. **Analizza ogni membro** attivo:
   - Come ha partecipato?
   - Ha fatto ridere?
   - Ha supportato altri?
   - Ha contribuito alle discussioni?
4. **Assegna voti** basati sui criteri qualitativi
5. **Scrivi giudizi** personalizzati e specifici
6. **Seleziona citazioni** memorabili
7. **Salva il JSON** nel percorso corretto

## Esecuzione Parallela

Questo agente è progettato per essere eseguito in parallelo.

Per generare tutte le settimane di un anno:
```bash
# Identifica settimane con messaggi
python3 scripts/list_weeks_with_messages.py 2024

# Esegui in parallelo (esempio con Claude CLI)
claude "Esegui agents/pagelle-week-agent.md con ANNO=2024 SETTIMANA=1" &
claude "Esegui agents/pagelle-week-agent.md con ANNO=2024 SETTIMANA=2" &
# ... etc
```

## Note Importanti

- Se una settimana ha meno di 10 messaggi, considera di saltarla o dare voti bassi a tutti
- Se un membro non ha scritto nulla, assegna voto 3 con giudizio "Fantasma della settimana"
- Le citazioni devono essere ESATTE dal testo, non parafrasate
- I nomi devono corrispondere esattamente a quelli in membri.json
