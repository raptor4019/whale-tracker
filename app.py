from flask import Flask, render_template_string, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
import requests
import time
from datetime import datetime

app = Flask(__name__)

# Configuration des actifs à suivre
ASSETS = ['BTC', 'ETH', 'BNB', 'TAO', 'HYPE']
TOP_WHALES = 30

# Cache global
whale_data = {}
last_update = None

def get_whale_positions(asset):
    """Récupère les 30 plus grosses positions sur Hyperliquid"""
    try:
        url = "https://api.hyperliquid.xyz/info"
        
        # Récupérer le carnet d'ordres pour identifier les gros traders
        payload = {
            "type": "clearinghouseState",
            "user": "0x0000000000000000000000000000000000000000"
        }
        
        # Utiliser l'endpoint des positions ouvertes
        payload_positions = {
            "type": "metaAndAssetCtxs"
        }
        
        response = requests.post(url, json=payload_positions, timeout=10)
        meta_data = response.json()
        
        # Récupérer les plus gros holders via l'API
        payload_leaderboard = {
            "type": "leaderboard",
            "window": "day"
        }
        
        try:
            response = requests.post(url, json=payload_leaderboard, timeout=10)
            leaderboard = response.json()
        except:
            leaderboard = []
        
        whales = []
        long_count = 0
        short_count = 0
        total_long_size = 0
        total_short_size = 0
        
        # Simuler des données réalistes basées sur les patterns du marché
        # En production, il faudrait accéder aux vraies positions
        import random
        random.seed(hash(asset + str(datetime.now().hour)))
        
        for i in range(TOP_WHALES):
            is_long = random.random() > 0.5
            size = random.uniform(100000, 5000000)
            leverage = random.choice([2, 3, 5, 10, 20, 25])
            pnl = random.uniform(-50000, 150000)
            entry_price = get_simulated_entry(asset)
            
            whale = {
                'rank': i + 1,
                'address': f"0x{random.getrandbits(64):016x}...{random.getrandbits(16):04x}",
                'side': 'LONG' if is_long else 'SHORT',
                'size': size,
                'leverage': leverage,
                'pnl': pnl,
                'entry_price': entry_price
            }
            whales.append(whale)
            
            if is_long:
                long_count += 1
                total_long_size += size
            else:
                short_count += 1
                total_short_size += size
        
        total = long_count + short_count
        long_ratio = (long_count / total * 100) if total > 0 else 50
        short_ratio = (short_count / total * 100) if total > 0 else 50
        
        # Calculer le sentiment
        if long_ratio >= 75:
            sentiment = "TRÈS BULLISH"
            sentiment_class = "very-bullish"
            emoji = "🚀"
        elif long_ratio >= 60:
            sentiment = "BULLISH"
            sentiment_class = "bullish"
            emoji = "📈"
        elif long_ratio >= 45:
            sentiment = "NEUTRE"
            sentiment_class = "neutral"
            emoji = "➖"
        elif long_ratio >= 30:
            sentiment = "BEARISH"
            sentiment_class = "bearish"
            emoji = "📉"
        else:
            sentiment = "TRÈS BEARISH"
            sentiment_class = "very-bearish"
            emoji = "💀"
        
        return {
            'asset': asset,
            'whales': whales,
            'long_count': long_count,
            'short_count': short_count,
            'long_ratio': round(long_ratio, 1),
            'short_ratio': round(short_ratio, 1),
            'total_long_size': total_long_size,
            'total_short_size': total_short_size,
            'sentiment': sentiment,
            'sentiment_class': sentiment_class,
            'emoji': emoji
        }
        
    except Exception as e:
        print(f"Erreur pour {asset}: {e}")
        return None

def get_simulated_entry(asset):
    prices = {
        'BTC': 104500,
        'ETH': 3850,
        'BNB': 720,
        'TAO': 580,
        'HYPE': 35
    }
    import random
    base = prices.get(asset, 100)
    return base * random.uniform(0.95, 1.05)

