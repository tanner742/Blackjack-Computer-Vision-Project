def recommend_action(
    player_cards,
    dealer_upcard,
    running_count=0,
    decks_remaining=1,
    can_double=True,
    can_surrender=True
):
    """
    player_cards: [int, int]   (1=Ace, 2-10)
    dealer_upcard: int (1=Ace, 2-10)
    running_count: current Hi-Lo running count
    decks_remaining: number of remaining decks
    can_double: whether doubling is allowed
    can_surrender: whether surrender is allowed
    """
    #True count for this model
    tc = running_count / max(decks_remaining, 0.25)
    
    
    #Detects hand type
    card1, card2 = player_cards
    total = sum(player_cards)
    is_pair = (card1 == card2)
    is_soft = (1 in player_cards and total + 10 <= 21)
    if is_soft:
        total += 10

    dealer = dealer_upcard

    #Insurance Deviation 
    if dealer == 1:
        if tc >= 3:
            insurance = "TAKE_INSURANCE"
        else:
            insurance = "NO_INSURANCE"
    else:
        insurance = "NO_INSURANCE"

    
    
    #FAB 4 implementation
    if can_surrender and total == 15 and dealer == 10:
        if tc < 0:
            return "SURRENDER", insurance
        else:
            return "STAND", insurance

    if can_surrender and total == 15 and dealer == 9:
        if tc < 2:
            return "SURRENDER", insurance
        else:
            return "STAND", insurance

    if can_surrender and total == 15 and dealer == 1:
        if tc < 2:
            return "SURRENDER", insurance
        else:
            return "STAND", insurance

    if can_surrender and total == 14 and dealer == 10:
        if tc < 3:
            return "SURRENDER", insurance
        else:
            return "STAND", insurance
        
    #Illustious 18 Deviations following a large enough true count
    if total == 16 and dealer == 10 and tc >= 0:
        return "STAND", insurance

    # Stand 15 vs 10 at TC >= 4
    if total == 15 and dealer == 10 and tc >= 4:
        return "STAND", insurance

    # 10 vs 10 double at TC >= 4
    if total == 10 and dealer == 10 and tc >= 4 and can_double:
        return "DOUBLE", insurance

    # 12 vs 3 stand at TC >= 2
    if total == 12 and dealer == 3 and tc >= 2:
        return "STAND", insurance

    # 12 vs 2 stand at TC >= 3
    if total == 12 and dealer == 2 and tc >= 3:
        return "STAND", insurance

    # 11 vs A double at TC >= 1
    if total == 11 and dealer == 1 and tc >= 1 and can_double:
        return "DOUBLE", insurance

    # 9 vs 2 double at TC >= 1
    if total == 9 and dealer == 2 and tc >= 1 and can_double:
        return "DOUBLE", insurance

    # 10 vs A double at TC >= 4
    if total == 10 and dealer == 1 and tc >= 4 and can_double:
        return "DOUBLE", insurance

    # 9 vs 7 double at TC >= 3
    if total == 9 and dealer == 7 and tc >= 3 and can_double:
        return "DOUBLE", insurance

    # 16 vs 9 stand at TC >= 5
    if total == 16 and dealer == 9 and tc >= 5:
        return "STAND", insurance

    # 13 vs 2 stand at TC >= -1
    if total == 13 and dealer == 2 and tc >= -1:
        return "STAND", insurance

    # 12 vs 4 stand at TC >= 0
    if total == 12 and dealer == 4 and tc >= 0:
        return "STAND", insurance

    # 12 vs 5 stand at TC >= -2
    if total == 12 and dealer == 5 and tc >= -2:
        return "STAND", insurance

    # 12 vs 6 stand at TC >= -1
    if total == 12 and dealer == 6 and tc >= -1:
        return "STAND", insurance

    # 13 vs 3 stand at TC >= -2
    if total == 13 and dealer == 3 and tc >= -2:
        return "STAND", insurance

    # 15 vs 9 stand at TC >= 5
    if total == 15 and dealer == 9 and tc >= 5:
        return "STAND", insurance

    # 15 vs A stand at TC >= 5
    if total == 15 and dealer == 1 and tc >= 5:
        return "STAND", insurance

    # 14 vs 10 stand at TC >= 3
    if total == 14 and dealer == 10 and tc >= 3:
        return "STAND", insurance



    #Pair Splits
    if is_pair:
        pair = card1

        if pair == 1 or pair == 8:
            return "SPLIT", insurance

        if pair == 9:
            return ("SPLIT" if dealer not in [7, 10, 1] else "STAND"), insurance

        if pair == 7:
            return ("SPLIT" if dealer <= 7 else "HIT"), insurance

        if pair == 6:
            return ("SPLIT" if dealer <= 6 else "HIT"), insurance

        if pair == 4:
            return ("SPLIT" if dealer in [5, 6] else "HIT"), insurance

        if pair in [2, 3]:
            return ("SPLIT" if dealer <= 7 else "HIT"), insurance
        
    #Soft totals
    if is_soft:
        if total <= 17:
            if dealer in [4, 5, 6] and can_double:
                return "DOUBLE", insurance
            return "HIT", insurance

        if total == 18:
            if dealer in [3, 4, 5, 6] and can_double:
                return "DOUBLE", insurance
            if dealer in [9, 10, 1]:
                return "HIT", insurance
            return "STAND", insurance

        if total >= 19:
            return "STAND", insurance

    #Hard totals
    if total <= 8:
        return "HIT", insurance

    if total == 9:
        if dealer in [3, 4, 5, 6] and can_double:
            return "DOUBLE", insurance
        return "HIT", insurance

    if total == 10:
        if dealer in range(2, 10) and can_double:
            return "DOUBLE", insurance
        return "HIT", insurance

    if total == 11:
        if can_double:
            return "DOUBLE", insurance
        return "HIT", insurance

    if total == 12:
        return ("STAND" if dealer in [4, 5, 6] else "HIT"), insurance

    if 13 <= total <= 16:
        return ("STAND" if dealer <= 6 else "HIT"), insurance

    if total >= 17:
        return "STAND", insurance

    return "HIT", insurance
