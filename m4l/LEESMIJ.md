# Ngoma in Live (Max for Live)

Ngoma draait als Max-instrument op een MIDI-spoor. Tempo, start/stop en de maatpositie volgen Live. Het geluid komt als stereo-audio het spoor in, dus opnemen, resamplen en je eigen effecten werken gewoon.

Nodig: Live 12 Suite (of Live met Max for Live) met Max 9.

## Installeren
Sleep `Ngoma.amxd` (in deze map) op een lege MIDI-track. Werkt dat ooit niet: maak in Live een Max Instrument, klik Edit, open in Max via File > Open het bestand `Ngoma.maxpat`, en kopieer alles daaruit naar het device (Cmd+A, Cmd+C, dan in het device Cmd+V en Cmd+S).

## Proberen
1. Klik in het device op **Open Ngoma**. Er opent een venster met Ngoma, je lokale versie in ~/MijnOS/Ngoma/public.
2. Klik één keer ergens in Ngoma, zodat de browser geluid mag maken.
3. Druk op Play in Live. Ngoma start op de tel en volgt het tempo. Stop in Live stopt Ngoma.
4. Zet een kick of de metronoom erbij. Iets te vroeg of te laat? Draai aan **Offset** (-50 tot +50 ms).
5. Sluit het Ngoma-venster: Ngoma blijft in de maat en je hoort hem nog.

Linksonder in Ngoma staat een kleine regel met wat Live stuurt (speelt, tel, tempo). Klopt het tempo daar niet, stuur dan een screenshot van die regel.

## Goed om te weten
- Timing: Ngoma plant zijn slagen iets vooruit om de vertraging van de browser op te vangen. In de test liep hij binnen ongeveer 2 ms gelijk met Live. In een echte set kan het een paar ms schommelen: prima voor jammen en opnemen, niet sample-exact.
- Freezen en offline exporteren in Live werken niet, omdat de browser alleen in real time speelt. Neem op naar een audiospoor.
- De knop "url https://ngoma.pages.dev" in de editor schakelt naar de online versie; standaard laadt hij je lokale bestand.
- Dit is de tussenstap. De echte plugin (VST3/AU, sample-exact, ook freezen en exporteren) volgt: zie het stappenplan.
