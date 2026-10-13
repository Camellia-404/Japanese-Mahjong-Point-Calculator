import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QHBoxLayout
from PySide6.QtGui import QIcon, QPixmap, QPainter
from PySide6.QtCore import QSize, Qt

# 1. Import auto-generated UI
from ui.ui_main_window import Ui_Form 

# 2. Import Mahjong logic
from engine.calculator import MahjongEngine

# ==========================================
# CONSTANTS & MAPPINGS
# ==========================================

# Standard engine notation
TILE_NAMES = [
    '1m', '2m', '3m', '4m', '5m', '6m', '7m', '8m', '9m',
    '1p', '2p', '3p', '4p', '5p', '6p', '7p', '8p', '9p',
    '1s', '2s', '3s', '4s', '5s', '6s', '7s', '8s', '9s',
    '1z', '2z', '3z', '4z', '5z', '6z', '7z'
]

# Map engine notation to your actual image filenames
FILE_MAP = {
    '1m': 'Man1', '2m': 'Man2', '3m': 'Man3', '4m': 'Man4', '5m': 'Man5', '6m': 'Man6', '7m': 'Man7', '8m': 'Man8', '9m': 'Man9',
    '1p': 'Pin1', '2p': 'Pin2', '3p': 'Pin3', '4p': 'Pin4', '5p': 'Pin5', '6p': 'Pin6', '7p': 'Pin7', '8p': 'Pin8', '9p': 'Pin9',
    '1s': 'Sou1', '2s': 'Sou2', '3s': 'Sou3', '4s': 'Sou4', '5s': 'Sou5', '6s': 'Sou6', '7s': 'Sou7', '8s': 'Sou8', '9s': 'Sou9',
    '1z': 'Ton',  '2z': 'Nan',  '3z': 'Shaa', '4z': 'Pei',    
    '5z': 'Haku', '6z': 'Hatsu','7z': 'Chun'                  
}

