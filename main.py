import cv2
import numpy as np
import mss
from ultralytics import YOLO

#Strategy logic located in theory.py to keep vision and decision logic seperate
from theory import recommend_action

HI_LO_MAP = {
    "2": +1, "3": +1, "4": +1, "5": +1, "6": +1,
    "7": 0, "8": 0, "9": 0,
    "10": -1, "J": -1, "Q": -1, "K": -1, "A": -1
}

def label_to_rank(label: str) -> str:
    if label in HI_LO_MAP:
        return label
    return label[:-1]

def rank_to_theory_int(rank: str) -> int:
    if rank == "A":
        return 1
    if rank in ["J", "Q", "K", "10"]:
        return 10
    return int(rank)

def rank_to_value(rank: str) -> int:
    if rank in ["J", "Q", "K", "10"]:
        return 10
    if rank == "A":
        return 11
    return int(rank)

def hand_total(card_set) -> int:
    ranks = [label_to_rank(c) for c in card_set]
    values = [rank_to_value(r) for r in ranks]
    total = sum(values)
    aces = ranks.count("A")
    while total > 21 and aces > 0:
        total -= 10
        aces -= 1
    return total

class CardTracker:
    def __init__(self, frames_required=60):
        self.frames_required = frames_required
        self.counts = {}
        self.confirmed_cards = set()

    def reset(self):
        self.counts.clear()
        self.confirmed_cards.clear()

    def update(self, detected_labels, other_confirmed_ranks=None):
        other_confirmed_ranks = other_confirmed_ranks or set()

        for label in detected_labels:
            self.counts[label] = self.counts.get(label, 0) + 1

            if self.counts[label] >= self.frames_required:
                rank = label_to_rank(label)
                #Prevent double-counting across player and dealer regions
                if rank in other_confirmed_ranks:
                    self.counts[label] = 0
                else:
                    self.confirmed_cards.add(label)
                    self.counts[label] = 0

        for label in list(self.counts.keys()):
            if label not in detected_labels:
                self.counts[label] = 0

        return self.confirmed_cards

def bet_recommendation(running_count, base_bet=10):
    if running_count <= 0:
        return base_bet
    if running_count == 1:
        return base_bet * 2
    if running_count == 2:
        return base_bet * 3
    if running_count == 3:
        return base_bet * 4
    return base_bet * 5

def draw_hud(img, lines, *, bar_h=90, pad=10, alpha=0.55):
    h, w = img.shape[:2]
    y0 = max(0, h - bar_h)

    overlay = img.copy()
    cv2.rectangle(overlay, (0, y0), (w, h), (0, 0, 0), -1)
    img[:] = cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0)

    y = y0 + pad + 18
    for line in lines:
        cv2.putText(
            img, line, (pad, y),
            cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2, cv2.LINE_AA
        )
        y += 22

    return img

def hi_lo_delta(cards) -> int:
    delta = 0
    for card in cards:
        rank = label_to_rank(card)
        delta += HI_LO_MAP.get(rank, 0)
    return delta

def pick_dealer_upcard_int(confirmed_dealer_cards):
    if not confirmed_dealer_cards:
        return None
    chosen_label = sorted(list(confirmed_dealer_cards))[0]
    chosen_rank = label_to_rank(chosen_label)
    return rank_to_theory_int(chosen_rank)

def get_player_cards_ints(confirmed_player_cards):
    if len(confirmed_player_cards) < 2:
        return None
    chosen = sorted(list(confirmed_player_cards))[:2]
    return [rank_to_theory_int(label_to_rank(c)) for c in chosen]

