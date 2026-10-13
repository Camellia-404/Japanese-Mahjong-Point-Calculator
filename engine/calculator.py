import math
from engine.hand_divider import HandDivider


YAKUMAN_LIST = ["四暗刻", "清老頭", "四槓子", "大三元", "国士無双", "九蓮宝燈", "大四喜", "緑一色", 
                "字一色", "小四喜", "大七星"]

class PointCalculator:
    """Handles the strict math of converting Han and Fu into final points."""
    
    @staticmethod
    def calculate_base_points(han: int, fu: int) -> int:
        """Calculates the raw base points before applying dealer multipliers."""
        if han >= 13:
            # COMPOSITE YAKUMAN SCALING
            # If Han is 13 -> Multiplier is 1 (Base 8,000)
            # If Han is 26 -> Multiplier is 2 (Base 16,000)
            # If Han is 39 -> Multiplier is 3 (Base 24,000)
            yakuman_multiplier = han // 13
            base_points = 8000 * yakuman_multiplier
            
        elif han >= 11:
            base_points = 6000  # Sanbaiman
        elif han >= 8:
            base_points = 4000  # Baiman
        elif han >= 6:
            base_points = 3000  # Haneman
        elif han == 5 or (han == 4 and fu >= 40) or (han == 3 and fu >= 70):
            base_points = 2000  # Mangan
        else:
            # Standard Formula for 1-4 Han
            base_points = fu * (2 ** (han + 2))
            if base_points > 2000:
                base_points = 2000 # Cap at Mangan
        
        return base_points

    @staticmethod
    def get_final_scores(han: int, fu: int, is_dealer: bool, is_tsumo: bool) -> dict:
        """Returns the exact point payouts, rounded up to the nearest 100."""
        base = PointCalculator.calculate_base_points(han, fu)
        
        # Helper to round up to nearest 100
        round_100 = lambda x: math.ceil(x / 100.0) * 100

        result = {
            "total": 0,
            "payout_dealer": 0,    # What the dealer pays (if Tsumo)
            "payout_non_dealer": 0 # What the non-dealer pays (if Tsumo)
        }

        if is_dealer:
            if is_tsumo:
                # Dealer Tsumo: All 3 non-dealers pay 2x base points
                payment = round_100(base * 2)
                result["payout_non_dealer"] = payment
                result["total"] = payment * 3
            else:
                # Dealer Ron: Discarder pays 6x base points
                result["total"] = round_100(base * 6)
        else: # Non-dealer win
            if is_tsumo:
                # Non-dealer Tsumo: Dealer pays 2x, other non-dealers pay 1x
                dealer_pays = round_100(base * 2)
                non_dealer_pays = round_100(base)
                result["payout_dealer"] = dealer_pays
                result["payout_non_dealer"] = non_dealer_pays
                result["total"] = dealer_pays + (non_dealer_pays * 2)
            else:
                # Non-dealer Ron: Discarder pays 4x base points
                result["total"] = round_100(base * 4)

        return result