# ==========================================
# MAIN APPLICATION CONTROLLER
# ==========================================
class MahjongCalculatorApp(QWidget, Ui_Form):
    def __init__(self):
        super().__init__()
        
        # Setup UI from Qt Designer
        self.setupUi(self)

        if self.frame_hand.layout() is None:
            self.frame_hand.setLayout(QHBoxLayout())
        if self.frame_dora.layout() is None:
            self.frame_dora.setLayout(QHBoxLayout())
        # Initialize Math Engine
        self.engine = MahjongEngine()
        
        # State Arrays
        self.current_doras = [] # Max 5 tiles
        self.closed_tiles = []  # e.g., ["1m", "2m", "3m"]
        self.open_melds = []    # List of lists e.g., [["5z", "5z", "5z"], ["1p", "2p", "3p"]]

        # Initialize the visual grid
        self.setup_tile_palette()
        
        # Connect the Calculate button
        self.btn_calculate.clicked.connect(self.run_calculation)
        
        

    def create_composited_tile(self, front_path, symbol_path):
        """Merges a transparent tile symbol onto the blank front background."""
        # 1. Load the blank white background
        base_pixmap = QPixmap(front_path)
        
        # 2. Load the transparent symbol (e.g., Man1)
        overlay_pixmap = QPixmap(symbol_path)
        
        # Fallback: if the symbol image is missing, just return the blank tile
        if overlay_pixmap.isNull():
            return base_pixmap

        # 3. Use QPainter to draw the symbol directly onto the base image
        painter = QPainter(base_pixmap)
        # We draw it at x=0, y=0 assuming both images are the exact same pixel dimensions
        painter.drawPixmap(0, 0, overlay_pixmap)
        painter.end() # Always close the painter when done!
        
        return base_pixmap
    
    def setup_tile_palette(self):
        row = 0
        col = 0
        
        
        front_path = os.path.join(BASE_DIR, "assets", "tiles", "Front.png") 
        
        for tile_str in TILE_NAMES:
            btn = QPushButton()
            
            file_name = FILE_MAP[tile_str] 
            symbol_path = os.path.join(BASE_DIR, "assets", "tiles", f"{file_name}.png")

            # Check if both the background and the symbol exist
            if os.path.exists(front_path) and os.path.exists(symbol_path):
                # Call our new merging function
                merged_pixmap = self.create_composited_tile(front_path, symbol_path)
                btn.setIcon(QIcon(merged_pixmap))
                btn.setIconSize(QSize(40, 55)) 
            else:
                btn.setText(tile_str) 
                
            btn.setFixedSize(45, 60)
            btn.setCursor(Qt.PointingHandCursor)
            
            btn.clicked.connect(lambda checked, t=tile_str: self.on_palette_tile_clicked(t))
            self.frame_palette.layout().addWidget(btn, row, col)
            
            col += 1
            if col > 8: 
                col = 0
                row += 1

    def get_total_tile_count(self, target_tile: str) -> int:
        """Counts how many times a specific tile exists across the entire app state."""
        count = 0
        
        # 1. Count in closed hand
        count += self.closed_tiles.count(target_tile)
        
        # 2. Count in doras
        count += self.current_doras.count(target_tile)
        
        # 3. Count in open melds
        for meld in self.open_melds:
            if "ankan" in meld:
                # If this meld is an Ankan, check if the first tile matches our target.
                # If it does, we know physically ALL 4 tiles are consumed!
                if meld[0] == target_tile:
                    count += 4
            else:
                # Normal counting for Chi, Pon, and Open Kan 
                # (Open Kan is safely formatted as ["1m", "1m", "1m", "1m"] so .count() works perfectly)
                count += meld.count(target_tile)
                
        return count


    def on_palette_tile_clicked(self, tile_str: str):
        
        # --- THE VALIDATOR ---
        def can_add_tiles(target_tile: str, amount_to_add: int) -> bool:
            # Returns True if legal, returns False (silently doing nothing) if it exceeds 4
            return self.get_total_tile_count(target_tile) + amount_to_add <= 4
        # ---------------------

        # 1. Dora Selection
        if self.radio_dora.isChecked():
            if len(self.current_doras) < 5:
                if not can_add_tiles(tile_str, 1): return
                
                self.current_doras.append(tile_str)
                # Assuming you have TILE_NAMES defined somewhere for sorting, keep your existing sort:
                # self.current_doras.sort(key=lambda t: TILE_NAMES.index(t)) 
                self.update_visual_displays()
            return

        # 2. Chi (Sequence)
        if self.radio_chi.isChecked():
            val = tile_str[0]
            suit = tile_str[1]
            if suit in ['m', 'p', 's'] and val.isdigit() and int(val) <= 7:
                t2 = f"{int(val)+1}{suit}"
                t3 = f"{int(val)+2}{suit}"
                
                # We must verify ALL THREE tiles are legally available before committing!
                if not can_add_tiles(tile_str, 1): return
                if not can_add_tiles(t2, 1): return
                if not can_add_tiles(t3, 1): return
                
                self.open_melds.append([tile_str, t2, t3])
                
        # 3. Pon (Triplet)
        elif self.radio_pon.isChecked():
            if not can_add_tiles(tile_str, 3): return
            self.open_melds.append([tile_str, tile_str, tile_str])
            
        # 4. Open Kan (Quad)
        elif self.radio_minkan.isChecked():
            if not can_add_tiles(tile_str, 4): return
            self.open_melds.append([tile_str, tile_str, tile_str, tile_str])
            
        # 5. Closed Kan (Concealed Quad)
        elif self.radio_ankan.isChecked():
            if not can_add_tiles(tile_str, 4): return
            self.open_melds.append([tile_str, tile_str, tile_str, "ankan"]) 
            
        # 6. Stand / Closed Tile (立牌)
        elif self.radio_hand.isChecked():
            if not can_add_tiles(tile_str, 1): return
            
            self.closed_tiles.append(tile_str)
            self.closed_tiles.sort(key=lambda t: TILE_NAMES.index(t)) # Keep your existing sort

        self.update_visual_displays()


    def get_tile_pixmap(self, tile_str: str) -> QPixmap:
        """Composites a transparent symbol onto the Front.png tile background."""
        import os
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))

        # 1. Handle Face-Down Tiles (Closed Kan)
        if tile_str == "ankan":
            # Note the capital 'B' to match your screenshot!
            return QPixmap(os.path.join(BASE_DIR, "assets", "tiles", "Back.png"))

        # 2. Setup paths for Face-Up Tiles
        front_path = os.path.join(BASE_DIR, "assets", "tiles", "Front.png")
        symbol_path = os.path.join(BASE_DIR, "assets", "tiles", f"{FILE_MAP[tile_str]}.png")

        base_pixmap = QPixmap(front_path)
        symbol_pixmap = QPixmap(symbol_path)

        # 3. Create an empty canvas exactly the size of the Front tile
        result = QPixmap(base_pixmap.size())
        result.fill(Qt.transparent)

        # 4. Paint the layers together
        painter = QPainter(result)
        painter.drawPixmap(0, 0, base_pixmap)    # Draw the white 3D tile body first
        
        if not symbol_pixmap.isNull():
            painter.drawPixmap(0, 0, symbol_pixmap) # Draw the symbol on top
        else:
            print(f"❌ ERROR: Missing symbol image at {symbol_path}")
            
        painter.end() # Finish painting

        return result

    def update_visual_displays(self):
        self._clear_layout(self.frame_hand.layout())
        self._clear_layout(self.frame_dora.layout())
        self.frame_hand.layout().setSpacing(2)
        
        front_path = os.path.join(BASE_DIR, "assets", "tiles", "Front.png")

        for i, tile in enumerate(self.closed_tiles):
            lbl = QLabel()
            
            # --- THE NEW WAY ---
            # 1. Get the perfectly composited image
            combined_pixmap = self.get_tile_pixmap(tile)
            
            # 2. Scale it and set it
            # Added Qt.SmoothTransformation so the symbols don't get pixelated when shrunk!
            lbl.setPixmap(combined_pixmap.scaled(40, 55, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            # -------------------
            
            # Bind click event
            lbl.mousePressEvent = lambda event, g="closed", idx=i: self.remove_from_hand(g, idx)
            self.frame_hand.layout().addWidget(lbl)

        self.frame_hand.layout().addWidget(QLabel("  "))   
       
        # -----------------------------------------
        # 2. Draw Open Melds
        # -----------------------------------------
        for i, meld in enumerate(self.open_melds):
            
            if "ankan" in meld:
                # The underlying data is still ["1m", "1m", "1m", "ankan"]
                # But we tell the UI to draw it as: Back, Face, Face, Back
                actual_tile = meld[0] 
                visual_sequence = ["ankan", actual_tile, actual_tile, "ankan"]
            else:
                # Chi, Pon, and Minkan just draw their exact array
                visual_sequence = meld

            for tile in visual_sequence:
                lbl = QLabel()
                
                # 1. Get the perfectly composited image (handles "ankan" automatically!)
                combined_pixmap = self.get_tile_pixmap(tile)
                
                # 2. Scale it smoothly and set it
                lbl.setPixmap(combined_pixmap.scaled(40, 55, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                
                # 3. Bind the click event for removal
                # Because 'i' is the loop index of the meld, clicking ANY of the 
                # 4 rendered tiles will correctly delete the entire group!
                lbl.mousePressEvent = lambda event, g="open", idx=i: self.remove_from_hand(g, idx)
                self.frame_hand.layout().addWidget(lbl)
            
            # Add a small visual gap between different melds
            self.frame_hand.layout().addWidget(QLabel(" "))
        self.frame_hand.layout().addStretch()

        # -----------------------------------------
        # 3. Draw Doras
        # -----------------------------------------
        for i, tile in enumerate(self.current_doras):
            lbl = QLabel()
            
            # Use the exact same compositing logic for the Dora box
            combined_pixmap = self.get_tile_pixmap(tile)
            lbl.setPixmap(combined_pixmap.scaled(40, 55, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            
            # Bind the click event
            lbl.mousePressEvent = lambda event, g="dora", idx=i: self.remove_from_hand(g, idx)
            self.frame_dora.layout().addWidget(lbl)
        

    def _clear_layout(self, layout):
        """Safely removes all widgets from a QLayout."""
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()

    def remove_from_hand(self, target_group: str, target_index: int):
        """
        Removes items based on their structural grouping.
        """
        if target_group == "closed":
            # Remove the single closed tile
            self.closed_tiles.pop(target_index)
            
        elif target_group == "open":
            # target_index refers to the specific MELD list.
            # Popping it removes all 3 or 4 tiles simultaneously!
            self.open_melds.pop(target_index)
            
        elif target_group == "dora":
            self.current_doras.pop(target_index)

        # Redraw the UI
        self.update_visual_displays()
        
    def remove_from_dora(self, tile_str: str):
        self.current_doras.remove(tile_str)
        self.update_visual_displays()

    def run_calculation(self):
        """Gathers UI state and passes it to the math engine."""
        
        effective_tile_count = len(self.closed_tiles) + (len(self.open_melds) * 3)
        
        if effective_tile_count != 14:
            self.lbl_result.setText(f"❌ Error: Hand has {effective_tile_count} tiles. Need exactly 14.")
            return

        is_actually_open = any("ankan" not in meld for meld in self.open_melds)

        ui_conditions = {
            "is_dealer": self.chk_dealer.isChecked(),
            "tsumo": self.chk_tsumo.isChecked(),
            "riichi": self.chk_riichi.isChecked() and not is_actually_open,
            "is_open": is_actually_open, 
            "dora_indicators": self.current_doras 
        }

        result = self.engine.calculate_score(self.closed_tiles, self.open_melds, ui_conditions)

        # Display Results
        if "error" in result:
            self.lbl_result.setText(f"⚠️ {result['error']}")
        else:
            yaku_str = ", ".join(result['yaku'])
            
            output = (
                f"✅ 計算通り\n"
                f"{'-'*30}\n"
                f"点数: {result['total_score']} \n"
                f"{result['han']}翻{result['fu']}符\n"
                f"{yaku_str}\n\n"
            )
            
            # Determine payout text
            if ui_conditions["tsumo"]:
                if ui_conditions["is_dealer"]:
                    output += f"{result['payout_non_dealer']} ALL"
                else:
                    output += f"{result['payout_non_dealer']} (子) / {result['payout_dealer']} (親)"
            else:
                output += f"{result['total_score']}"

            self.lbl_result.setText(output)





if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Apply a modern dark theme style (optional, but looks good)
    app.setStyle("Fusion") 
    
    window = MahjongCalculatorApp()
    window.setWindowTitle("Riichi Mahjong Calculator")
    window.show()
    
    sys.exit(app.exec())