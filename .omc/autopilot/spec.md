# Pokémon Red Autonomous Playthrough - Specification

## Product Goal
Autonomously play through Pokémon Red (USA) from Pallet Town to the Elite Four championship, making strategic decisions to optimize gameplay speed while maintaining a valid path to victory.

## Current State
- **Game Server**: http://localhost:8765 (PID 32068, alive)
- **ROM**: `/Users/conanssam-m4/Downloads/pokerl-pokemon-red/PokemonRL/roms/sequence1_house_exit/PokemonRed.gb`
- **Starting Location**: Pallet Town (map_id=0, position unknown due to state API null values)
- **API Endpoints**:
  - `GET /state` — returns game state (map, position, party, badges, items)
  - `POST /action` — sends button presses: `{"actions": ["press_up", "press_down", "press_left", "press_right", "press_a", "press_b"]}`
  - `GET /screenshot` — returns current game screen as PNG
  - `POST /reasoning` — sends reasoning event to dashboard

## High-Level Strategy

### Phase 1: Starter Pokémon Acquisition (Pallet Town → Oak's Lab → Route 1+)
- Navigate to Oak's Lab
- Trigger Oak event to receive starter Pokémon
- Choose optimal starter (Bulbasaur recommended for Brock/Misty)
- Exit to Route 1

### Phase 2: Early Game (Route 1 → Viridian City → Pewter City)
- Capture wild Pokémon (Pidgeot line for flight, useful Pokédex entries)
- Grind levels if needed
- Reach Pewter City Pokémon Center
- Defeat Brock (Rock-type Gym Leader)

### Phase 3: Mid Game (Viridian Forest → Cerulean City)
- Navigate Viridian Forest (tight corridor, watch for Pidgeotto/Bulbasaur)
- Reach Cerulean City
- Defeat Misty (Water-type Gym Leader)
- Continue east through Route 6

### Phase 4: Progression (Vermilion City → S.S. Anne → Rockete Hideout)
- Defeat Lt. Surge (Electric-type Gym)
- Sail S.S. Anne
- Raid Rocket Hideout in Celadon City (optional but recommended for exp)

### Phase 5: Mid-Late Game (Celadon → Lavender Town → Silph Co. → Saffron City)
- Defeat Erika (Grass-type Gym in Celadon)
- Handle ghost Pokémon in Pokémon Tower (need Pokéflute from Saffron)
- Defeat Blue at Saffron City
- Defeat Sabrina (Psychic-type Gym)

### Phase 6: Late Game (Victory Road → Elite Four)
- Navigate Victory Road maze
- Stock up on healing items
- Battle Elite Four (Lorelei, Bruno, Agatha, Lance)
- Defeat Champion Blue

## Key Mechanics

### Movement
- Use directional presses (up/down/left/right) to navigate
- Watch for walls/water (visible on screenshot)
- Wait times minimized (10-30 frames max between actions)

### Battles
- Use type advantage (grass < fire, water < electric, etc.)
- Prioritize catching Pokémon with high base stats
- Grind levels at key checkpoints

### UI Navigation
- A button to select/confirm
- B button to cancel/retreat
- Hold up/down to scroll in menus

## Success Criteria
1. ✅ Received all 8 Gym Badges
2. ✅ Reached Elite Four chamber
3. ✅ Defeated Champion Blue
4. ✅ Game credits roll (victory)

## Checkpoint Strategy
- Save game state and screenshot after each major milestone
- Store checkpoint metadata (location, level, party composition) in GitHub
- Create PR for each completed region/gym

## Constraints
- Server must remain alive (http://localhost:8765 must stay reachable)
- Movement/action latency: ~100ms per action
- No external input (fully autonomous)
- Screenshot verification for navigation accuracy
