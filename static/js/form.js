// REVEAL OPTIONAL SECTIONS
const tradeChk   = document.getElementById('tradein-checkbox');
const financeChk = document.getElementById('finance-checkbox');

tradeChk.addEventListener('change', () => {
  document.getElementById('tradein-fields').classList.toggle('hidden', !tradeChk.checked);
  updateCalculations();
});
financeChk.addEventListener('change', () => {
  document.getElementById('finance-fields').classList.toggle('hidden', !financeChk.checked);
  updateCalculations();
});





// ELEMENT REFERENCES (match your underscore IDs)
const retailInput        = document.getElementById('retail_price');
const discountInput      = document.getElementById('discount');
const addonsInput        = document.getElementById('addons');
const netInput           = document.getElementById('net_price');
const downpaymentInput   = document.getElementById('downpayment');

const tradePriceInput       = document.getElementById('tradein_price');
const tradeOutstandingInput = document.getElementById('tradein_outstanding');
const tradeBalanceInput     = document.getElementById('tradein_balance');
const tradePlateInput       = document.getElementById('tradein_plate');

const financeLoanInput    = document.getElementById('finance_loan');
const financeRateInput    = document.getElementById('finance_rate');
const financeTenureInput  = document.getElementById('finance_tenure');
const financeMonthlyInput = document.getElementById('finance_monthly');





// optional—keeps JS and HTML in sync
netInput.readOnly = true;

// ddd flags for manual editing
let manualNet = false;
let manualDiscount = false;

// set flags on focus/blur for net price
netInput.addEventListener('focus', () => { manualNet = true; });
netInput.addEventListener('blur', () => { 
  manualNet = false; 
  updateCalculations(); 
});

// set flags on focus/blur for discount
discountInput.addEventListener('focus', () => { manualDiscount = true; });
discountInput.addEventListener('blur', () => { 
  manualDiscount = false; 
  updateCalculations(); 
});

// when net price is manually changed, update discount if not manually edited
netInput.addEventListener('input', () => {
  const r = parseFloat(retailInput.value) || 0;
  const n = parseFloat(netInput.value) || 0;
  if (!manualDiscount) {
    discountInput.value = Math.max(r - n, 0);
  }
  updateCalculations();
});

// add keydown listener to clear net price on single backspace press
netInput.addEventListener('keydown', (e) => {
  if (e.key === "Backspace" && netInput.value !== "") {
    e.preventDefault();
    netInput.value = "";
    updateCalculations();
  }
});

// When discount is manually changed, update net price if not manually edited
discountInput.addEventListener('input', () => {
  const r = parseFloat(retailInput.value) || 0;
  const d = parseFloat(discountInput.value) || 0;
  if (!manualNet) {
    netInput.value = Math.max(r - d, 0);
  }
  updateCalculations();
});





// CALCULATION LOGIC
function updateCalculations() {
  // lock/unlock net price
  if (retailInput.value.trim() !== '') {
    netInput.readOnly = false;
    // Remove lock classes and ensure glow is applied
    netInput.classList.remove('bg-gray-600','opacity-50','cursor-not-allowed','focus-glow');
    netInput.classList.add('bg-gray-700','opacity-100','cursor-text','focus-glow');
  } else {
    netInput.readOnly = true;
    netInput.value    = '';
    // Remove glow effect when locked
    netInput.classList.remove('bg-gray-700','opacity-100','cursor-text','focus-glow');
    netInput.classList.add('bg-gray-600','opacity-50','cursor-not-allowed');
  }

  // 1) net price calculation
  const retail   = parseFloat(retailInput.value)   || 0;
  const discount = parseFloat(discountInput.value) || 0;
  const addons   = parseFloat(addonsInput.value)   || 0;
  let net = Math.max(retail - discount + addons, 0);

  // 2) trade-in balance calculation
  let tradeBalance = 0;
  if (tradeChk.checked) {
    const price       = parseFloat(tradePriceInput.value)       || 0;
    const outstanding = parseFloat(tradeOutstandingInput.value) || 0;
    tradeBalance = Math.max(price - outstanding, 0);
  }
  tradeBalanceInput.value = Math.round(tradeBalance).toLocaleString('en-US', {
    style: 'currency', currency: 'USD', maximumFractionDigits: 0
  });

  // 3) monthly installment calculation
  let monthlyInstallment = 0;
  if (financeChk.checked) {
    const loan   = parseFloat(financeLoanInput.value)   || 0;
    const rate   = parseFloat(financeRateInput.value)   || 0;
    const tenure = parseFloat(financeTenureInput.value) || 0;

    if (loan > 0 && rate > 0 && tenure > 0) {
      const monthlyRate = rate / 1200;  // annual % to monthly decimal
      monthlyInstallment = (loan + (loan * monthlyRate * tenure)) / tenure;
    }
  }
  financeMonthlyInput.value = monthlyInstallment
    ? Math.round(monthlyInstallment).toLocaleString('en-US', {
        style: 'currency', currency: 'USD', maximumFractionDigits: 0
      })
    : '';

  // 4) update net price only if not manually modified
  if (!manualNet) {
    netInput.value = Math.round(net).toLocaleString('en-US', {
      style: 'currency', currency: 'USD', maximumFractionDigits: 0
    });
  }

  // 5) downpayment calculation
  const loanAmt = financeChk.checked
    ? (parseFloat(financeLoanInput.value) || 0)
    : 0;
  const down = Math.max(net - loanAmt - tradeBalance, 0);
  downpaymentInput.value = Math.round(down).toLocaleString('en-US', {
    style: 'currency', currency: 'USD', maximumFractionDigits: 0
  });
}

