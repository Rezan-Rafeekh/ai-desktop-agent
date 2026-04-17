document.addEventListener("DOMContentLoaded", () => {
    const runBtn = document.getElementById("runBtn");
    const taskInput = document.getElementById("taskInput");
    const flowSection = document.getElementById("flowSection");
    const gallerySection = document.getElementById("gallerySection");
    const statusIndicator = document.getElementById("statusIndicator");
    const flowGrid = document.getElementById("flowGrid");
    const galleryGrid = document.getElementById("galleryGrid");

    const doExcel = document.getElementById("doExcel");
    const doWord = document.getElementById("doWord");
    const doPdf = document.getElementById("doPdf");
    const useLlm = document.getElementById("useLlm");

    let socket = null;
    let cardsMap = {};

    const extractionPanel = document.getElementById("extraction-panel");
    const extractionPreview = document.getElementById("extraction-data-preview");

    const sidebarToggle = document.getElementById("sidebarToggle");
    const historySidebar = document.getElementById("historySidebar");
    const historyList = document.getElementById("historyList");

    let promptHistory = JSON.parse(localStorage.getItem("promptHistory") || "[]");

    function renderHistory() {
        historyList.innerHTML = "";
        if (promptHistory.length === 0) {
            historyList.innerHTML = "<div style='color: var(--text-muted); font-size: 0.85rem;'>No recent prompts.</div>";
            return;
        }
        promptHistory.forEach(item => {
            const div = document.createElement("div");
            div.className = "history-item";
            div.innerText = item;
            div.addEventListener("click", () => {
                taskInput.value = item;
                historySidebar.classList.remove("open");
            });
            historyList.appendChild(div);
        });
    }

    function addToHistory(t) {
        // remove existing to put it at the top
        promptHistory = promptHistory.filter(h => h !== t);
        promptHistory.unshift(t);
        if (promptHistory.length > 20) promptHistory.pop();
        localStorage.setItem("promptHistory", JSON.stringify(promptHistory));
        renderHistory();
    }

    sidebarToggle.addEventListener("click", () => {
        historySidebar.classList.toggle("open");
    });

    renderHistory();

    runBtn.addEventListener("click", () => {
        const task = taskInput.value.trim();
        if (!task) return;

        addToHistory(task);

        // Reset UI
        flowSection.style.display = "block";
        gallerySection.style.display = "none";
        extractionPanel.style.display = "none";
        extractionPreview.innerText = "";
        statusIndicator.innerText = "Agent is preparing...";
        flowGrid.innerHTML = "";
        galleryGrid.innerHTML = "";
        cardsMap = {};

        // Compile manual plan just in case LLM is off
        let override_plan = [];
        if (doExcel.checked) override_plan.push("write_excel");
        if (doWord.checked) override_plan.push("generate_report_doc");
        if (doPdf.checked) override_plan.push("generate_pdf");

        // Connect WebSocket
        let wsHost = window.location.host;
        let wsProtocol = window.location.protocol === "https:" ? "wss://" : "ws://";
        
        // Handle local file access or live-server testing
        if (!wsHost || window.location.protocol === "file:" || window.location.port !== "8000") {
            wsHost = "127.0.0.1:8000";
            wsProtocol = "ws://";
        }
        
        const wsUrl = `${wsProtocol}${wsHost}/ws/agent`;
        socket = new WebSocket(wsUrl);

        socket.onopen = () => {
            statusIndicator.innerText = "Connection established. Initiating sequence...";
            runBtn.disabled = true;
            runBtn.innerText = "Executing...";
            
            socket.send(JSON.stringify({
                task: task,
                use_llm: useLlm.checked,
                plan: override_plan
            }));
        };

        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            
            if (data.type === "plan") {
                statusIndicator.innerText = "Execution Plan Generated";
                // Pre-create cards for plan
                data.plan.forEach(step => {
                    createStepCard(step);
                });
            } else if (data.type === "log") {
                updateStepCard(data.step, data.status, data.msg);
                
                if (data.preview_data) {
                    extractionPanel.style.display = "block";
                    extractionPreview.innerText = JSON.stringify(data.preview_data, null, 4);
                }

                if (data.screenshot) {
                    addScreenshot(data.step, data.screenshot);
                }
            } else if (data.type === "done") {
                statusIndicator.innerText = "Execution Concluded Successfully";
                statusIndicator.style.color = "var(--text-primary)";
                finishRun();
            } else if (data.type === "error") {
                statusIndicator.innerText = `Error: ${data.msg}`;
                statusIndicator.style.color = "#ff4d4d";
                finishRun();
            }
        };

        socket.onerror = (error) => {
            console.error(error);
            statusIndicator.innerText = "Connection Error.";
            finishRun();
        };

        socket.onclose = () => {
            finishRun();
        };
    });

    function createStepCard(stepName) {
        if (cardsMap[stepName]) return;

        const card = document.createElement("div");
        card.className = "step-card";
        
        let displayTitle = stepName.replace(/_/g, " ").replace(/\b\w/g, l => l.toUpperCase());

        card.innerHTML = `
            <div class="step-title">${displayTitle}</div>
            <div class="step-msg">Pending execution</div>
            <div class="step-status-lbl">Waiting</div>
        `;
        
        flowGrid.appendChild(card);
        cardsMap[stepName] = card;
    }

    function updateStepCard(stepName, status, msg) {
        if (!cardsMap[stepName]) {
            createStepCard(stepName);
        }

        const card = cardsMap[stepName];
        card.className = `step-card ${status}`;
        
        card.querySelector(".step-msg").innerText = msg;
        card.querySelector(".step-status-lbl").innerText = status;
    }

    function addScreenshot(stepName, url) {
        gallerySection.style.display = "block";
        
        let displayTitle = stepName.replace(/write_/, "").replace(/generate_report_/, "").replace(/generate_/, "").replace(/_/g, " ");
        displayTitle = displayTitle.charAt(0).toUpperCase() + displayTitle.slice(1) + " Capture";

        const item = document.createElement("div");
        item.className = "gallery-item";
        
        item.innerHTML = `
            <img src="${url}" class="gallery-img" alt="Screenshot" onload="this.style.opacity=1" style="opacity:0; transition: opacity 0.5s;">
            <div class="gallery-label">${displayTitle}</div>
        `;
        
        galleryGrid.appendChild(item);
    }

    function finishRun() {
        runBtn.disabled = false;
        runBtn.innerText = "Execute Plan";
        if (socket && socket.readyState === WebSocket.OPEN) {
            socket.close();
        }
    }
});
