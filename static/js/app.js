// DM Assistant Web - JavaScript Application

// Estado global
const state = {
    currentCharacter: null,
    characters: [],
    monsters: [],
    combatants: [],
    commandHistory: [],
    historyIndex: -1
};

// ==================== INICIALIZACIÓN ====================

document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    loadCharacters();
    loadMonsterTypes();
    updateClock();
    setInterval(updateClock, 1000);
    
    // Event listeners
    document.getElementById('console-input').addEventListener('keydown', handleConsoleInput);
    document.getElementById('dice-notation').addEventListener('keydown', function(e) {
        if (e.key === 'Enter') rollCustomDice();
    });
    document.getElementById('monster-search-input').addEventListener('keydown', function(e) {
        if (e.key === 'Enter') searchMonsters();
    });
});

function initializeApp() {
    addConsoleMessage('⚔️ DM Assistant Web v1.0 iniciado', 'system');
    addConsoleMessage('Cargando datos...', 'system');
    addLog('Sistema iniciado');
}

function updateClock() {
    const now = new Date();
    const timeStr = now.toLocaleTimeString('es-ES');
    document.getElementById('current-time').textContent = timeStr;
}

// ==================== CONSOLA ====================

function handleConsoleInput(e) {
    if (e.key === 'Enter') {
        const input = e.target.value.trim();
        if (input) {
            executeCommand(input);
            state.commandHistory.push(input);
            state.historyIndex = state.commandHistory.length;
            e.target.value = '';
        }
    } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        if (state.historyIndex > 0) {
            state.historyIndex--;
            e.target.value = state.commandHistory[state.historyIndex];
        }
    } else if (e.key === 'ArrowDown') {
        e.preventDefault();
        if (state.historyIndex < state.commandHistory.length - 1) {
            state.historyIndex++;
            e.target.value = state.commandHistory[state.historyIndex];
        } else {
            state.historyIndex = state.commandHistory.length;
            e.target.value = '';
        }
    }
}

function executeCommand(cmd) {
    addConsoleMessage(`⚔️ > ${cmd}`, 'system');
    
    const parts = cmd.trim().split(/\s+/);
    const command = parts[0].toLowerCase();
    const args = parts.slice(1);
    
    switch(command) {
        case '/help':
            showHelp();
            break;
        case '/clear':
            clearConsole();
            break;
        case '/characters':
            listCharactersInConsole();
            break;
        case '/character':
            if (args.length > 0) {
                loadCharacterByName(args.join(' '));
            } else {
                addConsoleMessage('Uso: /character [nombre o número]', 'error');
            }
            break;
        case '/dice':
        case '/d':
            if (args.length > 0) {
                rollDiceFromConsole(args[0]);
            } else {
                addConsoleMessage('Uso: /dice [notación] (ej: /dice 3d6)', 'error');
            }
            break;
        case '/d20':
            rollDiceFromConsole('1d20');
            break;
        case '/hp':
            if (args.length > 0) {
                modifyHPFromConsole(args[0]);
            } else {
                addConsoleMessage('Uso: /hp [+/-/=][valor] (ej: /hp +10, /hp -5, /hp =20)', 'error');
            }
            break;
        case '/xp':
            if (args.length > 0) {
                addXPFromConsole(parseInt(args[0]));
            } else {
                addConsoleMessage('Uso: /xp [cantidad]', 'error');
            }
            break;
        case '/monster':
            if (args.length > 0) {
                searchMonstersFromConsole(args.join(' '));
            } else {
                addConsoleMessage('Uso: /monster [nombre]', 'error');
            }
            break;
        case '/stats':
            showCurrentCharacterStats();
            break;
        default:
            addConsoleMessage(`Comando desconocido: ${command}. Escribe /help para ver los comandos disponibles.`, 'error');
    }
}

function addConsoleMessage(message, type = 'system') {
    const output = document.getElementById('console-output');
    const msgDiv = document.createElement('div');
    msgDiv.className = `console-message ${type}`;
    msgDiv.innerHTML = message;
    output.appendChild(msgDiv);
    output.scrollTop = output.scrollHeight;
}

function clearConsole() {
    document.getElementById('console-output').innerHTML = '';
    addConsoleMessage('Consola limpiada', 'system');
}

function showHelp() {
    toggleHelp();
}

// ==================== PERSONAJES ====================

async function loadCharacters() {
    try {
        const response = await fetch('/api/characters');
        const data = await response.json();
        
        if (data.success) {
            state.characters = data.characters;
            renderCharacterList();
            updateStats();
            addConsoleMessage(`✓ ${data.characters.length} personajes cargados`, 'success');
            addLog(`${data.characters.length} personajes cargados`);
        } else {
            addConsoleMessage('✗ Error cargando personajes: ' + data.error, 'error');
        }
    } catch (error) {
        addConsoleMessage('✗ Error de conexión al servidor', 'error');
        console.error(error);
    }
}