def stream_screen():
    model_path = r"C:\Users\buckt\OneDrive\Desktop\Card_Counts\runs\detect\card_detector_finetune_small_cards4\weights\best.pt"
    model = YOLO(model_path)

    WINDOW_NAME = "Player Detection"
    DISPLAY_SCALE = 1.6  #Can make larger to fit prefrence; larger will not affect performance 


    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)

    with mss.mss() as sct:
        #Assumes that monitor is on the left
        monitor = sct.monitors[2]

        img = np.array(sct.grab(monitor))
        frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

        dealer_roi = cv2.selectROI("Select DEALER Area", frame, showCrosshair=True)
        player_roi = cv2.selectROI("Select PLAYER Area", frame, showCrosshair=True)
        cv2.destroyAllWindows()

        dx, dy, dw, dh = map(int, dealer_roi)
        px, py, pw, ph = map(int, player_roi)

        dealer_region = {
            "top": monitor["top"] + dy,
            "left": monitor["left"] + dx,
            "width": dw,
            "height": dh
        }
        player_region = {
            "top": monitor["top"] + py,
            "left": monitor["left"] + px,
            "width": pw,
            "height": ph
        }

        dealer_tracker = CardTracker(frames_required=45)
        player_tracker = CardTracker(frames_required=45)

        shoe_seen_cards = set()
        running_count = 0
        decks_in_shoe = 1  

        while True:
            dealer_img = np.array(sct.grab(dealer_region))
            player_img = np.array(sct.grab(player_region))

            dealer_frame = cv2.cvtColor(dealer_img, cv2.COLOR_BGRA2BGR)
            player_frame = cv2.cvtColor(player_img, cv2.COLOR_BGRA2BGR)

            dealer_results = model(dealer_frame, verbose=False)
            player_results = model(player_frame, verbose=False)

            dealer_labels = [r.names[int(box.cls)] for r in dealer_results for box in r.boxes]
            player_labels = [r.names[int(box.cls)] for r in player_results for box in r.boxes]

            confirmed_player = player_tracker.update(player_labels)
            player_confirmed_ranks = {label_to_rank(lbl) for lbl in confirmed_player}

            confirmed_dealer = dealer_tracker.update(
                dealer_labels,
                other_confirmed_ranks=player_confirmed_ranks
            )

            hand_confirmed = set(confirmed_player).union(set(confirmed_dealer))
            newly_seen = hand_confirmed - shoe_seen_cards
            if newly_seen:
                running_count += hi_lo_delta(newly_seen)
                shoe_seen_cards |= newly_seen

            bet = bet_recommendation(running_count)

            player_total = hand_total(confirmed_player)
            dealer_total = hand_total(confirmed_dealer)

            player_annot = player_results[0].plot()

            action_text = "Action: (need 2 player cards + dealer upcard)"
            insurance_text = ""

            player_cards_ints = get_player_cards_ints(confirmed_player)
            dealer_up_int = pick_dealer_upcard_int(confirmed_dealer)

            decks_remaining = max((decks_in_shoe * 52 - len(shoe_seen_cards)) / 52.0, 0.25)

            if player_cards_ints is not None and dealer_up_int is not None:
                try:
                    action, insurance = recommend_action(
                        player_cards=player_cards_ints,
                        dealer_upcard=dealer_up_int,
                        running_count=running_count,
                        decks_remaining=decks_remaining,
                        can_double=True,
                        can_surrender=True
                    )
                    action_text = f"Action: {action}"
                    insurance_text = f"Insurance: {insurance}"
                except Exception as e:
                    action_text = f"Action: (theory.py error: {type(e).__name__})"

            hud_lines = [
                f"P:{player_total}  D:{dealer_total}   RC:{running_count}   Bet:${bet}",
                action_text + (f"   |   {insurance_text}" if insurance_text else ""),
                "Keys: [q]=quit  [n]=new hand (keep RC)  [s]=new shoe (reset RC)"
            ]
            draw_hud(player_annot, hud_lines, bar_h=90)


            if DISPLAY_SCALE != 1.0:
                player_show = cv2.resize(
                    player_annot,
                    None,
                    fx=DISPLAY_SCALE,
                    fy=DISPLAY_SCALE,
                    interpolation=cv2.INTER_LINEAR
                )
            else:
                player_show = player_annot

            cv2.imshow(WINDOW_NAME, player_show)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('n'):
                dealer_tracker.reset()
                player_tracker.reset()
            elif key == ord('s'):
                dealer_tracker.reset()
                player_tracker.reset()
                shoe_seen_cards.clear()
                running_count = 0

        cv2.destroyAllWindows()

if __name__ == "__main__":
    stream_screen()
