# Map standard tile strings to a 34-item index array
TILE_TO_INDEX = {
    '1m': 0, '2m': 1, '3m': 2, '4m': 3, '5m': 4, '6m': 5, '7m': 6, '8m': 7, '9m': 8,
    '1p': 9, '2p': 10, '3p': 11, '4p': 12, '5p': 13, '6p': 14, '7p': 15, '8p': 16, '9p': 17,
    '1s': 18, '2s': 19, '3s': 20, '4s': 21, '5s': 22, '6s': 23, '7s': 24, '8s': 25, '9s': 26,
    '1z': 27, '2z': 28, '3z': 29, '4z': 30, '5z': 31, '6z': 32, '7z': 33  # East, South, West, North, Haku, Hatsu, Chun
}
INDEX_TO_TILE = {v: k for k, v in TILE_TO_INDEX.items()}

class HandDivider:
    
    @staticmethod
    def to_34_array(tiles: list[str]) -> list[int]:
        """Converts a list of tile strings into a 34-element count array."""
        counts = [0] * 34
        for tile in tiles:
            counts[TILE_TO_INDEX[tile]] += 1
        return counts

    @staticmethod
    def to_strings(melds_of_indices: list[list[int]]) -> list[list[str]]:
        """Converts internal indices back to human-readable strings."""
        return [[INDEX_TO_TILE[idx] for idx in meld] for meld in melds_of_indices]

    @staticmethod
    def divide_hand(tiles: list[str]) -> list[list[list[str]]]:
        valid_divisions = []
        
        if len(tiles) == 14:
            orphans = ['1m', '9m', '1p', '9p', '1s', '9s', '1z', '2z', '3z', '4z', '5z', '6z', '7z']
            # Check if all tiles belong to the orphans list, and we have exactly 13 unique ones
            if all(t in orphans for t in tiles) and len(set(tiles)) == 13:
                # We package the entire hand into a single "1-block" division
                valid_divisions.append([tiles])


        # 1. Chiitoitsu (Seven Pairs) Check
        unique_tiles = set(tiles)
        if len(unique_tiles) == 7 and all(tiles.count(t) == 2 for t in unique_tiles):
            valid_divisions.append([[t, t] for t in unique_tiles])

        # 2. Standard 4-Meld + 1-Pair Check
        counts = {}
        for t in tiles:
            counts[t] = counts.get(t, 0) + 1
        
        # Try treating every pair as the "head" of the hand
        for pair_tile, count in counts.items():
            if count >= 2:
                remaining = counts.copy()
                remaining[pair_tile] -= 2
                
                # --- The Recursive Backtracker ---
                def backtrack(current_counts, current_melds):
                    # Clean up empty slots
                    current_counts = {k: v for k, v in current_counts.items() if v > 0}
                    
                    # Base Case: No tiles left! We successfully divided the hand.
                    if not current_counts:
                        valid_divisions.append(current_melds + [[pair_tile, pair_tile]])
                        return
                        
                    # Pick the lowest tile to "anchor" our search (prevents infinite loops)
                    anchor = sorted(current_counts.keys(), key=lambda x: (x[1], x[0]))[0]
                    
                    # Path A: Try extracting a Triplet
                    if current_counts[anchor] >= 3:
                        next_counts = current_counts.copy()
                        next_counts[anchor] -= 3
                        backtrack(next_counts, current_melds + [[anchor, anchor, anchor]])
                        
                    # Path B: Try extracting a Sequence
                    if anchor[1] in ['m', 'p', 's']:
                        val = int(anchor[0])
                        suit = anchor[1]
                        t2 = f"{val+1}{suit}"
                        t3 = f"{val+2}{suit}"
                        
                        if current_counts.get(t2, 0) > 0 and current_counts.get(t3, 0) > 0:
                            next_counts = current_counts.copy()
                            next_counts[anchor] -= 1
                            next_counts[t2] -= 1
                            next_counts[t3] -= 1
                            backtrack(next_counts, current_melds + [[anchor, t2, t3]])

                # Start the recursive search for this pair
                backtrack(remaining, [])
                
        return valid_divisions

# ==========================================
# EXAMPLE USAGE:
# ==========================================
if __name__ == "__main__":
    # Example 1: Standard Pinfu Shape (2m 3m 4m, 4p 5p 6p, 6s 7s 8s, 1z 1z 1z, wait on 9p 9p)
    test_hand = ["2m", "2m", "3m", "3m", "4m", "4m", "5s", "5s", "6s", "6s", "7s", "7s", "9p", "9p"]
    
    # Example 2: Complex multi-wait shape (Chuuren Poutou structure or similar overlaps)
    # The algorithm will return multiple valid interpretations of the same hand.
    test_hand_2 = ["1m", "1m", "1m", "2m", "3m", "4m", "5m", "6m", "7m", "8m", "9m", "9m", "9m", "1m"]

    divisions = HandDivider.divide_hand(test_hand)

    print(f"Found {len(divisions)} valid ways to interpret the hand:")
    for i, division in enumerate(divisions):
        print(f"Interpretation {i + 1}: {division}")    