function renderCharacterList() {
    const container = document.getElementById('character-list');
    
    if (state.characters.length === 0) {
        container.innerHTML = '<div class="loading">No hay personajes disponibles</div>';
        return;
    }
    
    container.innerHTML = '';
    state.characters.forEach((char, index) => {
        const card = document.createElement('div');
        card.className = 'character-card';
        card.onclick = () => loadCharacterByIndex(index);
        
        const hpPercent = (char.hp_current / char.hp_max) * 100;
        
        card.innerHTML = `
            <h4>${char.name}</h4>
            <div class="char-info">${char.race} ${char.class} Nv.${char.level}</div>
            <div class="char-stats">
                <span>HP: ${char.hp_current}/${char.hp_max}</span>
                <span>CA: ${char.ac}</span>
            </div>
            <div class="hp-bar">
                <div class="hp-bar-fill" style="width: ${hpPercent}%"></div>
            </div>
        `;
        
        container.appendChild(card);
    });
}

async function loadCharacterByIndex(index) {
    const char = state.characters[index];
    if (!char) return;
    
    try {
        const response = await fetch('/api/character/load', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ filename: char.filename })
        });
        
        const data = await response.json();
        
        if (data.success) {
            state.currentCharacter = data.character;
            renderCurrentCharacter();
            highlightActiveCharacter(index);
            addConsoleMessage(`✓ Personaje cargado: ${data.character.name}`, 'success');
            addLog(`Personaje cargado: ${data.character.name}`);
        } else {
            addConsoleMessage('✗ Error cargando personaje: ' + data.error, 'error');
        }
    } catch (error) {
        addConsoleMessage('✗ Error de conexión', 'error');
        console.error(error);
    }
}

function loadCharacterByName(nameOrNumber) {
    const num = parseInt(nameOrNumber);
    if (!isNaN(num) && num > 0 && num <= state.characters.length) {
        loadCharacterByIndex(num - 1);
    } else {
        const index = state.characters.findIndex(c => 
            c.name.toLowerCase().includes(nameOrNumber.toLowerCase())
        );
        if (index >= 0) {
            loadCharacterByIndex(index);
        } else {
            addConsoleMessage('✗ Personaje no encontrado', 'error');
        }
    }
}

function highlightActiveCharacter(index) {
    const cards = document.querySelectorAll('.character-card');
    cards.forEach((card, i) => {
        if (i === index) {
            card.classList.add('active');
        } else {
            card.classList.remove('active');
        }
    });
}

function renderCurrentCharacter() {
    const panel = document.getElementById('current-character-info');
    const char = state.currentCharacter;
    
    if (!char) {
        panel.innerHTML = '<p class="text-muted">Selecciona un personaje</p>';
        return;
    }
    
    const hp = char.hp || {};
    const hpPercent = (hp.current / hp.max) * 100;
    
    panel.innerHTML = `
        <h4 style="color: var(--secondary-color); margin-bottom: 10px;">${char.name}</h4>
        <p><strong>${char.race}</strong> - ${char.class} Nivel ${char.level}</p>
        <p>XP: ${char.experience || 0}</p>
        <div style="margin: 10px 0;">
            <p>HP: ${hp.current}/${hp.max}</p>
            <div class="hp-bar">
                <div class="hp-bar-fill" style="width: ${hpPercent}%"></div>
            </div>
        </div>
        <p>CA: ${char.ac} | THAC0: ${char.thac0}</p>
        <div style="margin-top: 10px; font-size: 0.85rem; color: var(--text-secondary);">
            <p>FUE ${char.attributes?.FUE || 10} | DES ${char.attributes?.DES || 10} | CON ${char.attributes?.CON || 10}</p>
            <p>INT ${char.attributes?.INT || 10} | SAB ${char.attributes?.SAB || 10} | CAR ${char.attributes?.CAR || 10}</p>
        </div>
    `;
}

function listCharactersInConsole() {
    addConsoleMessage('<strong>Personajes disponibles:</strong>', 'system');
    state.characters.forEach((char, index) => {
        addConsoleMessage(`${index + 1}. ${char.name} - ${char.race} ${char.class} Nv.${char.level} (HP: ${char.hp_current}/${char.hp_max})`, 'system');
    });
}

