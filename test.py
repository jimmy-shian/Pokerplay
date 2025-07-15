# import random
# import itertools
# from collections import defaultdict, Counter

# class Player:
#     def __init__(self, name, strategy='min'):
#         self.name = name
#         self.cards = list(range(1, 13))
#         self.history = []
#         self.strategy = strategy

#     def has_cards(self):
#         return len(self.cards) > 0

#     def find_valid_combinations(self, dice_sum):
#         valid = []
#         for i in range(1, len(self.cards)+1):
#             for comb in itertools.combinations(self.cards, i):
#                 if sum(comb) == dice_sum:
#                     valid.append(comb)
#         return valid

#     def choose_best_combination(self, valid_combinations):
#         if not valid_combinations:
#             return None

#         if self.strategy == 'min':
#             return min(valid_combinations, key=lambda x: len(x))  # 原策略

#         elif self.strategy == 'max':
#             return max(valid_combinations, key=lambda x: len(x))  # 優先最多張

#         elif self.strategy == 'safe':
#             # 優先不包含1的組合
#             non_one = [c for c in valid_combinations if 1 not in c]
#             if non_one:
#                 return max(non_one, key=lambda x: len(x))
#             return min(valid_combinations, key=lambda x: len(x))  # 不得已用1

#         else:
#             raise ValueError("Unknown strategy")

#     def cover_cards(self, combination):
#         for c in combination:
#             self.cards.remove(c)

# def roll_dice(num_dice=2):
#     return sum(random.randint(1, 6) for _ in range(num_dice))

# def play_round(players, stats):
#     consecutive_pass = 0
#     current = 0
#     num_players = len(players)

#     while True:
#         player = players[current]
#         dice_num = 2 if len(player.cards) > 1 else 1
#         dice_sum = roll_dice(dice_num)
#         valid_combos = player.find_valid_combinations(dice_sum)
#         best = player.choose_best_combination(valid_combos)

#         if best:
#             player.cover_cards(best)
#             player.history.append((dice_sum, tuple(sorted(best))))
#             consecutive_pass = 0
#             if not player.has_cards():
#                 for ds, comb in player.history:
#                     stats['win_combos'][(ds, comb)] += 1
#                 return player
#         else:
#             consecutive_pass += 1
#             if consecutive_pass >= num_players:
#                 return None
#         current = (current + 1) % num_players

# def simulate_for_player_count(num_games, num_players, strategy):
#     stats = {'win_combos': Counter()}
#     for _ in range(num_games):
#         players = [Player(f"Player{i+1}", strategy=strategy) for i in range(num_players)]
#         play_round(players, stats)
#     return stats['win_combos']

# def compare_strategies(num_games=3000):
#     strategies = ['min', 'max', 'safe']
#     all_stats = {s: {} for s in strategies}

#     for strategy in strategies:
#         print(f"\n🔍 模擬策略: {strategy}")
#         for n in range(2, 5):
#             print(f"  模擬 {n} 人局...")
#             all_stats[strategy][n] = simulate_for_player_count(num_games, n, strategy)

#     # 整理所有出現的 (dice_sum, combination)
#     all_keys = set()
#     for strategy_stats in all_stats.values():
#         for player_data in strategy_stats.values():
#             all_keys.update(player_data.keys())

#     # 依照骰子和做分類
#     grouped_by_sum = defaultdict(list)
#     for key in all_keys:
#         dice_sum, combo = key
#         grouped_by_sum[dice_sum].append(combo)

#     # 顯示結果
#     print("\n📊【不同策略與人數下，勝利者常用蓋牌組合比較】")
#     for ds in range(2, 13):
#         if ds not in grouped_by_sum:
#             continue
#         print(f"\n🎲 骰子總和 {ds}")
#         combos = grouped_by_sum[ds]

#         # 每個策略下的頻率
#         for comb in sorted(combos):
#             line = f"  {comb}:"
#             for strategy in strategies:
#                 for players in range(2, 5):
#                     count = all_stats[strategy][players].get((ds, comb), 0)
#                     line += f" {strategy}-{players}人[{count}]"
#             print(line)

# if __name__ == "__main__":
#     compare_strategies(num_games=1000)

import random
import itertools
from collections import defaultdict, Counter

