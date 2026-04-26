# chemhelper.py - Chemistry lab assistant (MVP)
from flask import Flask, render_template_string, request, jsonify
import json
import math

app = Flask(__name__)

# Small database (JSON file - scales to big DB later)
LAB_DATA_FILE = 'lab_data.json'

def load_data():
    try:
        with open(LAB_DATA_FILE, 'r') as f:
            return json.load(f)
    except:
        return {'compounds': [], 'experiments': [], 'reactions': []}

def save_data(data):
    with open(LAB_DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>LabAssistant - Chemistry Lab Software</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { box-sizing: border-box; }
        body {
            font-family: 'Courier New', monospace;
            background: #1a1a2e;
            margin: 0;
            padding: 20px;
            color: #eee;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            background: #16213e;
            padding: 20px;
            border-radius: 16px;
            margin-bottom: 20px;
            border-left: 4px solid #e94560;
        }
        h1 { margin: 0; color: #e94560; }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
        }
        .card {
            background: #16213e;
            border-radius: 16px;
            padding: 20px;
            border: 1px solid #0f3460;
        }
        .card h2 {
            margin-top: 0;
            color: #e94560;
            font-size: 20px;
        }
        input, select, textarea {
            width: 100%;
            padding: 10px;
            background: #0f3460;
            border: 1px solid #e94560;
            color: white;
            border-radius: 8px;
            margin: 8px 0;
        }
        button {
            background: #e94560;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            margin: 5px;
        }
        button.secondary {
            background: #0f3460;
            border: 1px solid #e94560;
        }
        .compound-list {
            max-height: 300px;
            overflow-y: auto;
        }
        .compound-item {
            background: #0f3460;
            padding: 10px;
            margin: 8px 0;
            border-radius: 8px;
            cursor: pointer;
        }
        .compound-item:hover {
            background: #e94560;
        }
        .reaction-result {
            background: #0f3460;
            padding: 15px;
            border-radius: 8px;
            margin-top: 15px;
            font-family: monospace;
        }
        .badge {
            display: inline-block;
            background: #e94560;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 10px;
            margin-left: 8px;
        }
        @media (max-width: 768px) {
            .grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1> LabAssistant</h1>
            <p>Chemistry lab management</p>
        </div>
        
        <div class="grid">
            <!-- Add Compound -->
            <div class="card">
                <h2>➕ Add Compound</h2>
                <input type="text" id="compoundName" placeholder="Name (e.g., Sodium Chloride)">
                <input type="text" id="compoundFormula" placeholder="Formula (e.g., NaCl)">
                <input type="number" id="compoundQuantity" placeholder="Quantity (g/mL)">
                <select id="compoundLocation">
                    <option value="Cabinet A">Cabinet A</option>
                    <option value="Cabinet B">Cabinet B</option>
                    <option value="Fridge">Fridge</option>
                    <option value="Flammable Cabinet">Flammable Cabinet</option>
                </select>
                <button onclick="addCompound()">Add to Inventory</button>
            </div>
            
            <!-- Inventory -->
            <div class="card">
                <h2> Inventory</h2>
                <div class="compound-list" id="inventoryList"></div>
            </div>
            
            <!-- Reaction Calculator -->
            <div class="card">
                <h2>Reaction Calculator</h2>
                <select id="reactant1">
                    <option value="">Select reactant 1</option>
                </select>
                <select id="reactant2">
                    <option value="">Select reactant 2</option>
                </select>
                <button onclick="calculateReaction()">Predict Reaction</button>
                <div id="reactionResult" class="reaction-result"></div>
            </div>
            
            <!-- Experiment Logger -->
            <div class="card">
                <h2>Experiment Log</h2>
                <input type="text" id="expName" placeholder="Experiment name">
                <textarea id="expNotes" rows="3" placeholder="Notes, observations, results..."></textarea>
                <button onclick="logExperiment()">Save Experiment</button>
                <div id="experimentLog"></div>
            </div>
        </div>
    </div>
    
    <script>
        let compounds = [];
        let experiments = [];
        
        async function loadData() {
            const res = await fetch('/api/data');
            const data = await res.json();
            compounds = data.compounds;
            experiments = data.experiments;
            updateInventory();
            updateReactants();
            updateExperimentLog();
        }
        
        async function addCompound() {
            const name = document.getElementById('compoundName').value;
            const formula = document.getElementById('compoundFormula').value;
            const quantity = document.getElementById('compoundQuantity').value;
            const location = document.getElementById('compoundLocation').value;
            
            if (!name || !formula) return;
            
            const compound = { name, formula, quantity: parseFloat(quantity), location, id: Date.now() };
            
            await fetch('/api/compound', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(compound)
            });
            
            document.getElementById('compoundName').value = '';
            document.getElementById('compoundFormula').value = '';
            document.getElementById('compoundQuantity').value = '';
            loadData();
        }
        
        async function calculateReaction() {
            const r1 = document.getElementById('reactant1').value;
            const r2 = document.getElementById('reactant2').value;
            
            if (!r1 || !r2) {
                document.getElementById('reactionResult').innerHTML = 'Select two compounds';
                return;
            }
            
            const res = await fetch('/api/reaction', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({reactant1: r1, reactant2: r2})
            });
            const result = await res.json();
            
            document.getElementById('reactionResult').innerHTML = `
                <strong>Reaction Prediction</strong><br>
                ${result.message}<br>
                <span class="badge">${result.safety || 'Handle with care'}</span>
            `;
        }
        
        async function logExperiment() {
            const name = document.getElementById('expName').value;
            const notes = document.getElementById('expNotes').value;
            
            if (!name) return;
            
            await fetch('/api/experiment', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({name, notes, date: new Date().toISOString()})
            });
            
            document.getElementById('expName').value = '';
            document.getElementById('expNotes').value = '';
            loadData();
        }
        
        function updateInventory() {
            const container = document.getElementById('inventoryList');
            if (compounds.length === 0) {
                container.innerHTML = '<div class="compound-item">No compounds yet. Add some!</div>';
                return;
            }
            container.innerHTML = compounds.map(c => `
                <div class="compound-item">
                    <strong>${c.name}</strong> (${c.formula})
                    <span class="badge">${c.quantity || 0} units</span>
                    <div style="font-size: 12px;">📍 ${c.location}</div>
                </div>
            `).join('');
        }
        
        function updateReactants() {
            const select1 = document.getElementById('reactant1');
            const select2 = document.getElementById('reactant2');
            
            select1.innerHTML = '<option value="">Select reactant 1</option>';
            select2.innerHTML = '<option value="">Select reactant 2</option>';
            
            compounds.forEach(c => {
                select1.innerHTML += `<option value="${c.name}">${c.name} (${c.formula})</option>`;
                select2.innerHTML += `<option value="${c.name}">${c.name} (${c.formula})</option>`;
            });
        }
        
        function updateExperimentLog() {
            const container = document.getElementById('experimentLog');
            if (experiments.length === 0) {
                container.innerHTML = '<div style="font-size:12px; color:#888;">No experiments logged yet.</div>';
                return;
            }
            container.innerHTML = experiments.slice(-3).reverse().map(e => `
                <div style="background:#0f3460; padding:10px; margin:8px 0; border-radius:8px;">
                    <strong>${e.name}</strong>
                    <div style="font-size:12px;">📅 ${new Date(e.date).toLocaleDateString()}</div>
                    <div style="font-size:12px;">📝 ${e.notes.substring(0, 100)}...</div>
                </div>
            `).join('');
        }
        
        loadData();
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return HTML

@app.route('/api/data')
def get_data():
    return jsonify(load_data())

@app.route('/api/compound', methods=['POST'])
def add_compound():
    data = load_data()
    data['compounds'].append(request.json)
    save_data(data)
    return jsonify({'success': True})

@app.route('/api/experiment', methods=['POST'])
def add_experiment():
    data = load_data()
    data['experiments'].append(request.json)
    save_data(data)
    return jsonify({'success': True})

@app.route('/api/reaction', methods=['POST'])
def predict_reaction():
    # Simple reaction predictor (expand with AI later)
    r1 = request.json['reactant1']
    r2 = request.json['reactant2']
    
    reactions = {
        ('Sodium', 'Chlorine'): 'Forms Sodium Chloride (NaCl) - Table salt!',
        ('Hydrogen', 'Oxygen'): 'Forms Water (H₂O) - Exothermic reaction!',
        ('Acid', 'Base'): 'Neutralization - Forms salt and water'
    }
    
    key = (r1, r2) if (r1, r2) in reactions else (r2, r1)
    result = reactions.get(key, f'Unknown reaction between {r1} and {r2}. Run experiment to determine!')
    
    return jsonify({'message': result, 'safety': 'Perform in well-ventilated area'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)