function showCurrentCharacterStats() {
    if (!state.currentCharacter) {
        addConsoleMessage('✗ No hay personaje cargado', 'error');
        return;
    }
    
    const char = state.currentCharacter;
    const hp = char.hp || {};
    
    addConsoleMessage(`<strong>═══ ${char.name} ═══</strong>`, 'success');
    addConsoleMessage(`${char.race} ${char.class} Nivel ${char.level}`, 'system');
    addConsoleMessage(`HP: ${hp.current}/${hp.max} | CA: ${char.ac} | THAC0: ${char.thac0}`, 'system');
    addConsoleMessage(`FUE ${char.attributes?.FUE} DES ${char.attributes?.DES} CON ${char.attributes?.CON} INT ${char.attributes?.INT} SAB ${char.attributes?.SAB} CAR ${char.attributes?.CAR}`, 'system');
    addConsoleMessage(`XP: ${char.experience || 0}`, 'system');
}

// ==================== HP / XP / DINERO ====================

async function modifyHP(operation, value) {
    if (!state.currentCharacter) {
        addConsoleMessage('✗ No hay personaje cargado', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/character/hp', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ operation, value })
        });
        
        const data = await response.json();
        
        if (data.success) {
            state.currentCharacter.hp = { current: data.hp.current, max: data.hp.max };
            renderCurrentCharacter();
            loadCharacters(); // Actualizar lista
            
            const change = data.hp.change;
            const changeStr = change > 0 ? `+${change}` : change;
            addConsoleMessage(`✓ HP modificado ${changeStr}: ${data.hp.current}/${data.hp.max}`, 'success');
            addLog(`HP modificado: ${changeStr}`);
        } else {
            addConsoleMessage('✗ Error: ' + data.error, 'error');
        }
    } catch (error) {
        addConsoleMessage('✗ Error de conexión', 'error');
        console.error(error);
    }
}

function setHP() {
    const value = parseInt(document.getElementById('hp-custom').value);
    if (!isNaN(value)) {
        modifyHP('set', value);
        document.getElementById('hp-custom').value = '';
    }
}

function modifyHPFromConsole(input) {
    const match = input.match(/^([+\-=])(\d+)$/);
    if (!match) {
        addConsoleMessage('✗ Formato inválido. Usa +10, -5 o =20', 'error');
        return;
    }
    
    const op = match[1];
    const value = parseInt(match[2]);
    
    const operation = op === '+' ? 'add' : op === '-' ? 'subtract' : 'set';
    modifyHP(operation, value);
}

async function addXP() {
    const input = document.getElementById('xp-amount');
    const xp = parseInt(input.value);
    
    if (isNaN(xp) || xp <= 0) {
        addConsoleMessage('✗ XP inválido', 'error');
        return;
    }
    
    addXPFromConsole(xp);
    input.value = '';
}

async function addXPFromConsole(xp) {
    if (!state.currentCharacter) {
        addConsoleMessage('✗ No hay personaje cargado', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/character/xp', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ xp })
        });
        
        const data = await response.json();
        
        if (data.success) {
            state.currentCharacter.experience = data.xp.new_xp;
            renderCurrentCharacter();
            addConsoleMessage(`✓ XP añadido: +${data.xp.added} (Total: ${data.xp.new_xp})`, 'success');
            addLog(`XP añadido: +${data.xp.added}`);
        } else {
            addConsoleMessage('✗ Error: ' + data.error, 'error');
        }
    } catch (error) {
        addConsoleMessage('✗ Error de conexión', 'error');
        console.error(error);
    }
}

// ==================== DADOS ====================

async function rollDice(notation) {
    updateLastRoll(notation);
    
    try {
        const response = await fetch('/api/dice/roll', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ notation })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayDiceResult(data);
            addLog(`Tirada: ${notation} = ${data.total}`);
        } else {
            addConsoleMessage('✗ Error: ' + data.error, 'error');
        }
    } catch (error) {
        addConsoleMessage('✗ Error de conexión', 'error');
        console.error(error);
    }
}

function rollCustomDice() {
    const notation = document.getElementById('dice-notation').value.trim();
    if (notation) {
        rollDice(notation);
        document.getElementById('dice-notation').value = '';
    }
}

function rollDiceFromConsole(notation) {
    rollDice(notation);
}

function displayDiceResult(data) {
    const container = document.getElementById('dice-results');
    const rollsStr = data.rolls.join(', ');
    
    container.innerHTML = `
        <div class="dice-result-item">
            <strong>${data.notation}</strong> = <span style="font-size: 2rem;">${data.total}</span>
            <span class="rolls">Tiradas: [${rollsStr}]${data.modifier !== 0 ? ` + Modificador: ${data.modifier}` : ''}</span>
        </div>
    `;
    
    const msg = `🎲 ${data.notation}: [${rollsStr}]${data.modifier !== 0 ? ` ${data.modifier > 0 ? '+' : ''}${data.modifier}` : ''} = <strong>${data.total}</strong>`;
    addConsoleMessage(msg, 'roll');
}

