# Blueprint: 4-Brained Unreal Engine Dev Crew

## Overkoepelende Strategie
Dit plan beschrijft de opzet voor een hybrid local/cloud multi-agent systeem in CrewAI-Studio. 
Het doel is om 90% van het iteratieve en data-zware ("RAG") werk door de lokale GPU (Guardian) te laten doen om OpenRouter credits te besparen, terwijl complexe C++ logica en probleemoplossing 
aan frontier cloud-modellen wordt overgelaten.

## Architectuur (Process: Hierarchical)
In een "Hierarchical" process flow krijgt de Manager agent de leiding. Hij verdeelt het werk, kijkt het na, en stuurt bij waar nodig. Hier zit ook de **Human-in-the-Loop (HitL)** ingebakken.

### 1. De Manager / Orchestrator (CEO)
* **Provider:** OpenRouter
* **Model:** `deepseek/deepseek-v4-pro` of `openai/gpt-5.5`
* **Rol:** Ontvangt het hoofddoel, snijdt het op in subtaken, en delegeert.
* **Instructie:** "Delegeer codeerwerk primair aan de Local Programmer. Bij falen of na 2 mislukte iteraties: escaleer specifieke bestanden naar de Expert Programmer. Beoordeel het eindresultaat. Vraag om *Human Approval* (HitL) voordat taken definitief geaccepteerd worden."
* **Human Input:** TRUE (Pauzeert voor de gebruiker om goedkeuring te geven of richting te wijzen).

### 2. De Local Researcher (RAG / Data Scraper) 🕵️‍♂️
* **Provider:** Guardian (Lokaal)
* **Model:** `Gemma4-A2B-Uncensored`
* **Tools:** `RAGTool`, `FileReadTool`
* **Rol:** Leest door actuele of zware Unreal Engine 5 C++ documentatie of lokale class bestanden zonder rekening te houden met tokenkosten.
* **Output:** Geeft extreem gecondenseerde samenvattingen en context arrays terug aan de Manager, zodat cloud agenten geen overtollige read/context tokens verbranden.

### 3. De Local Programmer (Het Werkpaard) 🐴
* **Provider:** Guardian (Lokaal)
* **Model:** `Qwen3.6-35B`
* **Rol:** Doet het dagelijkse "meter werk". Simpele UE classes, boilerplate, iteratieve aanpassingen, headers/includes opzetten.
* **Kosten:** €0,00 - Hier klopt de GPU de uren.

### 4. De Expert Programmer (De Sniper) 🎯
* **Provider:** OpenRouter
* **Model:** `anthropic/claude-mythos-preview` of `anthropic/claude-opus-4.7`
* **Rol:** Wordt standaard niet gebruikt. Wordt alleen "wakker gebeld" door de Manager wanneer de Local Programmer vastloopt op complexe Unreal pointer logica, garbage collection (`UObject`), of harde C++ linker/compilatie bugs.
* **Kosten:** Duur, maar zijn context is minuscuul omdat hij enkel de geëscaleerde, specifieke snippet voorgelegd krijgt door de Manager.

## Workflow (Uitrol Instructies CrewAI-Studio)
1. **Agents Maken:** Vul in de Studio op de Agents-tab de 4 bovenstaande rollen in, gekoppeld aan de juiste Provider/Model vanuit de Dropdown menu's.
2. **HitL Aanzetten:** Zet de "Require Human Approval" of "Human Input" toggles **aan** op de taken die aan de Manager zijn toegewezen.
3. **Crew Maken:** Zet op de Crew-setup tab de Task Process op **Hierarchical**.
4. **Tools Koppelen:** Ken de RAG- en Directory/File-tools uitsluitend toe aan de Local Researcher Agent, zodat deze het zware leeswerk lokaal afhandelt.
