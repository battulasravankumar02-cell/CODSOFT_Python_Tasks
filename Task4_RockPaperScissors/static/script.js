/**
 * ROCK • PAPER • SCISSORS — Frontend Controller
 * 
 * Manages Navigation Tabs, Hero Landing, Single Player, Duo 2-Player Match Flow,
 * Scoreboard Summaries, Theme Switching, and API communication.
 * 
 * NOTE: All game logic, random selections, winner determination,
 * and score tracking are computed strictly on the Python Flask backend.
 */

document.addEventListener('DOMContentLoaded', () => {
    // =========================================================================
    // 1. DOM ELEMENTS
    // =========================================================================

    // Navigation Tabs & Action Triggers
    const navTabs = document.querySelectorAll('.nav-tab');
    const tabPanes = document.querySelectorAll('.tab-pane');
    const heroStartSingleBtn = document.querySelector('.hero-start-single');
    const heroStartDuoBtn = document.querySelector('.hero-start-duo');
    const backHomeButtons = document.querySelectorAll('.back-home-btn');

    // Hero Stats
    const heroUserScoreEl = document.getElementById('hero-user-score');
    const heroTieScoreEl = document.getElementById('hero-tie-score');
    const heroCpuScoreEl = document.getElementById('hero-cpu-score');

    // Single Player Elements
    const singleUserScoreEl = document.getElementById('user-score-val');
    const singleCpuScoreEl = document.getElementById('cpu-score-val');
    const singleTiesScoreEl = document.getElementById('ties-score-val');
    const singleArenaEmpty = document.getElementById('arena-empty');
    const singleArenaBattle = document.getElementById('arena-battle');
    const singleUserIcon = document.getElementById('user-choice-icon');
    const singleUserLabel = document.getElementById('user-choice-label');
    const singleCpuIcon = document.getElementById('cpu-choice-icon');
    const singleCpuLabel = document.getElementById('cpu-choice-label');
    const singleResultBanner = document.getElementById('result-banner');
    const singleResultTitle = document.getElementById('result-title-text');
    const singleResultReason = document.getElementById('result-reason-text');
    const singleChoiceButtons = document.querySelectorAll('.single-choice-btn');
    const btnSinglePlayAgain = document.getElementById('btn-play-again');
    const btnSingleReset = document.getElementById('btn-reset-game');
    const singleHistoryList = document.getElementById('history-list');
    const singleHistoryCount = document.getElementById('history-count');

    // Duo Player Elements
    const duoSetupSection = document.getElementById('duo-setup-section');
    const duoActiveSection = document.getElementById('duo-active-section');
    const inputP1Name = document.getElementById('input-p1-name');
    const inputP2Name = document.getElementById('input-p2-name');
    const btnStartDuo = document.getElementById('btn-start-duo');
    const duoP1Badge = document.getElementById('duo-p1-badge');
    const duoP2Badge = document.getElementById('duo-p2-badge');
    const duoP1ScoreVal = document.getElementById('duo-p1-score-val');
    const duoP2ScoreVal = document.getElementById('duo-p2-score-val');
    const duoTiesScoreVal = document.getElementById('duo-ties-score-val');
    const duoP1Caption = document.getElementById('duo-p1-caption');
    const duoP2Caption = document.getElementById('duo-p2-caption');
    const duoTurnState = document.getElementById('duo-turn-state');
    const duoTurnIndicator = document.getElementById('duo-turn-indicator');
    const duoTurnSubtitle = document.getElementById('duo-turn-subtitle');
    const duoChoiceButtons = document.querySelectorAll('.duo-choice-btn');
    const duoClashState = document.getElementById('duo-clash-state');
    const duoP1Fighter = document.getElementById('duo-p1-fighter');
    const duoP2Fighter = document.getElementById('duo-p2-fighter');
    const duoP1ClashTag = document.getElementById('duo-p1-clash-tag');
    const duoP2ClashTag = document.getElementById('duo-p2-clash-tag');
    const duoP1ChoiceIcon = document.getElementById('duo-p1-choice-icon');
    const duoP1ChoiceLabel = document.getElementById('duo-p1-choice-label');
    const duoP2ChoiceIcon = document.getElementById('duo-p2-choice-icon');
    const duoP2ChoiceLabel = document.getElementById('duo-p2-choice-label');
    const duoResultBanner = document.getElementById('duo-result-banner');
    const duoResultTitleText = document.getElementById('duo-result-title-text');
    const duoResultReasonText = document.getElementById('duo-result-reason-text');
    const btnDuoNextRound = document.getElementById('btn-duo-next-round');
    const btnDuoChangePlayers = document.getElementById('btn-duo-change-players');
    const duoHistoryList = document.getElementById('duo-history-list');
    const duoHistoryCount = document.getElementById('duo-history-count');

    // Score Tab Elements
    const tabScoreSingleUser = document.getElementById('tab-score-single-user');
    const tabScoreSingleTies = document.getElementById('tab-score-single-ties');
    const tabScoreSingleCpu = document.getElementById('tab-score-single-cpu');
    const tabScoreDuoP1Name = document.getElementById('tab-score-duo-p1-name');
    const tabScoreDuoP1Val = document.getElementById('tab-score-duo-p1-val');
    const tabScoreDuoP2Name = document.getElementById('tab-score-duo-p2-name');
    const tabScoreDuoP2Val = document.getElementById('tab-score-duo-p2-val');
    const tabScoreDuoTiesVal = document.getElementById('tab-score-duo-ties-val');
    const btnTabResetScore = document.getElementById('btn-tab-reset-score');

    // Theme Elements
    const themeBtnDark = document.getElementById('theme-btn-dark');
    const themeBtnLight = document.getElementById('theme-btn-light');

    // Modal & Toast Elements
    const resetModal = document.getElementById('reset-modal');
    const btnModalCancel = document.getElementById('btn-modal-cancel');
    const btnModalConfirm = document.getElementById('btn-modal-confirm');
    const toastBox = document.getElementById('toast-box');

    // Duo Game Turn Memory
    let duoState = {
        p1Name: inputP1Name?.value.trim() || 'Player 1',
        p2Name: inputP2Name?.value.trim() || 'Player 2',
        currentTurn: 1, // 1 for Player 1, 2 for Player 2
        p1Choice: null,
        p2Choice: null,
        isProcessing: false
    };

    let singleProcessing = false;

    // =========================================================================
    // 2. TOAST NOTIFICATIONS & SCORE ANIMATIONS
    // =========================================================================

    function showToast(message, isError = false) {
        if (!toastBox) return;
        const toast = document.createElement('div');
        toast.className = `toast ${isError ? 'toast-error' : ''}`;
        toast.textContent = message;
        toastBox.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateY(15px)';
            toast.style.transition = 'all 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    function animateScore(element, newValue) {
        if (!element) return;
        if (element.textContent !== String(newValue)) {
            element.textContent = newValue;
            element.classList.add('updated');
            setTimeout(() => {
                element.classList.remove('updated');
            }, 350);
        }
    }

    // =========================================================================
    // 3. TAB NAVIGATION CONTROLLER
    // =========================================================================

    function switchTab(targetTab) {
        navTabs.forEach(t => {
            const isMatch = t.dataset.tab === targetTab;
            t.classList.toggle('active', isMatch);
            t.setAttribute('aria-selected', isMatch ? 'true' : 'false');
        });

        tabPanes.forEach(p => {
            p.classList.toggle('active', p.id === `pane-${targetTab}`);
        });

        if (targetTab === 'score') {
            fetchScores();
        }
    }

    navTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            switchTab(tab.dataset.tab);
        });
    });

    if (heroStartSingleBtn) {
        heroStartSingleBtn.addEventListener('click', () => {
            switchTab('single');
        });
    }

    if (heroStartDuoBtn) {
        heroStartDuoBtn.addEventListener('click', () => {
            switchTab('duo');
        });
    }

    backHomeButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            switchTab('home');
        });
    });

    // =========================================================================
    // 4. SINGLE PLAYER CONTROLLER
    // =========================================================================

    function renderSingleHistory(historyItems) {
        if (!singleHistoryList) return;

        if (!historyItems || historyItems.length === 0) {
            singleHistoryList.innerHTML = `
                <div class="history-empty" id="history-empty-msg">
                    <span>No rounds played yet. Choose your weapon to start!</span>
                </div>
            `;
            if (singleHistoryCount) singleHistoryCount.textContent = '0 / 5';
            return;
        }

        if (singleHistoryCount) {
            singleHistoryCount.textContent = `${historyItems.length} / 5`;
        }

        const html = historyItems.map(r => {
            const badgeLabel = r.result === 'win' ? 'WIN' : (r.result === 'lose' ? 'DEFEAT' : 'TIE');
            return `
                <div class="history-row history-row-${r.result}">
                    <div class="history-col history-col-you">
                        <span class="history-icon">${r.user_icon}</span>
                        <span class="history-text">You: <strong>${r.user_label}</strong></span>
                    </div>
                    <div class="history-col history-col-vs">vs</div>
                    <div class="history-col history-col-cpu">
                        <span class="history-icon">${r.computer_icon}</span>
                        <span class="history-text">CPU: <strong>${r.computer_label}</strong></span>
                    </div>
                    <div class="history-col history-col-badge">
                        <span class="badge-outcome badge-${r.result}">${badgeLabel}</span>
                    </div>
                </div>
            `;
        }).join('');

        singleHistoryList.innerHTML = html;
    }

    async function handleSingleChoice(choice) {
        if (singleProcessing) return;
        singleProcessing = true;

        singleChoiceButtons.forEach(btn => {
            if (btn.dataset.choice === choice) {
                btn.classList.add('selected');
                setTimeout(() => btn.classList.remove('selected'), 300);
            }
        });

        try {
            const response = await fetch('/play', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({ choice: choice })
            });

            const data = await response.json();

            if (!response.ok || !data.success) {
                showToast(data.error || 'Unable to process round. Please try again.', true);
                singleProcessing = false;
                return;
            }

            const round = data.round;

            // Update Arena
            singleArenaEmpty.classList.add('hidden');
            singleArenaBattle.classList.remove('hidden');

            singleUserIcon.textContent = round.user_icon;
            singleUserLabel.textContent = round.user_label;
            singleCpuIcon.textContent = round.computer_icon;
            singleCpuLabel.textContent = round.computer_label;

            // Result Banner
            singleResultBanner.className = `result-banner result-${round.result}`;
            singleResultTitle.textContent = round.result_title;
            singleResultReason.textContent = round.result_reason;

            // Scores
            animateScore(singleUserScoreEl, data.scores.user);
            animateScore(singleCpuScoreEl, data.scores.computer);
            animateScore(singleTiesScoreEl, data.scores.ties);

            // Update Hero mini scores
            if (heroUserScoreEl) heroUserScoreEl.textContent = data.scores.user;
            if (heroTieScoreEl) heroTieScoreEl.textContent = data.scores.ties;
            if (heroCpuScoreEl) heroCpuScoreEl.textContent = data.scores.computer;

            // History
            renderSingleHistory(data.history);

            // Show Play Again button
            btnSinglePlayAgain.classList.remove('hidden');

        } catch (err) {
            console.error('Single Player Error:', err);
            showToast('Connection error with game server.', true);
        } finally {
            singleProcessing = false;
        }
    }

    async function handleSinglePlayAgain() {
        try {
            await fetch('/play-again', {
                method: 'POST',
                headers: { 'Accept': 'application/json' }
            });
            singleArenaBattle.classList.add('hidden');
            singleArenaEmpty.classList.remove('hidden');
            btnSinglePlayAgain.classList.add('hidden');
        } catch (err) {
            console.error('Play Again Error:', err);
        }
    }

    singleChoiceButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            handleSingleChoice(btn.dataset.choice);
        });
    });

    if (btnSinglePlayAgain) {
        btnSinglePlayAgain.addEventListener('click', handleSinglePlayAgain);
    }

    if (btnSingleReset) {
        btnSingleReset.addEventListener('click', () => {
            openResetModal();
        });
    }

    // =========================================================================
    // 5. DUO 2-PLAYER CONTROLLER
    // =========================================================================

    function updateDuoTurnPrompt() {
        if (!duoTurnIndicator || !duoTurnSubtitle) return;
        if (duoState.currentTurn === 1) {
            duoTurnIndicator.textContent = `${duoState.p1Name}, select your weapon`;
            duoTurnSubtitle.textContent = `Choose silently, then pass device to ${duoState.p2Name}.`;
        } else {
            duoTurnIndicator.textContent = `${duoState.p2Name}, select your weapon`;
            duoTurnSubtitle.textContent = `Choose silently to battle ${duoState.p1Name}!`;
        }
    }

    function renderDuoHistory(historyItems) {
        if (!duoHistoryList) return;

        if (!historyItems || historyItems.length === 0) {
            duoHistoryList.innerHTML = `
                <div class="history-empty" id="duo-history-empty-msg">
                    <span>No duo rounds played yet. Make your moves to start!</span>
                </div>
            `;
            if (duoHistoryCount) duoHistoryCount.textContent = '0 / 5';
            return;
        }

        if (duoHistoryCount) {
            duoHistoryCount.textContent = `${historyItems.length} / 5`;
        }

        const html = historyItems.map(r => {
            const outcomeBadge = r.result === 'p1_win' ? `${r.p1_name} WON` : (r.result === 'p2_win' ? `${r.p2_name} WON` : 'TIE');
            const outcomeClass = r.result === 'tie' ? 'tie' : (r.result === 'p1_win' ? 'win' : 'lose');
            return `
                <div class="history-row history-row-${outcomeClass}">
                    <div class="history-col history-col-you">
                        <span class="history-icon">${r.p1_icon}</span>
                        <span class="history-text">${r.p1_name}: <strong>${r.p1_label}</strong></span>
                    </div>
                    <div class="history-col history-col-vs">vs</div>
                    <div class="history-col history-col-cpu">
                        <span class="history-icon">${r.p2_icon}</span>
                        <span class="history-text">${r.p2_name}: <strong>${r.p2_label}</strong></span>
                    </div>
                    <div class="history-col history-col-badge">
                        <span class="badge-outcome badge-${outcomeClass}">${outcomeBadge}</span>
                    </div>
                </div>
            `;
        }).join('');

        duoHistoryList.innerHTML = html;
    }

    async function handleStartDuo() {
        const p1 = inputP1Name.value.trim() || 'Player 1';
        const p2 = inputP2Name.value.trim() || 'Player 2';

        try {
            const response = await fetch('/duo-setup', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({ p1_name: p1, p2_name: p2 })
            });

            const data = await response.json();

            if (data.success) {
                duoState.p1Name = data.p1_name;
                duoState.p2Name = data.p2_name;
                duoState.currentTurn = 1;
                duoState.p1Choice = null;
                duoState.p2Choice = null;

                // Update UI Labels & Badges
                duoP1Badge.textContent = duoState.p1Name.toUpperCase();
                duoP2Badge.textContent = duoState.p2Name.toUpperCase();
                duoP1Caption.textContent = `${duoState.p1Name} Score`;
                duoP2Caption.textContent = `${duoState.p2Name} Score`;

                animateScore(duoP1ScoreVal, 0);
                animateScore(duoP2ScoreVal, 0);
                animateScore(duoTiesScoreVal, 0);

                duoSetupSection.classList.add('hidden');
                duoActiveSection.classList.remove('hidden');
                duoTurnState.classList.remove('hidden');
                duoClashState.classList.add('hidden');
                btnDuoNextRound.classList.add('hidden');

                updateDuoTurnPrompt();
                renderDuoHistory([]);
                showToast(`Match started: ${duoState.p1Name} vs ${duoState.p2Name}!`);
            }
        } catch (err) {
            console.error('Start Duo Error:', err);
            showToast('Unable to start Duo match.', true);
        }
    }

    async function handleDuoChoice(choice) {
        if (duoState.isProcessing) return;

        if (duoState.currentTurn === 1) {
            // Player 1 selected
            duoState.p1Choice = choice;
            duoState.currentTurn = 2;

            showToast(`${duoState.p1Name} locked move! 🔒 Pass to ${duoState.p2Name}`);
            updateDuoTurnPrompt();

        } else if (duoState.currentTurn === 2) {
            // Player 2 selected -> submit round to Python backend
            duoState.p2Choice = choice;
            duoState.isProcessing = true;

            try {
                const response = await fetch('/play-duo', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                    },
                    body: JSON.stringify({
                        p1_name: duoState.p1Name,
                        p2_name: duoState.p2Name,
                        p1_choice: duoState.p1Choice,
                        p2_choice: duoState.p2Choice
                    })
                });

                const data = await response.json();

                if (!response.ok || !data.success) {
                    showToast(data.error || 'Error processing Duo round.', true);
                    duoState.isProcessing = false;
                    return;
                }

                const round = data.round;

                // Show Clash Reveal
                duoTurnState.classList.add('hidden');
                duoClashState.classList.remove('hidden');

                duoP1ClashTag.textContent = `${duoState.p1Name.toUpperCase()}'S MOVE`;
                duoP2ClashTag.textContent = `${duoState.p2Name.toUpperCase()}'S MOVE`;

                duoP1ChoiceIcon.textContent = round.p1_icon;
                duoP1ChoiceLabel.textContent = round.p1_label;
                duoP2ChoiceIcon.textContent = round.p2_icon;
                duoP2ChoiceLabel.textContent = round.p2_label;

                // Outcome Banner
                const outcomeClass = round.result === 'tie' ? 'tie' : (round.result === 'p1_win' ? 'win' : 'lose');
                duoResultBanner.className = `result-banner result-${outcomeClass}`;
                duoResultTitleText.textContent = round.result_title;
                duoResultReasonText.textContent = round.result_reason;

                // Scores
                animateScore(duoP1ScoreVal, data.scores.p1);
                animateScore(duoP2ScoreVal, data.scores.p2);
                animateScore(duoTiesScoreVal, data.scores.ties);

                // History
                renderDuoHistory(data.history);

                // Show Next Round Button
                btnDuoNextRound.classList.remove('hidden');

            } catch (err) {
                console.error('Duo Round Error:', err);
                showToast('Connection error during Duo round.', true);
            } finally {
                duoState.isProcessing = false;
            }
        }
    }

    async function handleDuoNextRound() {
        try {
            await fetch('/duo-play-again', {
                method: 'POST',
                headers: { 'Accept': 'application/json' }
            });
            duoState.currentTurn = 1;
            duoState.p1Choice = null;
            duoState.p2Choice = null;

            duoClashState.classList.add('hidden');
            duoTurnState.classList.remove('hidden');
            btnDuoNextRound.classList.add('hidden');
            updateDuoTurnPrompt();
        } catch (err) {
            console.error('Duo Next Round Error:', err);
        }
    }

    function handleDuoChangePlayers() {
        duoActiveSection.classList.add('hidden');
        duoSetupSection.classList.remove('hidden');
    }

    if (btnStartDuo) {
        btnStartDuo.addEventListener('click', handleStartDuo);
    }

    duoChoiceButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            handleDuoChoice(btn.dataset.choice);
        });
    });

    if (btnDuoNextRound) {
        btnDuoNextRound.addEventListener('click', handleDuoNextRound);
    }

    if (btnDuoChangePlayers) {
        btnDuoChangePlayers.addEventListener('click', handleDuoChangePlayers);
    }

    // =========================================================================
    // 6. SCOREBOARD TAB & RESET SCORE MODAL
    // =========================================================================

    async function fetchScores() {
        try {
            const response = await fetch('/get-scores');
            const data = await response.json();

            if (data.success) {
                // Update Single Player Stats
                if (tabScoreSingleUser) tabScoreSingleUser.textContent = data.single.user;
                if (tabScoreSingleTies) tabScoreSingleTies.textContent = data.single.ties;
                if (tabScoreSingleCpu) tabScoreSingleCpu.textContent = data.single.computer;

                // Update Hero Mini Stats
                if (heroUserScoreEl) heroUserScoreEl.textContent = data.single.user;
                if (heroTieScoreEl) heroTieScoreEl.textContent = data.single.ties;
                if (heroCpuScoreEl) heroCpuScoreEl.textContent = data.single.computer;

                // Update Duo Player Stats
                if (tabScoreDuoP1Name) tabScoreDuoP1Name.textContent = data.duo.p1_name ? data.duo.p1_name.toUpperCase() : 'PLAYER 1';
                if (tabScoreDuoP1Val) tabScoreDuoP1Val.textContent = data.duo.p1_score;
                if (tabScoreDuoP2Name) tabScoreDuoP2Name.textContent = data.duo.p2_name ? data.duo.p2_name.toUpperCase() : 'PLAYER 2';
                if (tabScoreDuoP2Val) tabScoreDuoP2Val.textContent = data.duo.p2_score;
                if (tabScoreDuoTiesVal) tabScoreDuoTiesVal.textContent = data.duo.ties;
            }
        } catch (err) {
            console.error('Fetch Scores Error:', err);
        }
    }

    function openResetModal() {
        if (resetModal) {
            resetModal.classList.remove('hidden');
        }
    }

    function closeResetModal() {
        if (resetModal) {
            resetModal.classList.add('hidden');
        }
    }

    async function executeScoreReset() {
        try {
            const response = await fetch('/reset', {
                method: 'POST',
                headers: { 'Accept': 'application/json' }
            });
            const data = await response.json();

            if (data.success) {
                // Reset Single Player UI
                animateScore(singleUserScoreEl, 0);
                animateScore(singleCpuScoreEl, 0);
                animateScore(singleTiesScoreEl, 0);
                if (heroUserScoreEl) heroUserScoreEl.textContent = '0';
                if (heroTieScoreEl) heroTieScoreEl.textContent = '0';
                if (heroCpuScoreEl) heroCpuScoreEl.textContent = '0';

                singleArenaBattle.classList.add('hidden');
                singleArenaEmpty.classList.remove('hidden');
                btnSinglePlayAgain.classList.add('hidden');
                renderSingleHistory([]);

                // Reset Duo Player UI
                animateScore(duoP1ScoreVal, 0);
                animateScore(duoP2ScoreVal, 0);
                animateScore(duoTiesScoreVal, 0);
                duoClashState.classList.add('hidden');
                duoActiveSection.classList.add('hidden');
                duoSetupSection.classList.remove('hidden');
                if (inputP1Name) inputP1Name.value = '';
                if (inputP2Name) inputP2Name.value = '';
                duoState.p1Name = 'Player 1';
                duoState.p2Name = 'Player 2';
                duoState.currentTurn = 1;
                duoState.p1Choice = null;
                duoState.p2Choice = null;
                renderDuoHistory([]);

                // Reset Score Tab UI
                if (tabScoreSingleUser) tabScoreSingleUser.textContent = '0';
                if (tabScoreSingleTies) tabScoreSingleTies.textContent = '0';
                if (tabScoreSingleCpu) tabScoreSingleCpu.textContent = '0';
                if (tabScoreDuoP1Name) tabScoreDuoP1Name.textContent = 'PLAYER 1';
                if (tabScoreDuoP1Val) tabScoreDuoP1Val.textContent = '0';
                if (tabScoreDuoP2Name) tabScoreDuoP2Name.textContent = 'PLAYER 2';
                if (tabScoreDuoP2Val) tabScoreDuoP2Val.textContent = '0';
                if (tabScoreDuoTiesVal) tabScoreDuoTiesVal.textContent = '0';

                closeResetModal();
                showToast('All scores and session data have been reset to 0!');
            }
        } catch (err) {
            console.error('Reset Error:', err);
            showToast('Unable to reset game scores.', true);
        }
    }

    if (btnTabResetScore) {
        btnTabResetScore.addEventListener('click', openResetModal);
    }

    if (btnModalCancel) {
        btnModalCancel.addEventListener('click', closeResetModal);
    }

    if (btnModalConfirm) {
        btnModalConfirm.addEventListener('click', executeScoreReset);
    }

    // Close modal on outside backdrop click
    if (resetModal) {
        resetModal.addEventListener('click', (e) => {
            if (e.target === resetModal) {
                closeResetModal();
            }
        });
    }

    // =========================================================================
    // 7. THEME SWITCHING (DARK / LIGHT MODE)
    // =========================================================================

    function applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('rps_theme', theme);

        const isDark = theme === 'dark';
        if (themeBtnDark) {
            themeBtnDark.classList.toggle('active', isDark);
            const tag = themeBtnDark.querySelector('.theme-active-tag');
            if (tag) tag.classList.toggle('hidden', !isDark);
        }
        if (themeBtnLight) {
            themeBtnLight.classList.toggle('active', !isDark);
            const tag = themeBtnLight.querySelector('.theme-active-tag');
            if (tag) tag.classList.toggle('hidden', isDark);
        }
    }

    if (themeBtnDark) {
        themeBtnDark.addEventListener('click', () => applyTheme('dark'));
    }

    if (themeBtnLight) {
        themeBtnLight.addEventListener('click', () => applyTheme('light'));
    }

    const savedTheme = localStorage.getItem('rps_theme') || 'dark';
    applyTheme(savedTheme);

    // =========================================================================
    // 8. MOTION UI: DYNAMIC CLASH PARTICLES EMITTER OVER PICTURE
    // =========================================================================

    const clashCanvas = document.getElementById('clash-particles-canvas');
    const heroMotionFrame = document.getElementById('hero-motion-frame');

    if (clashCanvas && heroMotionFrame) {
        const ctx = clashCanvas.getContext('2d');
        let width = 0;
        let height = 0;
        let dpr = window.devicePixelRatio || 1;

        function resizeClashCanvas() {
            const rect = heroMotionFrame.getBoundingClientRect();
            width = rect.width;
            height = rect.height;
            clashCanvas.width = width * dpr;
            clashCanvas.height = height * dpr;
            ctx.scale(dpr, dpr);
        }

        window.addEventListener('resize', resizeClashCanvas);
        resizeClashCanvas();

        const clashColors = [
            '#00e5ff', '#38bdf8', // Cyan sparks
            '#ffb703', '#fb8500', // Gold/Orange sparks
            '#ffffff',           // White hot clash sparks
            '#e879f9', '#c084fc'  // Energy purple
        ];

        class ClashSpark {
            constructor(originX, originY, isBurst = false) {
                this.reset(originX, originY, isBurst);
            }

            reset(originX, originY, isBurst = false) {
                // Collision point is near the center
                const cx = originX !== undefined ? originX : width * 0.5 + (Math.random() - 0.5) * 30;
                const cy = originY !== undefined ? originY : height * 0.5 + (Math.random() - 0.5) * 25;
                
                this.x = cx;
                this.y = cy;

                const angle = Math.random() * Math.PI * 2;
                const speed = isBurst ? (Math.random() * 3.5 + 1.5) : (Math.random() * 2.2 + 0.6);

                this.vx = Math.cos(angle) * speed;
                this.vy = Math.sin(angle) * speed - (Math.random() * 0.8 + 0.3); // Float slightly upward
                this.gravity = 0.02;
                this.drag = 0.985;

                this.size = Math.random() * 3.2 + 1.2;
                this.color = clashColors[Math.floor(Math.random() * clashColors.length)];
                this.alpha = 1;
                this.decay = Math.random() * 0.02 + 0.012;
                this.twinkle = Math.random() * 0.2;
            }

            update() {
                this.x += this.vx;
                this.y += this.vy;
                this.vy += this.gravity;
                this.vx *= this.drag;
                this.vy *= this.drag;
                this.alpha -= this.decay;
                this.size = Math.max(0, this.size - 0.02);

                if (this.alpha <= 0 || this.size <= 0) {
                    this.reset();
                }
            }

            draw() {
                if (this.alpha <= 0) return;
                ctx.save();
                ctx.globalAlpha = Math.max(0, Math.min(1, this.alpha + Math.sin(Date.now() * 0.01) * this.twinkle));
                ctx.fillStyle = this.color;
                ctx.shadowBlur = 10;
                ctx.shadowColor = this.color;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                ctx.fill();
                ctx.restore();
            }
        }

        const sparks = [];
        const sparkCount = 38;
        for (let i = 0; i < sparkCount; i++) {
            const s = new ClashSpark();
            // Stagger start ages so they don't all pop at once
            s.alpha = Math.random();
            sparks.push(s);
        }

        // Interactive hover particle burst
        heroMotionFrame.addEventListener('mousemove', (e) => {
            const rect = heroMotionFrame.getBoundingClientRect();
            const mouseX = e.clientX - rect.left;
            const mouseY = e.clientY - rect.top;

            if (sparks.length < 60 && Math.random() < 0.4) {
                sparks.push(new ClashSpark(mouseX, mouseY, true));
            }
        });

        function animateClashMotion() {
            ctx.clearRect(0, 0, width, height);

            for (let i = 0; i < sparks.length; i++) {
                sparks[i].update();
                sparks[i].draw();
            }

            // Keep array size bounded
            if (sparks.length > sparkCount) {
                sparks.splice(sparkCount, sparks.length - sparkCount);
            }

            requestAnimationFrame(animateClashMotion);
        }

        animateClashMotion();
    }

    // =========================================================================
    // 9. AMBIENT BACKGROUND STARFIELD PARTICLES
    // =========================================================================

    const bgCanvas = document.getElementById('bg-particles-canvas') || document.getElementById('particles-canvas');
    if (bgCanvas) {
        const bgCtx = bgCanvas.getContext('2d');
        let bgWidth = (bgCanvas.width = window.innerWidth);
        let bgHeight = (bgCanvas.height = window.innerHeight);

        window.addEventListener('resize', () => {
            bgWidth = bgCanvas.width = window.innerWidth;
            bgHeight = bgCanvas.height = window.innerHeight;
        });

        const bgParticles = [];
        const bgCount = 40;
        const bgColors = ['#00e5ff', '#ff9d42', '#a855f7', '#ffffff'];

        for (let i = 0; i < bgCount; i++) {
            bgParticles.push({
                x: Math.random() * bgWidth,
                y: Math.random() * bgHeight,
                speed: Math.random() * 0.4 + 0.1,
                vx: (Math.random() - 0.5) * 0.3,
                vy: -(Math.random() * 0.4 + 0.1), // Gentle drift upward
                radius: Math.random() * 1.8 + 0.8,
                color: bgColors[Math.floor(Math.random() * bgColors.length)],
                alpha: Math.random() * 0.5 + 0.2
            });
        }

        function animateBgParticles() {
            bgCtx.clearRect(0, 0, bgWidth, bgHeight);

            for (let i = 0; i < bgParticles.length; i++) {
                const p = bgParticles[i];
                p.x += p.vx;
                p.y += p.vy;

                if (p.x < 0) p.x = bgWidth;
                if (p.x > bgWidth) p.x = 0;
                if (p.y < 0) p.y = bgHeight;
                if (p.y > bgHeight) p.y = 0;

                bgCtx.beginPath();
                bgCtx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
                bgCtx.fillStyle = p.color;
                bgCtx.shadowBlur = 8;
                bgCtx.shadowColor = p.color;
                bgCtx.globalAlpha = p.alpha;
                bgCtx.fill();
                bgCtx.globalAlpha = 1;
            }

            requestAnimationFrame(animateBgParticles);
        }

        animateBgParticles();
    }
});
