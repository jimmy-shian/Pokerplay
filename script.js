document.addEventListener('DOMContentLoaded', () => {
    const cardGrid = document.getElementById('card-grid');
    const playersInput = document.getElementById('players');
    const diceSumInput = document.getElementById('dice-sum');
    const suggestBtn = document.getElementById('suggest-btn');
    const resetBtn = document.getElementById('reset-btn');
    const suggestionOutput = document.getElementById('suggestion-output');

    // Enter 鍵觸發建議
    [diceSumInput, playersInput].forEach(input => {
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                suggestBtn.click();
            }
        });
    });

    let statsData = {};
    let availableCards = Array.from({ length: 9 }, (_, i) => i + 1);

    // 載入數據
    async function loadStats() {
        try {
            const response = await fetch('multiplayer_stats.json');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            statsData = await response.json();
            console.log('數據成功載入:', statsData);
        } catch (error) {
            suggestionOutput.innerHTML = `<p style="color: red;">錯誤：無法載入數據檔案 (multiplayer_stats.json)。請確保檔案存在於同一個資料夾中。</p>`;
            console.error('載入數據失敗:', error);
        }
    }

    // 初始化卡牌
    function initGrid() {
        cardGrid.innerHTML = '';
        availableCards = Array.from({ length: 9 }, (_, i) => i + 1);
        for (let i = 1; i <= 9; i++) {
            const card = document.createElement('div');
            card.className = 'card';
            card.textContent = i;
            card.dataset.value = i;
            card.addEventListener('click', () => toggleCard(card));
            cardGrid.appendChild(card);
        }
        suggestionOutput.innerHTML = '請輸入條件並點擊按鈕。';
    }

    // 切換卡牌狀態
    function toggleCard(cardElement) {
        cardElement.classList.toggle('removed');
        updateAvailableCards();
    }

    // 更新可用卡牌列表
    function updateAvailableCards() {
        availableCards = [];
        const cards = cardGrid.querySelectorAll('.card');
        cards.forEach(card => {
            if (!card.classList.contains('removed')) {
                availableCards.push(parseInt(card.dataset.value));
            }
        });
    }

    // 尋找所有總和等於目標的組合 (遞迴)
    function findCombinations(cards, target, partial = []) {
        const sum = partial.reduce((a, b) => a + b, 0);
        if (sum === target) {
            return [partial];
        }
        if (sum > target) {
            return [];
        }

        let results = [];
        for (let i = 0; i < cards.length; i++) {
            const n = cards[i];
            const remaining = cards.slice(i + 1);
            results = results.concat(findCombinations(remaining, target, partial.concat([n])));
        }
        return results;
    }

    // 獲取建議
    function getSuggestion() {
        const numPlayers = playersInput.value;
        const diceSum = parseInt(diceSumInput.value);
        if (isNaN(diceSum) || diceSum < 2 || diceSum > 12) {
            suggestionOutput.innerHTML = `<p style="color:red;">骰子總和應介於 2 到 12。</p>`;
            return;
        }

        if (!statsData[Object.keys(statsData)[0]]) {
            suggestionOutput.innerHTML = `<p style="color: red;">數據尚未載入或格式不正確。</p>`;
            return;
        }

        const validCombos = findCombinations(availableCards, diceSum);

        if (validCombos.length === 0) {
            suggestionOutput.innerHTML = '根據您目前的牌面，沒有可以出的組合。';
            return;
        }

        let suggestions = [];
        const strategies = ['min', 'max', 'safe'];

        validCombos.forEach(combo => {
            let totalScore = 0;
            let scoresByStrategy = {};

            strategies.forEach(strategy => {
                const tupleString = (() => {
                    const sorted = combo.slice().sort((a, b) => a - b);
                    const inner = sorted.join(', ') + (sorted.length === 1 ? ',' : '');
                    return `(${inner})`;
                })();
                const key = `(${diceSum}, ${tupleString})`;
                const score = statsData[strategy]?.[numPlayers]?.[key] || 0;
                scoresByStrategy[strategy] = score;
                totalScore += score;
            });

            suggestions.push({ combo, totalScore, scoresByStrategy });
        });

        // 根據總分排序，總分越高越好
        suggestions.sort((a, b) => b.totalScore - a.totalScore);

        displaySuggestions(suggestions);
    }

    // 顯示建議
    function displaySuggestions(suggestions) {
        let html = '';
        if (suggestions.length === 0) {
            suggestionOutput.innerHTML = '找不到任何建議。';
            return;
        }

        // 以所有建議總分為分母，計算每組合相對勝率
        const grandTotalScore = suggestions.reduce((acc, s) => acc + s.totalScore, 0) || 1;

        suggestions.forEach(sugg => {
            html += `<div class="suggestion-item">
                        <p><strong>推薦組合:</strong><span class="combo">${sugg.combo.join(' + ')}</span> <span style="color: #666; font-size: 1.1rem;">(勝率: ${((sugg.totalScore / grandTotalScore) * 100).toFixed(1)}%)</span></p>
                        <ul>`;
            Object.entries(sugg.scoresByStrategy).forEach(([strategy, score]) => {
                const pct = sugg.totalScore ? ((score / sugg.totalScore) * 100).toFixed(1) : 0;
                html += `<li><span class="strategy-${strategy}"><strong>${strategy.toUpperCase()} 策略</strong></span>：\t${pct}% <span style="color: #666; font-size: 1rem;">(${score})</span></li>`;
            });
            html += `</ul></div>`;
        });

        suggestionOutput.innerHTML = html;
    }

    // 綁定事件
    suggestBtn.addEventListener('click', getSuggestion);
    resetBtn.addEventListener('click', initGrid);

    // 初始啟動
    loadStats();
    initGrid();
});