// --- Wire up inputs ---
[
  retailInput,
  discountInput,
  addonsInput,
  tradePriceInput,
  tradeOutstandingInput,
  tradePlateInput,
  financeLoanInput,
  financeRateInput,
  financeTenureInput
].forEach(el => el && el.addEventListener('input', updateCalculations));

// initial calculation
updateCalculations();





// CLICK SOUND FUNCTIONALITY
document.addEventListener('DOMContentLoaded', () => {
  const clickSound       = new Audio("./../static/audio/button-click.wav");
  const clickSoundEffect = new Audio("./../static/audio/click.mp3");
  // include all non-readonly inputs
  document.querySelectorAll('input:not([readonly])').forEach(input => {
    input.addEventListener('click', () => {
      clickSound.play();
      clickSoundEffect.play();
    });
  });
  // explicitly add click sound for net price if it's unlocked
  if (netInput) {
    netInput.addEventListener('click', () => {
      if (!netInput.readOnly) {
        clickSound.play();
        clickSoundEffect.play();
      }
    });
  }
});





// FORM  VALIDATION LOGIC
document.addEventListener('DOMContentLoaded', function() {
    // Get checkboxes and their respective field groups
    const tradeinCheckbox = document.getElementById('tradein-checkbox');
    const financeCheckbox = document.getElementById('finance-checkbox');
    const tradeinFields = document.getElementById('tradein-fields');
    const financeFields = document.getElementById('finance-fields');
    
    // get all inputs that require validation
    const tradeinRequiredInputs = document.querySelectorAll('[data-tradein-required]');
    const financeRequiredInputs = document.querySelectorAll('[data-finance-required]');

    // function to toggle required attribute
    function toggleRequired(inputs, required) {
        inputs.forEach(input => {
            if (required) {
                input.setAttribute('required', '');
            } else {
                input.removeAttribute('required');
            }
        });
    }

    // handle trade-in checkbox
    tradeinCheckbox.addEventListener('change', function() {
        tradeinFields.classList.toggle('hidden', !this.checked);
        toggleRequired(tradeinRequiredInputs, this.checked);
        if (!this.checked) {
            tradeinRequiredInputs.forEach(input => input.value = '');
        }
    });

    // handle finance checkbox
    financeCheckbox.addEventListener('change', function() {
        financeFields.classList.toggle('hidden', !this.checked);
        toggleRequired(financeRequiredInputs, this.checked);
        if (!this.checked) {
            financeRequiredInputs.forEach(input => input.value = '');
        }
    });

    // validate form before submission
    document.getElementById('sales-form').addEventListener('submit', function(e) {
        const numberInputs = document.querySelectorAll('input[type="number"]');
        let hasError = false;

        numberInputs.forEach(input => {
            if (input.hasAttribute('required') && input.value !== '') {
                const value = parseFloat(input.value);
                const min = parseFloat(input.min);

                // for outstanding loan field, allow value equal to min.
                if (input.id === 'tradein_outstanding') {
                    if (!isNaN(min) && value < min) {
                        alert(`${input.previousElementSibling.textContent} must be at least ${min}`);
                        hasError = true;
                    }
                } else {
                    if (!isNaN(min) && value <= min) {
                        alert(`${input.previousElementSibling.textContent} must be greater than ${min}`);
                        hasError = true;
                    }
                }
            }
        });

        if (hasError) {
            e.preventDefault();
        }
    });
});