class Player:
    def __init__(self, name, strategy='min'):
        self.name = name
        self.strategy = strategy
        self.reset()

    def reset(self):
        self.cards = list(range(1, 13))
        self.history = []

    def has_cards(self):
        return bool(self.cards)

    def find_valid_combinations(self, dice_sum):
        valid = []
        for i in range(1, len(self.cards) + 1):
            for comb in itertools.combinations(self.cards, i):
                if sum(comb) == dice_sum:
                    valid.append(comb)
        return valid

    def choose_best_combination(self, valid_combinations):
        if not valid_combinations:
            return None
        if self.strategy == 'min':
            return min(valid_combinations, key=lambda x: len(x))
        elif self.strategy == 'max':
            return max(valid_combinations, key=lambda x: len(x))
        elif self.strategy == 'safe':
            non_one = [c for c in valid_combinations if 1 not in c]
            if non_one:
                return max(non_one, key=lambda x: len(x))
            return min(valid_combinations, key=lambda x: len(x))
        else:
            raise ValueError(f"Unknown strategy: {self.strategy}")

    def cover_cards(self, combination):
        for c in combination:
            self.cards.remove(c)

def roll_dice(num_dice=2):
    return sum(random.randint(1, 6) for _ in range(num_dice))

def play_round(players, stats):
    current = 0
    num_players = len(players)
    consecutive_pass = 0

    while True:
        player = players[current]

        dice_num = 1 if len(player.cards) == 1 else 2
        dice_sum = roll_dice(dice_num)

        valid_combos = player.find_valid_combinations(dice_sum)
        best = player.choose_best_combination(valid_combos)

        if best:
            player.cover_cards(best)
            player.history.append((dice_sum, tuple(sorted(best))))
            consecutive_pass = 0

            if not player.has_cards():
                for ds, comb in player.history:
                    stats['win_combos'][(ds, comb)] += 1
                # 回傳贏家與其他人剩牌數
                return [player], [0 if p == player else len(p.cards) for p in players]
        else:
            consecutive_pass += 1
            if consecutive_pass >= num_players:
                # 全員 PASS，判定剩餘最少為勝者
                remaining = [len(p.cards) for p in players]
                min_val = min(remaining)
                winners = [p for p in players if len(p.cards) == min_val]
                for w in winners:
                    for ds, comb in w.history:
                        stats['win_combos'][(ds, comb)] += 1
                return winners, remaining

        current = (current + 1) % num_players

def simulate_game_with_score(num_rounds, num_players, strategy):
    stats = {'win_combos': Counter()}
    total_scores = [0] * num_players

    for _ in range(num_rounds):
        players = [Player(f"Player{i+1}", strategy=strategy) for i in range(num_players)]
        winners, scores = play_round(players, stats)
        for i in range(num_players):
            total_scores[i] += scores[i]

    return stats['win_combos'], total_scores

def compare_strategies(num_games=1000, num_rounds=3):
    strategies = ['min', 'max', 'safe']
    all_stats = {s: {} for s in strategies}
    total_score_summary = {s: {} for s in strategies}

    for strategy in strategies:
        print(f"\n🔍 模擬策略: {strategy}")
        for n in range(2, 5):
            print(f"  模擬 {n} 人局 x {num_rounds} 回合 x {num_games} 場...")
            total_score = [0] * n
            win_combos = Counter()

            for _ in range(num_games):
                combos, scores = simulate_game_with_score(num_rounds, n, strategy)
                win_combos.update(combos)
                for i in range(n):
                    total_score[i] += scores[i]

            all_stats[strategy][n] = win_combos
            avg_scores = [round(score / num_games, 2) for score in total_score]
            total_score_summary[strategy][n] = avg_scores

    # 顯示勝利組合
    print("\n📊【勝利者常用蓋牌組合統計】")
    all_keys = set()
    for strategy_stats in all_stats.values():
        for player_data in strategy_stats.values():
            all_keys.update(player_data.keys())

    grouped_by_sum = defaultdict(list)
    for key in all_keys:
        dice_sum, combo = key
        grouped_by_sum[dice_sum].append(combo)

    for ds in range(2, 13):
        if ds not in grouped_by_sum:
            continue
        print(f"\n🎲 骰子總和 {ds}")
        combos = grouped_by_sum[ds]
        for comb in sorted(set(combos)):
            line = f"  {comb}:"
            for strategy in strategies:
                for players in range(2, 5):
                    count = all_stats[strategy][players].get((ds, comb), 0)
                    line += f" {strategy}-{players}人[{count}]"
            print(line)

    # 顯示平均扣分
    print("\n🏁【平均剩餘牌數（越低越好）】")
    for strategy in strategies:
        for players in range(2, 5):
            avg = total_score_summary[strategy][players]
            print(f"{strategy} 策略 - {players}人局：平均剩餘牌數 {avg}")

if __name__ == "__main__":
    compare_strategies(num_games=1000, num_rounds=3)
