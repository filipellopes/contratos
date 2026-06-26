function onlyDigits(value) {
    return (value || "").replace(/\D/g, "");
}

function formatCNPJ(value) {
    const d = onlyDigits(value).slice(0, 14);
    return d
        .replace(/^(\d{2})(\d)/, "$1.$2")
        .replace(/^(\d{2})\.(\d{3})(\d)/, "$1.$2.$3")
        .replace(/\.(\d{3})(\d)/, ".$1/$2")
        .replace(/(\d{4})(\d)/, "$1-$2");
}

function formatCPF(value) {
    const d = onlyDigits(value).slice(0, 11);
    return d
        .replace(/(\d{3})(\d)/, "$1.$2")
        .replace(/(\d{3})(\d)/, "$1.$2")
        .replace(/(\d{3})(\d{1,2})$/, "$1-$2");
}

function formatCurrencyInput(value) {
    const digits = onlyDigits(value);
    if (!digits) return "";
    const number = parseInt(digits, 10) / 100;
    return number.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

function parseCurrency(value) {
    if (!value) return 0;
    const cleaned = value.replace(/[^\d,.-]/g, "").replace(/\./g, "").replace(",", ".");
    const num = parseFloat(cleaned);
    return isNaN(num) ? 0 : num;
}

function applyMasks(root) {
    root.querySelectorAll(".mask-cnpj").forEach((input) => {
        input.addEventListener("input", () => {
            input.value = formatCNPJ(input.value);
        });
    });
    root.querySelectorAll(".mask-cpf").forEach((input) => {
        input.addEventListener("input", () => {
            input.value = formatCPF(input.value);
        });
    });
    root.querySelectorAll(".mask-currency").forEach((input) => {
        input.addEventListener("input", () => {
            input.value = formatCurrencyInput(input.value);
        });
    });
}

window.applyMasks = applyMasks;
document.addEventListener("DOMContentLoaded", () => applyMasks(document));