class YakuEvaluator:
    """Evaluates the structural conditions of the hand to find Yaku and Fu."""
    
    def __init__(self, tiles: list[str], division: list[list[str]], conditions: dict):
        self.tiles = tiles
        self.division = division
        self.conditions = conditions # e.g. {"riichi": True, "tsumo": False}
        self.is_open = conditions.get("is_open", False)

    def calculate_fu(self) -> int:
        
        # 1. Chiitoitsu (Seven Pairs) Exception
        # Seven Pairs is strictly fixed at 25 Fu by the rules of Riichi.
        if len(self.division) == 7:
            return 25

        fu = 20 # Base Fu for all hands
        
        # 2. Win Condition Fu
        win_fu = 0
        if not self.is_open and not self.conditions.get("tsumo"):
            win_fu = 10  # Menzen Ron (Closed hand, won by Ron)
        elif self.conditions.get("tsumo"):
            win_fu = 2   # Tsumo (Drawing your own winning tile)

        # 3. Melds (Ankou, Pon, Minkan, Ankan)
        meld_fu = 0
        raw_open = self.conditions.get("open_melds", [])
        
        for item in self.division:
            # Look for Triplets or Quads
            if len(item) >= 3 and item[0] == item[1] == item[2]:
                tile = item[0]
                
                # Check if the tile is a Terminal (1 or 9) or Honor (Winds/Dragons 'z')
                is_terminal_honor = (tile[0] in ['1', '9'] or 'z' in tile)
                
                # Base Value: 2 for Simples, 4 for Terminals/Honors
                base_val = 4 if is_terminal_honor else 2
                
                is_quad = (len(item) == 4)
                
                # --- Open vs Closed Detection ---
                # This uses Python's list equality. If they called an Open Pon, 
                # ['1m', '1m', '1m'] will exactly match an item in raw_open.
                is_open = False
                if is_quad:
                    if item in raw_open:  
                        is_open = True # Minkan
                    # NOTE: If it is an Ankan, raw_open contains 'ankan' as the 4th item.
                    # Therefore, ['1m', '1m', '1m', '1m'] in raw_open is mathematically False!
                    # It perfectly defaults to a Closed Kan!
                else:
                    if item in raw_open:  
                        is_open = True # Pon
                        
                # --- Apply Multipliers ---
                multiplier = 1
                if not is_open: 
                    multiplier *= 2  # Closed shapes (Ankou/Ankan) are worth 2x
                if is_quad: 
                    multiplier *= 4  # Kans are worth 4x
                
                meld_fu += (base_val * multiplier)

        # 4. Pair (Yakuhai) Fu
        pair_fu = 0
        
        # If your UI doesn't send these yet, we safely default them to East ('1z')
        seat_wind = self.conditions.get("seat_wind", "1z") 
        round_wind = self.conditions.get("round_wind", "1z")
        
        for item in self.division:
            if len(item) == 2:
                tile = item[0]
                # Dragons (+2 Fu)
                if tile in ['5z', '6z', '7z']:
                    pair_fu += 2
                # Seat Wind (+2 Fu)
                if tile == seat_wind:
                    pair_fu += 2
                # Round Wind (+2 Fu)
                if tile == round_wind:
                    pair_fu += 2
                # (Note: If Seat Wind AND Round Wind are the same, it safely adds +4 Fu!)

        # 5. Wait Fu (Penchan, Kanchan, Tanki)
        wait_fu = 0
        # NOTE: To calculate exact Wait Fu, the engine must know exactly which tile was 
        # the "Winning Tile" (the one drawn or called to finish the hand). 
        # Because we haven't built a Winning Tile selector in the UI yet, 
        # we are keeping Wait Fu at 0 to prevent mathematically false positives.

        # Calculate the pre-rounded total
        total_fu = fu + win_fu + meld_fu + pair_fu + wait_fu

        # 6. Pinfu Exceptions & Rounding
        # Pinfu Tsumo Exception: If you have no bonus Fu, Pinfu waives the 2 Tsumo Fu to stay at 20.
        if meld_fu == 0 and pair_fu == 0 and wait_fu == 0:
            if not self.is_open and self.conditions.get("tsumo"):
                return 20

        # Standard Rounding: Always round UP to the nearest 10
        rounded_fu = int(math.ceil(total_fu / 10.0)) * 10
        
        # Open Pinfu Exception: Open hands that round to 20 Fu are universally bumped to 30 Fu.
        if self.is_open and rounded_fu == 20:
            return 30
            
        return rounded_fu

    def evaluate_yaku(self) -> tuple[int, list[str]]:
        """Checks the hand against all Yaku rules."""
        yaku_list = []
        han = 0
        
        # 1. Riichi (1 Han) - Must be closed
        if self.conditions.get("riichi") and not self.is_open:
            yaku_list.append("立直")
            han += 1

        # closed hand tsumo
        if not self.is_open and self.conditions.get("tsumo", False):
            yaku_list.append("門前清自摸和")
            han += 1

        # 2. Tanyao / All Simples (1 Han)
        # Check if the hand contains ANY 1s, 9s, or Honors (z)
        terminals_honors = ["1m","9m","1p","9p","1s","9s","1z","2z","3z","4z","5z","6z","7z"]
        is_tanyao = not any(tile in self.tiles for tile in terminals_honors)
        if is_tanyao:
            yaku_list.append("断幺九")
            han += 1

        # 3. Yakuhai / Value Dragons (1 Han per set)
        dragons = {"5z":"白", "6z":"發", "7z":"中"}
        for d, output_yaku in dragons.items():
            if self.tiles.count(d) >= 3:
                yaku_list.append(f"{output_yaku}")
                han += 1

        # 4. Pinhu
        if not self.is_open and len(self.division) == 5:
            sequence_count = 0
            pair_tile = None
            
            for meld in self.division:
                # Sequence check (3 unique tiles)
                if len(meld) == 3 and len(set(meld)) == 3:
                    sequence_count += 1
                # Pair check (2 identical tiles)
                elif len(meld) == 2:
                    pair_tile = meld[0]
                    
            if sequence_count == 4 and pair_tile:
                
                # 3. Verify the pair is "Valueless"
                # Dragons are always value. '1z' (East) is assumed value for Round Wind.
                invalid_pairs = ['5z', '6z', '7z', '1z']
                
                # If the player is NOT the dealer, their seat wind would normally 
                # be South, West, or North. For a perfect engine, you would add their
                # specific seat wind to the invalid_pairs list here!
                
                if pair_tile not in invalid_pairs:
                    # Note: Assumes the two-sided wait requirement is met structurally.
                    yaku_list.append("平和")
                    han += 1

        # 5. Honitsu (Half Flush) & Chinitsu (Full Flush)
        # Create a set of all unique suits in the hand
        suits_present = set(tile[1] for tile in self.tiles)

        # Honitsu: Exactly 2 types of tiles, and one of them MUST be 'z'
        if len(suits_present) == 2 and 'z' in suits_present:
            yaku_list.append("混一色")
            han += 2 if self.is_open else 3

        # Chinitsu: Exactly 1 type of tile, and it is NOT 'z'
        elif len(suits_present) == 1 and 'z' not in suits_present:
            yaku_list.append("清一色")
            han += 5 if self.is_open else 6

        # 6. chiitoitsu
        if len(self.division) == 7:
            # Chiitoitsu is strictly a closed hand Yaku (2 Han).
            if not self.is_open: 
                yaku_list.append("七対子")
                han += 2
                
        # -----------------------------------------
        # Toitoi, Sanankou, & Suuankou
        # -----------------------------------------
        if len(self.division) == 5:
            triplet_count = 0
            
            # 1. Count ALL triplets and Kans in the final merged shape
            for item in self.division:
                if len(item) >= 3 and item[0] == item[1] == item[2]:
                    triplet_count += 1
            
            # 2. Count ONLY the explicitly called open triplets (Pon and Minkan)
            raw_open_melds = self.conditions.get("open_melds", [])
            open_triplet_count = 0
            
            for meld in raw_open_melds:
                # If it's a Pon/Minkan, it's open. 
                # If it has the "ankan" tag, it's a Closed Kan, so we IGNORE it here!
                if len(meld) >= 3 and meld[0] == meld[1] == meld[2] and "ankan" not in meld:
                    open_triplet_count += 1
                    
            # 3. The Math: Total Triplets - Called Triplets = Concealed Triplets
            concealed_triplets = triplet_count - open_triplet_count

            # 4. Apply the Yaku
            # Suuankou (Four Concealed Triplets -> Yakuman)
            if concealed_triplets == 4:
                yaku_list.append("四暗刻")
                han += 13
                
            else:
                # Toitoi (All Triplets -> 2 Han)    
                if triplet_count == 4:
                    yaku_list.append("対々")
                    han += 2
                    
                # Sanankou (Three Concealed Triplets -> 2 Han)
                if concealed_triplets == 3:
                    yaku_list.append("三暗刻")
                    han += 2

        kan_count = 0
        
        for item in self.division:
            # A Kan is explicitly a 4-tile meld where all tiles are identical
            if len(item) == 4 and len(set(item)) == 1:
                kan_count += 1

        # Apply the Yaku
        if kan_count == 4:
            yaku_list.append("四槓子")
            han += 13
        elif kan_count == 3:
            yaku_list.append("三槓子")
            han += 2


        # 7. Ryanpeikou & Iipeikou
        if not self.is_open and len(self.division) == 5:
            sequences = []
            for meld in self.division:
                # A sequence has 3 tiles, and all 3 must be unique (unlike a triplet)
                if len(meld) == 3 and len(set(meld)) == 3:
                    # CRITICAL FIX: Sort the meld before making it a tuple!
                    # This guarantees ['2m', '3m', '4m'] matches ['3m', '2m', '4m']
                    sequences.append(tuple(sorted(meld)))
            
            seq_counts = {}
            for seq in sequences:
                seq_counts[seq] = seq_counts.get(seq, 0) + 1
                
            identical_pairs = 0
            for count in seq_counts.values():
                identical_pairs += count // 2 

            if identical_pairs == 2:
                yaku_list.append("二盃口")
                han += 3
            elif identical_pairs == 1:
                yaku_list.append("一盃口")
                han += 1

        # 8. Junchan & Chanta
        if len(self.division) == 5:
            is_chanta = True
            is_junchan = True
            has_sequence = False
            
            for meld in self.division:
                # Check if the meld is a sequence (e.g., ['1m', '2m', '3m'])
                if len(meld) == 3 and len(set(meld)) == 3:
                    has_sequence = True
                
                has_terminal = any(tile[0] in ['1', '9'] for tile in meld)
                has_honor = any('z' in tile for tile in meld)
                
                has_yaochu = has_terminal or has_honor
                
                if not has_yaochu:
                    is_chanta = False
                    

                if not has_terminal or has_honor:
                    is_junchan = False

            if has_sequence:
                if is_junchan:
                    yaku_list.append("純全帯么九")
                    han += 2 if self.is_open else 3
                elif is_chanta:
                    yaku_list.append("全帯幺九")
                    han += 1 if self.is_open else 2

        # 9. Chinroutou & Honroutou
        is_chinroutou = True
        is_honroutou = True
        
        for tile in self.tiles:
            is_terminal = tile[0] in ['1', '9']
            is_honor = 'z' in tile
            
            # If we find any middle tile (2 through 8), both Yaku are immediately dead.
            if not is_terminal and not is_honor:
                is_honroutou = False
                is_chinroutou = False
                break 

            if is_honor:
                is_chinroutou = False

        if is_chinroutou:
            yaku_list.append("清老頭")
            han += 13
        elif is_honroutou:
            yaku_list.append("混老頭")
            han += 2

        # 10. Sanshoku
        if len(self.division) == 5:
            seq_starts = {} 
            triplet_nums = {} 

            for meld in self.division:
                
                # Check for Sequences
                if len(meld) == 3 and len(set(meld)) == 3:
                    # Sort it to guarantee ['1m', '2m', '3m'] order
                    sorted_meld = sorted(meld)
                    
                    val = sorted_meld[0][0]  # The number (e.g., '1')
                    suit = sorted_meld[0][1] # The suit (e.g., 'm')
                    
                    if suit in ['m', 'p', 's']:
                        if val not in seq_starts:
                            seq_starts[val] = set()
                        seq_starts[val].add(suit)

                # Check for Triplets / Quads
                elif len(meld) >= 3 and len(set(meld)) == 1:
                    val = meld[0][0]  # The number
                    suit = meld[0][1] # The suit
                    
                    if suit in ['m', 'p', 's']:
                        if val not in triplet_nums:
                            triplet_nums[val] = set()
                        triplet_nums[val].add(suit)

            has_doujun = any(len(suits) == 3 for suits in seq_starts.values())
            if has_doujun:
                yaku_list.append("三色同順")
                han += 1 if self.is_open else 2

            has_doukou = any(len(suits) == 3 for suits in triplet_nums.values())
            if has_doukou:
                yaku_list.append("三色同刻")
                han += 2

        # -----------------------------------------
        # NEW: Ittsu (Ikkitsukan / Pure Straight)
        # -----------------------------------------
        if len(self.division) == 5:
            # 1. Collect all valid sequences into a list of tuples
            sequences = []
            for meld in self.division:
                if len(meld) == 3 and len(set(meld)) == 3:
                    # Sort to guarantee order (e.g., '1m', '2m', '3m')
                    sequences.append(tuple(sorted(meld)))

            # 2. Check each suit to see if the full straight exists
            for suit in ['m', 'p', 's']:
                seq1 = (f'1{suit}', f'2{suit}', f'3{suit}')
                seq2 = (f'4{suit}', f'5{suit}', f'6{suit}')
                seq3 = (f'7{suit}', f'8{suit}', f'9{suit}')
                
                # If ALL THREE sequences exist in the collected sequences list
                if seq1 in sequences and seq2 in sequences and seq3 in sequences:
                    yaku_list.append("一気通貫")
                    han += 1 if self.is_open else 2
                    break # We found it, stop checking other suits!

        if len(self.division) == 5:
            dragon_triplets = 0
            dragon_pair = False
            
            # The dragon tiles: White (5z), Green (6z), Red (7z)
            dragons = ['5z', '6z', '7z']
            
            for item in self.division:
                # Check for a Dragon Triplet or Kan
                if len(item) >= 3 and item[0] == item[1] == item[2] and item[0] in dragons:
                    dragon_triplets += 1
                
                # Check for a Dragon Pair
                elif len(item) == 2 and item[0] == item[1] and item[0] in dragons:
                    dragon_pair = True

            # Apply the Yaku
            if dragon_triplets == 3:
                yaku_list.append("大三元")
                han += 13
            elif dragon_triplets == 2 and dragon_pair:
                yaku_list.append("小三元")
                han += 2

        # =========================================
        # YAKUMAN MASTER BLOCK
        # =========================================

        # -----------------------------------------
        # 1. Kokushi Musou (Thirteen Orphans)
        # -----------------------------------------
        # Our special 1-block shape from the Hand Divider
        if len(self.division) == 1 and not self.is_open:
            yaku_list.append("国士無双")
            han += 13

        # -----------------------------------------
        # 2. Chuuren Poutou (Nine Gates)
        # -----------------------------------------
        if not self.is_open:
            # Check if every single tile is the exact same suit
            suits = [t[1] for t in self.tiles]
            if len(set(suits)) == 1 and suits[0] in ['m', 'p', 's']:
                
                # Extract just the numbers
                vals = [t[0] for t in self.tiles]
                
                # The mathematical requirement for Nine Gates
                # (At least three 1s, at least three 9s, and at least one of everything else)
                reqs = {'1':3, '2':1, '3':1, '4':1, '5':1, '6':1, '7':1, '8':1, '9':3}
                
                # Python's all() beautifully checks if every requirement is met
                if all(vals.count(num) >= min_count for num, min_count in reqs.items()):
                    yaku_list.append("九蓮宝燈")
                    han += 13

        # -----------------------------------------
        # 3. Shousuushii & Daisuushii (The Four Winds)
        # -----------------------------------------
        if len(self.division) == 5:
            wind_triplets = 0
            wind_pair = False
            winds = ['1z', '2z', '3z', '4z'] # East, South, West, North
            
            for item in self.division:
                # Is it a Triplet/Kan of a Wind?
                if len(item) >= 3 and item[0] == item[1] == item[2] and item[0] in winds:
                    wind_triplets += 1
                # Is it the Pair of a Wind?
                elif len(item) == 2 and item[0] == item[1] and item[0] in winds:
                    wind_pair = True

            if wind_triplets == 4:
                yaku_list.append("大四喜")
                han += 13 
                # (Note: In some rule sets this is a Double Yakuman worth 26 Han!)
            elif wind_triplets == 3 and wind_pair:
                yaku_list.append("小四喜")
                han += 13
        # -----------------------------------------
        # 4. Ryuuiisou (All Green)
        # -----------------------------------------
        # Only tiles that use exclusively green ink: 2s, 3s, 4s, 6s, 8s, and Green Dragon (6z)
        green_tiles = ['2s', '3s', '4s', '6s', '8s', '6z']
        
        if all(t in green_tiles for t in self.tiles):
            yaku_list.append("緑一色")
            han += 13

        # -----------------------------------------
        # 5. Tsuuiisou (All Honors) & Daichisei
        # -----------------------------------------
        honor_tiles = ['1z', '2z', '3z', '4z', '5z', '6z', '7z']
        
        if all(t in honor_tiles for t in self.tiles):
            
            # The Special Case: 7 Pairs (Daichisei / Great Seven Stars)
            # If the division is 7 pairs, and there are exactly 7 unique tiles, 
            # it mathematically guarantees one pair of every single honor tile!
            if len(self.division) == 7 and len(set(self.tiles)) == 7:
                yaku_list.append("大七星")
                han += 13
            else:
                # Standard All Honors (4 melds and a pair)
                yaku_list.append("字一色")
                han += 13
            
        yakumans_achieved = [y for y in yaku_list if y in YAKUMAN_LIST]
        
        if yakumans_achieved:
            # 1. Discard all regular Yaku and keep ONLY the Yakumans
            yaku_list = yakumans_achieved
            
            # 2. Recalculate Han purely based on the number of Yakumans!
            # (1 Yakuman = 13 Han, 2 Yakumans = 26 Han, 3 Yakumans = 39 Han)
            han = len(yakumans_achieved) * 13
            
            # 3. Immediately return. We intentionally bypass Dora counting!
            return han, yaku_list
        
        
        if han == 0:
            return 0, []

        # Add Dora (1 Han each, doesn't count as a Yaku on its own)
        dora_count = 0
        indicators = self.conditions.get("dora_indicators", [])

        # For every indicator in the UI...
        for ind in indicators:
            # 1. Figure out what the actual Dora tile is
            actual_dora = get_dora_from_indicator(ind)
            
            # 2. Count exactly how many of that tile are in the raw hand
            dora_count += self.tiles.count(actual_dora)
        

        # Apply the total Dora han
        if dora_count > 0:
            yaku_list.append(f"ドラ {dora_count}")
            han += dora_count

        return han, yaku_list



