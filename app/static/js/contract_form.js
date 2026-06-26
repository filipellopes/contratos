document.addEventListener("DOMContentLoaded", () => {
    const container = document.getElementById("contratantes-container");
    const addBtn = document.getElementById("btn-add-contratante");
    const totalEl = document.getElementById("valor-total");
    const empresaSelect = document.getElementById("empresa_contratada_id");

    if (window.applyMasks) applyMasks(document);

    function reindexContratantes() {
        container.querySelectorAll(".contratante-row").forEach((row, index) => {
            row.dataset.index = index;
            row.querySelector(".contratante-num").textContent = index + 1;
            row.querySelectorAll("[name^='contratantes']").forEach((input) => {
                input.name = input.name.replace(/contratantes\[\d+\]/, `contratantes[${index}]`);
            });
            const removeBtn = row.querySelector(".btn-remove-contratante");
            removeBtn.disabled = index === 0;
        });
        updateTotal();
    }

    function updateTotal() {
        let total = 0;
        container.querySelectorAll(".contratante-valor").forEach((input) => {
            total += parseCurrency(input.value);
        });
        totalEl.textContent = total.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
    }

    function cloneContratanteRow() {
        const firstRow = container.querySelector(".contratante-row");
        const clone = firstRow.cloneNode(true);
        clone.querySelectorAll("input").forEach((input) => {
            input.value = "";
        });
        clone.querySelectorAll("select").forEach((select) => {
            select.selectedIndex = 0;
        });
        container.appendChild(clone);
        if (window.applyMasks) applyMasks(clone);
        clone.querySelector(".contratante-valor").addEventListener("input", updateTotal);
        reindexContratantes();
    }

    if (addBtn) {
        addBtn.addEventListener("click", cloneContratanteRow);
    }

    container.addEventListener("click", (event) => {
        if (event.target.classList.contains("btn-remove-contratante")) {
            const rows = container.querySelectorAll(".contratante-row");
            if (rows.length <= 1) return;
            event.target.closest(".contratante-row").remove();
            reindexContratantes();
        }
    });

    container.addEventListener("input", (event) => {
        if (event.target.classList.contains("contratante-valor")) {
            updateTotal();
        }
    });

    if (empresaSelect) {
        empresaSelect.addEventListener("change", async () => {
            const id = empresaSelect.value;
            if (!id) return;
            try {
                const response = await fetch(`/empresas-contratadas/api/${id}`);
                if (!response.ok) return;
                const data = await response.json();
                document.getElementById("cnpj_contratada").value = data.cnpj_formatted || data.cnpj || "";
                document.getElementById("endereco_contratado").value = data.address || "";
                document.getElementById("nome_contratado").value = data.responsible_name || "";
                document.getElementById("cpf_contratado").value = data.responsible_cpf_formatted || data.responsible_cpf || "";
                document.getElementById("crc_contratado").value = data.crc || "";
            } catch (err) {
                console.error("Erro ao carregar empresa:", err);
            }
        });
    }

    reindexContratantes();
});