async function rollAttack() {
    const thac0 = parseInt(document.getElementById('attack-thac0').value);
    const weaponBonus = parseInt(document.getElementById('attack-weapon-bonus').value);
    const strBonus = parseInt(document.getElementById('attack-str-bonus').value);
    
    try {
        const response = await fetch('/api/dice/attack', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ thac0, weapon_bonus: weaponBonus, str_bonus: strBonus })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayAttackResult(data);
            addLog(`Ataque: d20=${data.roll}, AC impactada=${data.ac_hit}`);
        } else {
            addConsoleMessage('✗ Error: ' + data.error, 'error');
        }
    } catch (error) {
        addConsoleMessage('✗ Error de conexión', 'error');
        console.error(error);
    }
}

function displayAttackResult(data) {
    const container = document.getElementById('attack-results');
    
    let resultClass = '';
    let resultText = '';
    
    if (data.is_critical) {
        resultClass = 'attack-critical';
        resultText = '🎯 ¡CRÍTICO! ¡Doble daño!';
    } else if (data.is_fumble) {
        resultClass = 'attack-fumble';
        resultText = '💥 ¡PIFIA! Fallo automático';
    } else {
        resultClass = 'attack-success';
        resultText = `Tirada: ${data.roll} + ${data.bonuses.weapon + data.bonuses.strength} = ${data.total}`;
    }
    
    container.innerHTML = `
        <div class="${resultClass}">
            <p><strong>${resultText}</strong></p>
            <p>THAC0: ${data.thac0} - Total: ${data.total} = <strong>CA impactada: ${data.ac_hit}</strong></p>
            <p style="font-size: 0.9rem; color: var(--text-secondary); margin-top: 5px;">
                Impacta a objetivos con CA ${data.ac_hit} o superior (número más alto)
            </p>
        </div>
    `;
    
    const msg = `⚔️ Ataque: d20=${data.roll}, THAC0=${data.thac0}, Bonos=${data.bonuses.weapon + data.bonuses.strength} → <strong>CA ${data.ac_hit}</strong>`;
    addConsoleMessage(msg, data.is_critical ? 'success' : 'roll');
}

// ==================== MONSTRUOS ====================

