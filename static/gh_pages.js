// Client-side Cricket Kit Management Engine for GitHub Pages (localStorage)
(function () {
    const STORAGE_KEY = "cricket_kit_gh_pages_v1";

    const DEFAULT_STATE = {
        nextPlayerId: 4,
        nextEquipmentId: 6,
        nextBorrowingId: 1,
        players: [
            { id: 1, name: "Virat Kohli", phone: "9876543210" },
            { id: 2, name: "Rohit Sharma", phone: "9876543211" },
            { id: 3, name: "MS Dhoni", phone: "9876543212" }
        ],
        equipment: [
            { id: 1, name: "Cricket Bat", quantity: 15, available: 15 },
            { id: 2, name: "Helmet", quantity: 20, available: 20 },
            { id: 3, name: "Pads", quantity: 12, available: 12 },
            { id: 4, name: "Practice Balls", quantity: 30, available: 30 },
            { id: 5, name: "Gloves", quantity: 15, available: 15 }
        ],
        borrowings: []
    };

    function cloneDefault() {
        return JSON.parse(JSON.stringify(DEFAULT_STATE));
    }

    function loadState() {
        try {
            const raw = localStorage.getItem(STORAGE_KEY);
            if (!raw) {
                const fresh = cloneDefault();
                saveState(fresh);
                return fresh;
            }
            const parsed = JSON.parse(raw);
            if (!Array.isArray(parsed.players) || !Array.isArray(parsed.equipment) || !Array.isArray(parsed.borrowings)) {
                const fresh = cloneDefault();
                saveState(fresh);
                return fresh;
            }
            return parsed;
        } catch (err) {
            return cloneDefault();
        }
    }

    function saveState(state) {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    }

    function showAlert(message, type) {
        const container = document.getElementById("messages-container");
        if (!container) return;
        container.innerHTML = "";

        const alertEl = document.createElement("div");
        alertEl.className = `alert alert-${type}`;
        alertEl.textContent = message;
        container.appendChild(alertEl);

        setTimeout(() => {
            if (alertEl.parentNode) {
                alertEl.style.transition = "opacity 0.6s ease";
                alertEl.style.opacity = "0";
                setTimeout(() => alertEl.remove(), 600);
            }
        }, 4000);
    }

    function todayISO() {
        const now = new Date();
        const year = now.getFullYear();
        const month = String(now.getMonth() + 1).padStart(2, "0");
        const day = String(now.getDate()).padStart(2, "0");
        return `${year}-${month}-${day}`;
    }

    function renderStats(state) {
        const totalTypes = state.equipment.length;
        const totalItems = state.equipment.reduce((sum, item) => sum + item.quantity, 0);
        const availableItems = state.equipment.reduce((sum, item) => sum + item.available, 0);
        const borrowedItems = state.borrowings
            .filter(b => b.status === "Borrowed")
            .reduce((sum, b) => sum + b.quantity, 0);
        const totalPlayers = state.players.length;

        document.getElementById("stat-types").textContent = totalTypes;
        document.getElementById("stat-total").textContent = totalItems;
        document.getElementById("stat-available").textContent = availableItems;
        document.getElementById("stat-borrowed").textContent = borrowedItems;
        document.getElementById("stat-players").textContent = totalPlayers;
    }

    function renderDropdowns(state) {
        const playerSelect = document.getElementById("borrow-player-id");
        const equipmentSelect = document.getElementById("borrow-equipment-id");

        const sortedPlayers = [...state.players].sort((a, b) => a.name.localeCompare(b.name));
        playerSelect.innerHTML = "";
        const defaultPlayerOpt = document.createElement("option");
        defaultPlayerOpt.value = "";
        defaultPlayerOpt.disabled = true;
        defaultPlayerOpt.selected = true;
        defaultPlayerOpt.textContent = "-- Select Player --";
        playerSelect.appendChild(defaultPlayerOpt);

        sortedPlayers.forEach(player => {
            const opt = document.createElement("option");
            opt.value = String(player.id);
            opt.textContent = `${player.name} (${player.phone || "No Phone"})`;
            playerSelect.appendChild(opt);
        });

        equipmentSelect.innerHTML = "";
        const defaultEqOpt = document.createElement("option");
        defaultEqOpt.value = "";
        defaultEqOpt.disabled = true;
        defaultEqOpt.selected = true;
        defaultEqOpt.textContent = "-- Select Equipment --";
        equipmentSelect.appendChild(defaultEqOpt);

        state.equipment.forEach(item => {
            const opt = document.createElement("option");
            opt.value = String(item.id);
            opt.disabled = item.available === 0;
            opt.textContent = `${item.name} (${item.available} available)`;
            equipmentSelect.appendChild(opt);
        });
    }

    function renderEquipmentTable(state) {
        const tbody = document.getElementById("equipment-table-body");
        tbody.innerHTML = "";

        if (state.equipment.length === 0) {
            const tr = document.createElement("tr");
            const td = document.createElement("td");
            td.colSpan = 5;
            td.textContent = "No equipment records found.";
            tr.appendChild(td);
            tbody.appendChild(tr);
            return;
        }

        state.equipment.forEach(item => {
            const tr = document.createElement("tr");

            const tdId = document.createElement("td");
            tdId.textContent = item.id;

            const tdName = document.createElement("td");
            const strong = document.createElement("strong");
            strong.textContent = item.name;
            tdName.appendChild(strong);

            const tdQty = document.createElement("td");
            tdQty.textContent = item.quantity;

            const tdAvail = document.createElement("td");
            tdAvail.textContent = item.available;

            const tdStatus = document.createElement("td");
            const badge = document.createElement("span");
            if (item.available === 0) {
                badge.className = "badge badge-danger";
                badge.textContent = "Out of Stock";
            } else if (item.available <= 3) {
                badge.className = "badge badge-warning";
                badge.textContent = `Low Stock (${item.available})`;
            } else {
                badge.className = "badge badge-success";
                badge.textContent = "In Stock";
            }
            tdStatus.appendChild(badge);

            tr.append(tdId, tdName, tdQty, tdAvail, tdStatus);
            tbody.appendChild(tr);
        });
    }

    function renderBorrowingsTable(state) {
        const tbody = document.getElementById("borrowings-table-body");
        tbody.innerHTML = "";

        const ordered = [...state.borrowings].sort((a, b) => b.id - a.id);

        if (ordered.length === 0) {
            const tr = document.createElement("tr");
            const td = document.createElement("td");
            td.colSpan = 7;
            td.textContent = "No items borrowed yet.";
            tr.appendChild(td);
            tbody.appendChild(tr);
            return;
        }

        ordered.forEach(record => {
            const player = state.players.find(p => p.id === record.playerId);
            const item = state.equipment.find(e => e.id === record.equipmentId);

            const tr = document.createElement("tr");

            const tdId = document.createElement("td");
            tdId.textContent = `#${record.id}`;

            const tdPlayer = document.createElement("td");
            tdPlayer.textContent = player ? player.name : record.playerName || "Unknown Player";

            const tdEquip = document.createElement("td");
            const strong = document.createElement("strong");
            strong.textContent = item ? item.name : record.equipmentName || "Unknown Item";
            tdEquip.appendChild(strong);

            const tdQty = document.createElement("td");
            tdQty.textContent = record.quantity;

            const tdDate = document.createElement("td");
            tdDate.textContent = record.issueDate;

            const tdStatus = document.createElement("td");
            const badge = document.createElement("span");
            if (record.status === "Borrowed") {
                badge.className = "badge badge-warning";
                badge.textContent = "Borrowed";
            } else {
                badge.className = "badge badge-secondary";
                badge.textContent = "Returned";
            }
            tdStatus.appendChild(badge);

            const tdAction = document.createElement("td");
            if (record.status === "Borrowed") {
                const btn = document.createElement("button");
                btn.type = "button";
                btn.className = "btn-return";
                btn.textContent = "Return Kit";
                btn.addEventListener("click", () => handleReturn(record.id));
                tdAction.appendChild(btn);
            } else {
                const span = document.createElement("span");
                span.className = "text-muted";
                span.textContent = "Completed";
                tdAction.appendChild(span);
            }

            tr.append(tdId, tdPlayer, tdEquip, tdQty, tdDate, tdStatus, tdAction);
            tbody.appendChild(tr);
        });
    }

    function renderAll() {
        const state = loadState();
        renderStats(state);
        renderDropdowns(state);
        renderEquipmentTable(state);
        renderBorrowingsTable(state);
    }

    function handleReturn(borrowId) {
        const state = loadState();
        const record = state.borrowings.find(b => b.id === borrowId);
        if (!record || record.status !== "Borrowed") {
            showAlert("Record not found or already returned!", "danger");
            return;
        }

        const eq = state.equipment.find(e => e.id === record.equipmentId);
        record.status = "Returned";
        if (eq) {
            eq.available = Math.min(eq.quantity, eq.available + record.quantity);
        }

        saveState(state);
        renderAll();
        showAlert(`Equipment returned successfully (${record.quantity} item(s) restored to inventory)!`, "success");
    }

    document.addEventListener("DOMContentLoaded", () => {
        renderAll();

        const borrowForm = document.getElementById("borrow-form");
        const playerForm = document.getElementById("player-form");
        const equipmentForm = document.getElementById("equipment-form");
        const resetBtn = document.getElementById("reset-demo-btn");

        borrowForm.addEventListener("submit", (event) => {
            event.preventDefault();
            if (!borrowForm.checkValidity()) {
                alert("Please enter valid details!");
                return;
            }

            const playerId = parseInt(document.getElementById("borrow-player-id").value, 10);
            const equipmentId = parseInt(document.getElementById("borrow-equipment-id").value, 10);
            const quantity = parseInt(document.getElementById("borrow-quantity").value, 10);

            if (!playerId || !equipmentId || !quantity || quantity <= 0) {
                showAlert("Please select a player, equipment, and a valid quantity!", "danger");
                return;
            }

            const state = loadState();
            const player = state.players.find(p => p.id === playerId);
            const eq = state.equipment.find(e => e.id === equipmentId);

            if (!player || !eq) {
                showAlert("Selected player or equipment not found!", "danger");
                return;
            }

            if (eq.available < quantity) {
                showAlert(`Not enough '${eq.name}' in stock! Only ${eq.available} available.`, "danger");
                return;
            }

            eq.available -= quantity;
            state.borrowings.push({
                id: state.nextBorrowingId++,
                playerId: player.id,
                playerName: player.name,
                equipmentId: eq.id,
                equipmentName: eq.name,
                quantity: quantity,
                issueDate: todayISO(),
                status: "Borrowed"
            });

            saveState(state);
            borrowForm.reset();
            document.getElementById("borrow-quantity").value = "1";
            renderAll();
            showAlert(`Successfully issued ${quantity}x ${eq.name} to ${player.name}!`, "success");
        });

        playerForm.addEventListener("submit", (event) => {
            event.preventDefault();
            if (!playerForm.checkValidity()) {
                alert("Please enter valid details!");
                return;
            }

            const nameInput = document.getElementById("player-name");
            const phoneInput = document.getElementById("player-phone");
            const name = nameInput.value.trim();
            const phone = phoneInput.value.trim();

            if (!name) {
                showAlert("Player name is required!", "danger");
                return;
            }

            const state = loadState();
            state.players.push({
                id: state.nextPlayerId++,
                name: name,
                phone: phone
            });

            saveState(state);
            playerForm.reset();
            renderAll();
            showAlert(`Player '${name}' added successfully!`, "success");
        });

        equipmentForm.addEventListener("submit", (event) => {
            event.preventDefault();
            if (!equipmentForm.checkValidity()) {
                alert("Please enter valid details!");
                return;
            }

            const nameInput = document.getElementById("equipment-name");
            const qtyInput = document.getElementById("equipment-quantity");
            const name = nameInput.value.trim();
            const quantity = parseInt(qtyInput.value, 10);

            if (!name || !quantity || quantity <= 0) {
                showAlert("Please provide a valid equipment name and quantity greater than zero!", "danger");
                return;
            }

            const state = loadState();
            state.equipment.push({
                id: state.nextEquipmentId++,
                name: name,
                quantity: quantity,
                available: quantity
            });

            saveState(state);
            equipmentForm.reset();
            qtyInput.value = "1";
            renderAll();
            showAlert(`Equipment '${name}' (${quantity} items) added successfully!`, "success");
        });

        if (resetBtn) {
            resetBtn.addEventListener("click", () => {
                if (confirm("Reset inventory, players, and borrowing history back to default sample data?")) {
                    const fresh = cloneDefault();
                    saveState(fresh);
                    renderAll();
                    showAlert("Data reset to defaults.", "success");
                }
            });
        }
    });
})();
