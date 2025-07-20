import random
import itertools
from collections import defaultdict, Counter

class Player:
    def __init__(self, name, strategy='min'):
        self.name = name
        self.strategy = strategy
        self.reset()

    def reset(self):
        self.cards = list(range(1, 10))
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

        dice_num = 1 if len(player.cards) == 1 and player.cards[0] == 1 else 2
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
                # 全員 PASS，但遊戲必須直到有人清空手牌才結束。
                # 重置 pass 計數並繼續下一輪。
                consecutive_pass = 0

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
    import sys
    strategies = ['min', 'max', 'safe']
    all_stats = {s: {} for s in strategies}
    total_score_summary = {s: {} for s in strategies}

    for strategy in strategies:
        print(f"\n🔍 模擬策略: {strategy}")
        for n in range(2, 5):
            print(f"  模擬 {n} 人局 x {num_rounds} 回合 x {num_games} 場...")
            total_score = [0] * n
            win_combos = Counter()

            for g in range(num_games):
                combos, scores = simulate_game_with_score(num_rounds, n, strategy)
                win_combos.update(combos)
                for i in range(n):
                    total_score[i] += scores[i]
                # 每 1000 場顯示一次進度
                if (g + 1) % 1000 == 0 or g + 1 == num_games:
                    sys.stdout.write(f"\r      進度: {g + 1}/{num_games}")
                    sys.stdout.flush()
            # 清除進度列
            sys.stdout.write("\r" + " " * 40 + "\r")
            sys.stdout.flush()

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

    # 將結果儲存為 JSON
    import json
    # 將 tuple key 轉換為 string
    all_stats_serializable = {}
    for strategy, player_data in all_stats.items():
        all_stats_serializable[strategy] = {}
        for players, combos in player_data.items():
            all_stats_serializable[strategy][str(players)] = {str(k): v for k, v in combos.items()}

    with open('multiplayer_stats.json', 'w') as f:
        json.dump(all_stats_serializable, f, indent=2)
    print("\n✅ 所有策略的模擬數據已儲存至 multiplayer_stats.json")

if __name__ == "__main__":
    compare_strategies(num_games= 900000, num_rounds=3)