async function loadMonsterTypes() {
    try {
        const response = await fetch('/api/monsters/types');
        const data = await response.json();
        
        if (data.success) {
            const select = document.getElementById('monster-type-filter');
            data.types.forEach(type => {
                const option = document.createElement('option');
                option.value = type;
                option.textContent = type;
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.error(error);
    }
}

async function searchMonsters() {
    const query = document.getElementById('monster-search-input').value.trim();
    if (!query) return;
    
    searchMonstersFromConsole(query);
}

async function searchMonstersFromConsole(query) {
    try {
        const response = await fetch(`/api/monsters/search?q=${encodeURIComponent(query)}`);
        const data = await response.json();
        
        if (data.success) {
            displayMonsters(data.monsters);
            addConsoleMessage(`✓ Encontrados ${data.monsters.length} monstruos`, 'success');
        } else {
            addConsoleMessage('✗ Error: ' + data.error, 'error');
        }
    } catch (error) {
        addConsoleMessage('✗ Error de conexión', 'error');
        console.error(error);
    }
}

async function filterMonstersByType() {
    const type = document.getElementById('monster-type-filter').value;
    if (!type) {
        document.getElementById('monster-results').innerHTML = '<p class="text-muted">Selecciona un tipo</p>';
        return;
    }
    
    try {
        const response = await fetch(`/api/monsters/by-type/${encodeURIComponent(type)}`);
        const data = await response.json();
        
        if (data.success) {
            displayMonsters(data.monsters);
            addConsoleMessage(`✓ ${data.monsters.length} monstruos de tipo "${type}"`, 'success');
        } else {
            addConsoleMessage('✗ Error: ' + data.error, 'error');
        }
    } catch (error) {
        addConsoleMessage('✗ Error de conexión', 'error');
        console.error(error);
    }
}

function displayMonsters(monsters) {
    const container = document.getElementById('monster-results');
    
    if (monsters.length === 0) {
        container.innerHTML = '<p class="text-muted">No se encontraron monstruos</p>';
        return;
    }
    
    container.innerHTML = '';
    monsters.forEach(monster => {
        const card = document.createElement('div');
        card.className = 'monster-card';
        card.innerHTML = `
            <h4>${monster.name}</h4>
            <div class="monster-stat"><label>CA:</label><span>${monster.ac}</span></div>
            <div class="monster-stat"><label>HD:</label><span>${monster.hd}</span></div>
            <div class="monster-stat"><label>HP:</label><span>${monster.hp}</span></div>
            <div class="monster-stat"><label>THAC0:</label><span>${monster.thac0}</span></div>
            <div class="monster-stat"><label>Ataques:</label><span>${monster.attacks}</span></div>
            <div class="monster-stat"><label>Daño:</label><span>${monster.damage}</span></div>
            <div class="monster-stat"><label>Movimiento:</label><span>${monster.movement}</span></div>
            <div class="monster-stat"><label>Moral:</label><span>${monster.morale}</span></div>
        `;
        container.appendChild(card);
    });
}

// ==================== COMBATE ====================

function addCombatant(button) {
    const parent = button.parentElement;
    const name = parent.querySelector('input[type="text"]').value;
    const bonus = parseInt(parent.querySelector('input[type="number"]').value) || 0;
    
    if (!name) return;
    
    state.combatants.push({ name, bonus });
    
    // Limpiar inputs
    parent.querySelector('input[type="text"]').value = '';
    parent.querySelector('input[type="number"]').value = '0';
    
    // Añadir nuevo input
    const newInput = document.createElement('div');
    newInput.className = 'combatant-input';
    newInput.innerHTML = `
        <input type="text" placeholder="Nombre" class="input">
        <input type="number" placeholder="Bonus" class="input" style="width: 80px;" value="0">
        <button class="btn btn-small" onclick="addCombatant(this)">➕</button>
    `;
    document.getElementById('combatants-list').appendChild(newInput);
    
    addConsoleMessage(`Combatiente añadido: ${name} (bonus: ${bonus > 0 ? '+' : ''}${bonus})`, 'system');
}

async function rollInitiative() {
    if (state.combatants.length === 0) {
        addConsoleMessage('✗ Añade combatientes primero', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/combat/initiative', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ combatants: state.combatants })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayInitiative(data.initiative);
            addConsoleMessage(`✓ Iniciativa tirada para ${data.initiative.length} combatientes`, 'success');
            addLog('Iniciativa tirada');
        } else {
            addConsoleMessage('✗ Error: ' + data.error, 'error');
        }
    } catch (error) {
        addConsoleMessage('✗ Error de conexión', 'error');
        console.error(error);
    }
}

function displayInitiative(results) {
    const container = document.getElementById('initiative-results');
    const trackerContainer = document.getElementById('combat-tracker-list');
    
    let html = '<h4 style="color: var(--secondary-color); margin-bottom: 10px;">Orden de Iniciativa:</h4>';
    results.forEach((result, index) => {
        html += `
            <div class="initiative-item">
                <span><strong>${index + 1}.</strong> ${result.name}</span>
                <span>Tirada: ${result.roll} + ${result.bonus} = <strong>${result.total}</strong></span>
            </div>
        `;
    });
    
    container.innerHTML = html;
    trackerContainer.innerHTML = html;
    
    // Añadir a consola
    addConsoleMessage('<strong>═══ INICIATIVA ═══</strong>', 'success');
    results.forEach((result, index) => {
        addConsoleMessage(`${index + 1}. ${result.name}: ${result.roll} + ${result.bonus} = <strong>${result.total}</strong>`, 'roll');
    });
}

// ==================== UI UTILITIES ====================

function showTab(tabName) {
    // Desactivar todas las tabs
    document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    
    // Activar la tab seleccionada
    event.target.classList.add('active');
    document.getElementById(`tab-${tabName}`).classList.add('active');
}

function toggleHelp() {
    const modal = document.getElementById('help-modal');
    modal.classList.toggle('active');
}

function updateStats() {
    document.getElementById('stat-characters').textContent = state.characters.length;
}

function updateLastRoll(notation) {
    document.getElementById('stat-last-roll').textContent = notation;
}

function addLog(message) {
    const log = document.getElementById('activity-log');
    const entry = document.createElement('div');
    entry.className = 'log-entry';
    const time = new Date().toLocaleTimeString('es-ES');
    entry.textContent = `[${time}] ${message}`;
    log.insertBefore(entry, log.firstChild);
    
    // Limitar a 50 entradas
    while (log.children.length > 50) {
        log.removeChild(log.lastChild);
    }
}

// Cerrar modal al hacer clic fuera
window.onclick = function(event) {
    const modal = document.getElementById('help-modal');
    if (event.target === modal) {
        modal.classList.remove('active');
    }
}
