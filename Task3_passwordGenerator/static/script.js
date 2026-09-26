/**
 * Password Generator - Client-side UI Controller
 * Handles browser interactions and communicates with the Python Flask backend.
 */

document.addEventListener("DOMContentLoaded", () => {
    // DOM Elements
    const passwordBox = document.getElementById("passwordBox");
    const passwordDisplay = document.getElementById("passwordDisplay");
    const copyBtn = document.getElementById("copyBtn");
    const copyStatus = document.getElementById("copyStatus");
    const strengthVal = document.getElementById("strengthVal");
    const strengthBarFill = document.getElementById("strengthBarFill");
    const lengthSlider = document.getElementById("lengthSlider");
    const lengthDisplay = document.getElementById("lengthDisplay");

    const checkUpper = document.getElementById("checkUpper");
    const checkLower = document.getElementById("checkLower");
    const checkNumbers = document.getElementById("checkNumbers");
    const checkSymbols = document.getElementById("checkSymbols");

    const rowUpper = document.getElementById("rowUpper");
    const rowLower = document.getElementById("rowLower");
    const rowNumbers = document.getElementById("rowNumbers");
    const rowSymbols = document.getElementById("rowSymbols");

    const generateBtn = document.getElementById("generateBtn");
    const resetBtn = document.getElementById("resetBtn");

    let currentPassword = "";
    let copyTimeout = null;

    // 1. Slider Interaction: updates length display in real-time
    lengthSlider.addEventListener("input", (e) => {
        lengthDisplay.textContent = e.target.value;
    });

    // 2. Clickable Row toggles
    function setupRowToggle(rowElement, checkboxElement) {
        rowElement.addEventListener("click", (e) => {
            // Prevent double toggle if the input or switch slider itself was clicked
            if (e.target.tagName !== "INPUT" && !e.target.classList.contains("switch-slider")) {
                checkboxElement.checked = !checkboxElement.checked;
            }
        });
    }

    setupRowToggle(rowUpper, checkUpper);
    setupRowToggle(rowLower, checkLower);
    setupRowToggle(rowNumbers, checkNumbers);
    setupRowToggle(rowSymbols, checkSymbols);

    // 3. Generate Password via Python Flask Backend
    async function requestPasswordGeneration() {
        const payload = {
            length: parseInt(lengthSlider.value, 10),
            uppercase: checkUpper.checked,
            lowercase: checkLower.checked,
            numbers: checkNumbers.checked,
            symbols: checkSymbols.checked
        };

        // Client-side quick check
        if (!payload.uppercase && !payload.lowercase && !payload.numbers && !payload.symbols) {
            showError("Please select at least one character type.");
            return;
        }

        try {
            generateBtn.disabled = true;
            generateBtn.style.opacity = "0.75";

            const response = await fetch("/api/generate", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(payload)
            });

            const result = await response.json();

            if (response.ok && result.success) {
                currentPassword = result.password;

                // Update password display
                passwordDisplay.textContent = result.password;
                passwordDisplay.className = "password-text";

                // Update strength
                strengthVal.textContent = result.strength.label;
                strengthVal.style.color = result.strength.color;
                strengthBarFill.style.width = `${Math.round(result.strength.score * 100)}%`;
                strengthBarFill.style.backgroundColor = result.strength.color;

                // Reset copy feedback if idle
                resetCopyFeedback();
            } else {
                showError(result.error || "Failed to generate password.");
            }
        } catch (err) {
            showError("Server connection error. Please try again.");
        } finally {
            generateBtn.disabled = false;
            generateBtn.style.opacity = "1";
        }
    }

    function showError(message) {
        currentPassword = "";
        passwordDisplay.textContent = message;
        passwordDisplay.className = "password-text error-text";

        strengthVal.textContent = "Invalid";
        strengthVal.style.color = "#EF4444";
        strengthBarFill.style.width = "0%";
        strengthBarFill.style.backgroundColor = "#EF4444";

        copyStatus.textContent = "Cannot copy empty password";
        copyStatus.className = "password-status error-status";
    }

    generateBtn.addEventListener("click", requestPasswordGeneration);

    // 4. Copy to Clipboard Functionality
    async function copyToClipboard() {
        if (!currentPassword) return;

        try {
            if (navigator.clipboard && window.isSecureContext) {
                await navigator.clipboard.writeText(currentPassword);
            } else {
                // Fallback for non-https / older browsers
                const textArea = document.createElement("textarea");
                textArea.value = currentPassword;
                textArea.style.position = "fixed";
                textArea.style.left = "-999999px";
                document.body.appendChild(textArea);
                textArea.focus();
                textArea.select();
                document.execCommand("copy");
                textArea.remove();
            }

            // Visual feedback
            copyStatus.textContent = "✓ Password copied to clipboard!";
            copyStatus.className = "password-status copied";

            copyBtn.classList.add("copied");
            copyBtn.innerHTML = '<span class="copy-icon">✓</span><span class="copy-btn-text">Copied!</span>';

            if (copyTimeout) clearTimeout(copyTimeout);
            copyTimeout = setTimeout(resetCopyFeedback, 2000);
        } catch (err) {
            copyStatus.textContent = "Copy failed. Please manually select text.";
        }
    }

    function resetCopyFeedback() {
        copyStatus.textContent = "Click to copy";
        copyStatus.className = "password-status";

        copyBtn.classList.remove("copied");
        copyBtn.innerHTML = '<span class="copy-icon">📋</span><span class="copy-btn-text">Copy</span>';
    }

    passwordBox.addEventListener("click", copyToClipboard);
    passwordBox.addEventListener("keydown", (e) => {
        if (e.key === "Enter" || e.key === " ") {
            e.preventDefault();
            copyToClipboard();
        }
    });

    copyBtn.addEventListener("click", (e) => {
        e.stopPropagation(); // Avoid triggering double click on parent box
        copyToClipboard();
    });

    // 5. Reset to Defaults
    resetBtn.addEventListener("click", () => {
        lengthSlider.value = 16;
        lengthDisplay.textContent = "16";

        checkUpper.checked = true;
        checkLower.checked = true;
        checkNumbers.checked = true;
        checkSymbols.checked = false;

        currentPassword = "";
        passwordDisplay.textContent = "Your password will appear here";
        passwordDisplay.className = "password-text placeholder";

        strengthVal.textContent = "Not generated";
        strengthVal.style.color = "#64748B";
        strengthBarFill.style.width = "0%";
        strengthBarFill.style.backgroundColor = "#64748B";

        resetCopyFeedback();
    });
});