class MahjongEngine:
    
    def calculate_score(self, closed_tiles: list[str], open_melds: list[list[str]], conditions: dict) -> dict:
        

        conditions["open_melds"] = open_melds
        # 1. Sanitize the Open Melds (Fixing the Ankan placeholder)
        # We must convert ["1m", "1m", "1m", "ankan"] into a true 4-tile list 
        # so string checks like tile[0] don't crash in your Yaku Evaluator!
        clean_open_melds = []
        for meld in open_melds:
            if "ankan" in meld:
                tile = meld[0]
                clean_open_melds.append([tile, tile, tile, tile])
            else:
                clean_open_melds.append(meld)

        # 2. Build a flat list of ALL tiles for raw checks (like Dora, Chinroutou, etc.)
        all_tiles = closed_tiles.copy()
        for meld in clean_open_melds:
            all_tiles.extend(meld)

        # 3. Divide ONLY the closed tiles!
        # If you have 1 open meld and 11 closed tiles, this perfectly handles the 11 tiles.
        closed_divisions = HandDivider.divide_hand(closed_tiles)
        
        if not closed_divisions:
            return {"error": "❌ 冲合！！！"}

        best_han = -1
        best_fu = -1
        best_yaku = []

        # 4. THE TAKAME LOOP
        for closed_div in closed_divisions:
            
            # --- THE MAGIC MERGE ---
            # Combine the backtracker's closed shape with the locked open shapes
            full_division = closed_div + clean_open_melds
            
            # Ensure the hand exactly equals 5 blocks (or 7 pairs for Chiitoitsu)
            if len(full_division) not in [5, 7, 1]:
                continue
            
            # Evaluate this specific merged shape
            evaluator = YakuEvaluator(all_tiles, full_division, conditions)
            han, yaku_list = evaluator.evaluate_yaku()
            fu = evaluator.calculate_fu()
            
            # Score metric (Han is king, Fu breaks ties)
            score_metric = (han * 1000) + fu 
            current_best_metric = (best_han * 1000) + best_fu
            
            if score_metric > current_best_metric:
                best_han = han
                best_fu = fu
                best_yaku = yaku_list

        # 5. Final Validation
        if best_han <= 0:
            return {"error": "❌ 役無し！！！"}

        # 6. Calculate Final Points
        # Note: Swap PointCalculator to however your engine calculates total_score!
        payouts = PointCalculator.get_final_scores(best_han, best_fu, conditions.get("is_dealer", False), conditions.get("tsumo", False))

        return {
            "han": best_han,
            "fu": best_fu,
            "yaku": best_yaku,
            "total_score": payouts["total"],
            "payout_dealer": payouts["payout_dealer"],
            "payout_non_dealer": payouts["payout_non_dealer"]
        }
    


def get_dora_from_indicator(indicator: str) -> str:
    """Takes a Dora indicator and returns the actual Dora tile."""
    val = int(indicator[0])
    suit = indicator[1]

    # Numbered suits (Manzu, Pinzu, Souzu) loop 1-9
    if suit in ['m', 'p', 's']:
        new_val = val + 1 if val < 9 else 1
        return f"{new_val}{suit}"
    
    # Honor suits (Zihai) loop within Winds (1-4) and Dragons (5-7)
    elif suit == 'z':
        if val <= 4: # Winds: Ton(1)->Nan(2)->Shaa(3)->Pei(4)->Ton(1)
            new_val = val + 1 if val < 4 else 1
            return f"{new_val}z"
        else:        # Dragons: Haku(5)->Hatsu(6)->Chun(7)->Haku(5)
            new_val = val + 1 if val < 7 else 5
            return f"{new_val}z"