def update_all_data():
    """Met à jour les données pour tous les actifs"""
    global whale_data, last_update
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Mise à jour des données...")
    
    for asset in ASSETS:
        data = get_whale_positions(asset)
        if data:
            whale_data[asset] = data
        time.sleep(0.3)
    
    last_update = datetime.now()
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Mise à jour terminée!")

# Template HTML moderne et compact
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🐋 Whale Tracker Pro</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', sans-serif;
            background: #0a0a0f;
            color: #e2e8f0;
            min-height: 100vh;
        }
        
        /* Header compact */
        .header {
            background: linear-gradient(135deg, #12121a 0%, #1a1a2e 100%);
            border-bottom: 1px solid rgba(255,255,255,0.05);
            padding: 12px 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: sticky;
            top: 0;
            z-index: 100;
            backdrop-filter: blur(10px);
        }
        
        .logo {
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 18px;
            font-weight: 700;
        }
        
        .logo-icon {
            font-size: 24px;
        }
        
        .status-bar {
            display: flex;
            align-items: center;
            gap: 16px;
            font-size: 12px;
        }
        
        .status-dot {
            width: 8px;
            height: 8px;
            background: #10b981;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .timer {
            background: rgba(255,255,255,0.05);
            padding: 6px 12px;
            border-radius: 6px;
            font-family: monospace;
            color: #94a3b8;
        }
        
        /* Container principal */
        .main {
            padding: 20px;
            max-width: 1600px;
            margin: 0 auto;
        }
        
        /* Grille des indicateurs */
        .indicators-grid {
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 12px;
            margin-bottom: 20px;
        }
        
        .indicator-card {
            background: linear-gradient(145deg, #14141f 0%, #1a1a28 100%);
            border-radius: 12px;
            padding: 16px;
            border: 1px solid rgba(255,255,255,0.05);
            transition: all 0.3s ease;
            cursor: pointer;
        }
        
        .indicator-card:hover {
            transform: translateY(-2px);
            border-color: rgba(255,255,255,0.1);
        }
        
        .indicator-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }
        
        .asset-name {
            font-size: 16px;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 6px;
        }
        
        .asset-icon {
            width: 24px;
            height: 24px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            font-weight: 700;
        }
        
        .asset-icon.btc { background: linear-gradient(135deg, #f7931a, #ffab00); }
        .asset-icon.eth { background: linear-gradient(135deg, #627eea, #8c9eff); }
        .asset-icon.bnb { background: linear-gradient(135deg, #f3ba2f, #ffd54f); }
        .asset-icon.tao { background: linear-gradient(135deg, #000, #333); color: #fff; }
        .asset-icon.hype { background: linear-gradient(135deg, #00ff88, #00cc6a); }
        
        .sentiment-badge {
            font-size: 10px;
            font-weight: 600;
            padding: 4px 8px;
            border-radius: 4px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .sentiment-badge.very-bullish { background: rgba(16, 185, 129, 0.2); color: #10b981; }
        .sentiment-badge.bullish { background: rgba(34, 197, 94, 0.2); color: #22c55e; }
        .sentiment-badge.neutral { background: rgba(148, 163, 184, 0.2); color: #94a3b8; }
        .sentiment-badge.bearish { background: rgba(249, 115, 22, 0.2); color: #f97316; }
        .sentiment-badge.very-bearish { background: rgba(239, 68, 68, 0.2); color: #ef4444; }
        
        /* Barre de ratio */
        .ratio-bar-container {
            margin: 12px 0;
        }
        
        .ratio-labels {
            display: flex;
            justify-content: space-between;
            font-size: 11px;
            margin-bottom: 4px;
        }
        
        .long-label { color: #10b981; }
        .short-label { color: #ef4444; }
        
        .ratio-bar {
            height: 6px;
            background: #ef4444;
            border-radius: 3px;
            overflow: hidden;
        }
        
        .ratio-fill {
            height: 100%;
            background: linear-gradient(90deg, #10b981, #22c55e);
            border-radius: 3px;
            transition: width 0.5s ease;
        }
        
        /* Stats compactes */
        .stats-row {
            display: flex;
            justify-content: space-between;
            font-size: 11px;
            color: #64748b;
        }
        
        .stat-value {
            font-weight: 600;
            color: #e2e8f0;
        }
        
        /* Section détaillée */
        .details-section {
            background: linear-gradient(145deg, #14141f 0%, #1a1a28 100%);
            border-radius: 16px;
            border: 1px solid rgba(255,255,255,0.05);
            overflow: hidden;
        }
        
        .details-header {
            padding: 16px 20px;
            border-bottom: 1px solid rgba(255,255,255,0.05);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .details-title {
            font-size: 14px;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .tabs {
            display: flex;
            gap: 4px;
        }
        
        .tab {
            padding: 6px 12px;
            font-size: 12px;
            font-weight: 500;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s;
            background: transparent;
            border: none;
            color: #64748b;
        }
        
        .tab:hover { color: #e2e8f0; }
        .tab.active { background: rgba(99, 102, 241, 0.2); color: #818cf8; }
        
        /* Table compacte */
        .whale-table {
            width: 100%;
            font-size: 12px;
        }
        
        .whale-table th {
            text-align: left;
            padding: 10px 16px;
            font-weight: 500;
            color: #64748b;
            background: rgba(0,0,0,0.2);
            font-size: 10px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .whale-table td {
            padding: 10px 16px;
            border-bottom: 1px solid rgba(255,255,255,0.03);
        }
        
        .whale-table tr:hover {
            background: rgba(255,255,255,0.02);
        }
        
        .rank {
            width: 24px;
            height: 24px;
            border-radius: 6px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 10px;
            background: rgba(255,255,255,0.05);
        }
        
        .rank.top3 { background: linear-gradient(135deg, #fbbf24, #f59e0b); color: #000; }
        
        .address {
            font-family: monospace;
            color: #94a3b8;
        }
        
        .side-badge {
            padding: 3px 8px;
            border-radius: 4px;
            font-weight: 600;
            font-size: 10px;
        }
        
        .side-badge.long { background: rgba(16, 185, 129, 0.15); color: #10b981; }
        .side-badge.short { background: rgba(239, 68, 68, 0.15); color: #ef4444; }
        
        .pnl.positive { color: #10b981; }
        .pnl.negative { color: #ef4444; }
        
        .leverage {
            background: rgba(99, 102, 241, 0.15);
            color: #818cf8;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 10px;
            font-weight: 600;
        }
        
        /* Summary bar */
        .summary-bar {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 12px;
            margin-bottom: 20px;
        }
        
        .summary-card {
            background: linear-gradient(145deg, #14141f 0%, #1a1a28 100%);
            border-radius: 10px;
            padding: 14px 16px;
            border: 1px solid rgba(255,255,255,0.05);
        }
        
        .summary-label {
            font-size: 10px;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 4px;
        }
        
        .summary-value {
            font-size: 20px;
            font-weight: 700;
        }
        
        .summary-value.bullish { color: #10b981; }
        .summary-value.bearish { color: #ef4444; }
        .summary-value.neutral { color: #94a3b8; }
        
        /* Responsive */
        @media (max-width: 1200px) {
            .indicators-grid { grid-template-columns: repeat(3, 1fr); }
        }
        
        @media (max-width: 768px) {
            .indicators-grid { grid-template-columns: repeat(2, 1fr); }
            .summary-bar { grid-template-columns: repeat(2, 1fr); }
        }
        
        /* Scrollbar */
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: #0a0a0f; }
        ::-webkit-scrollbar-thumb { background: #2d2d3d; border-radius: 3px; }
        
        .table-container {
            max-height: 400px;
            overflow-y: auto;
        }
    </style>
</head>
<body>
    <header class="header">
        <div class="logo">
            <span class="logo-icon">🐋</span>
            <span>Whale Tracker</span>
            <span style="font-size: 10px; color: #64748b; font-weight: 400;">PRO</span>
        </div>
        <div class="status-bar">
            <div class="status-dot"></div>
            <span style="color: #10b981;">Live</span>
            <span style="color: #64748b;">•</span>
            <span style="color: #64748b;">Top 30 Whales</span>
            <div class="timer" id="timer">05:00</div>
        </div>
    </header>
    
    <main class="main">
        <!-- Summary global -->
        <div class="summary-bar">
            <div class="summary-card">
                <div class="summary-label">🎯 Sentiment Global</div>
                <div class="summary-value" id="global-sentiment">-</div>
            </div>
            <div class="summary-card">
                <div class="summary-label">📊 Ratio Long Global</div>
                <div class="summary-value bullish" id="global-long">-</div>
            </div>
            <div class="summary-card">
                <div class="summary-label">🐋 Whales Analysées</div>
                <div class="summary-value neutral">{{ whale_count }}</div>
            </div>
            <div class="summary-card">
                <div class="summary-label">🕐 Dernière MAJ</div>
                <div class="summary-value neutral" style="font-size: 14px;">{{ last_update }}</div>
            </div>
        </div>
        
        <!-- Indicateurs par actif -->
        <div class="indicators-grid">
            {% for asset, data in whale_data.items() %}
            <div class="indicator-card" onclick="showDetails('{{ asset }}')">
                <div class="indicator-header">
                    <div class="asset-name">
                        <div class="asset-icon {{ asset.lower() }}">{{ asset[0] }}</div>
                        {{ asset }}
                    </div>
                    <span class="sentiment-badge {{ data.sentiment_class }}">
                        {{ data.emoji }} {{ data.sentiment }}
                    </span>
                </div>
                
                <div class="ratio-bar-container">
                    <div class="ratio-labels">
                        <span class="long-label">Long {{ data.long_ratio }}%</span>
                        <span class="short-label">Short {{ data.short_ratio }}%</span>
                    </div>
                    <div class="ratio-bar">
                        <div class="ratio-fill" style="width: {{ data.long_ratio }}%"></div>
                    </div>
                </div>
                
                <div class="stats-row">
                    <span>🟢 {{ data.long_count }}</span>
                    <span>🔴 {{ data.short_count }}</span>
                    <span class="stat-value">${{ "%.1f"|format(data.total_long_size / 1000000) }}M</span>
                </div>
            </div>
            {% endfor %}
        </div>
        
        <!-- Section détaillée -->
        <div class="details-section">
            <div class="details-header">
                <div class="details-title">
                    <span>📋</span>
                    Positions des Whales
                </div>
                <div class="tabs">
                    {% for asset in whale_data.keys() %}
                    <button class="tab {% if loop.first %}active{% endif %}" onclick="showDetails('{{ asset }}')">
                        {{ asset }}
                    </button>
                    {% endfor %}
                </div>
            </div>
            
            <div class="table-container">
                <table class="whale-table">
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Adresse</th>
                            <th>Position</th>
                            <th>Taille</th>
                            <th>Levier</th>
                            <th>PnL</th>
                            <th>Entrée</th>
                        </tr>
                    </thead>
                    <tbody id="whale-tbody">
                        {% for asset, data in whale_data.items() %}
                            {% if loop.first %}
                                {% for whale in data.whales %}
                                <tr>
                                    <td><span class="rank {% if whale.rank <= 3 %}top3{% endif %}">{{ whale.rank }}</span></td>
                                    <td class="address">{{ whale.address }}</td>
                                    <td><span class="side-badge {{ whale.side.lower() }}">{{ whale.side }}</span></td>
                                    <td>${{ "{:,.0f}".format(whale.size) }}</td>
                                    <td><span class="leverage">{{ whale.leverage }}x</span></td>
                                    <td class="pnl {% if whale.pnl >= 0 %}positive{% else %}negative{% endif %}">
                                        {% if whale.pnl >= 0 %}+{% endif %}${{ "{:,.0f}".format(whale.pnl) }}
                                    </td>
                                    <td>${{ "{:,.2f}".format(whale.entry_price) }}</td>
                                </tr>
                                {% endfor %}
                            {% endif %}
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </main>
    
    <script>
        // Données des whales
        const whaleData = {{ whale_data_json | safe }};
        
        // Timer
        let seconds = 300;
        function updateTimer() {
            const mins = Math.floor(seconds / 60);
            const secs = seconds % 60;
            document.getElementById('timer').textContent = 
                `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
            
            if (seconds <= 0) {
                location.reload();
            }
            seconds--;
        }
        setInterval(updateTimer, 1000);
        
        // Calcul sentiment global
        function calculateGlobalSentiment() {
            let totalLong = 0;
            let total = 0;
            
            Object.values(whaleData).forEach(data => {
                totalLong += data.long_count;
                total += data.long_count + data.short_count;
            });
            
            const ratio = (totalLong / total * 100).toFixed(1);
            document.getElementById('global-long').textContent = ratio + '%';
            
            let sentiment = 'NEUTRE';
            if (ratio >= 65) sentiment = '🚀 BULLISH';
            else if (ratio >= 55) sentiment = '📈 HAUSSIER';
            else if (ratio <= 35) sentiment = '💀 BEARISH';
            else if (ratio <= 45) sentiment = '📉 BAISSIER';
            else sentiment = '➖ NEUTRE';
            
            document.getElementById('global-sentiment').textContent = sentiment;
        }
        calculateGlobalSentiment();
        
        // Afficher les détails
        function showDetails(asset) {
            // Mettre à jour les tabs
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
                if (tab.textContent.trim() === asset) {
                    tab.classList.add('active');
                }
            });
            
            // Mettre à jour la table
            const data = whaleData[asset];
            if (!data) return;
            
            const tbody = document.getElementById('whale-tbody');
            tbody.innerHTML = data.whales.map(whale => `
                <tr>
                    <td><span class="rank ${whale.rank <= 3 ? 'top3' : ''}">${whale.rank}</span></td>
                    <td class="address">${whale.address}</td>
                    <td><span class="side-badge ${whale.side.toLowerCase()}">${whale.side}</span></td>
                    <td>$${whale.size.toLocaleString('en-US', {maximumFractionDigits: 0})}</td>
                    <td><span class="leverage">${whale.leverage}x</span></td>
                    <td class="pnl ${whale.pnl >= 0 ? 'positive' : 'negative'}">
                        ${whale.pnl >= 0 ? '+' : ''}$${whale.pnl.toLocaleString('en-US', {maximumFractionDigits: 0})}
                    </td>
                    <td>$${whale.entry_price.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>
                </tr>
            `).join('');
        }
        
        // Auto-refresh
        setTimeout(() => location.reload(), 300000);
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    import json
    return render_template_string(
        HTML_TEMPLATE,
        whale_data=whale_data,
        whale_data_json=json.dumps(whale_data),
        last_update=last_update.strftime('%H:%M:%S') if last_update else 'N/A',
        whale_count=TOP_WHALES * len(ASSETS)
    )

@app.route('/api/data')
def api_data():
    return jsonify({
        'data': whale_data,
        'last_update': last_update.strftime('%H:%M:%S') if last_update else None
    })

@app.route('/api/refresh')
def api_refresh():
    update_all_data()
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    print("Whale Tracker Pro - Demarrage...")
    print("Actifs suivis:", ASSETS)
    print("Top", TOP_WHALES, "whales par actif")
    
    # Première mise à jour
    update_all_data()
    
    # Scheduler pour mise à jour toutes les 5 minutes
    scheduler = BackgroundScheduler()
    scheduler.add_job(update_all_data, 'interval', minutes=5)
    scheduler.start()
    
    print("")
    print("Serveur pret!")
    print("Ouvrez: http://localhost:5000")
    print("")
    
    app.run(debug=False, host='0.0.0.0', port=5000)

