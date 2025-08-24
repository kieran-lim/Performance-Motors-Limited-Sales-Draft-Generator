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

// CUSTOM PACKAGES FUNCTIONALITY
document.addEventListener('DOMContentLoaded', function() {
    const addCustomPackageBtn = document.getElementById('add-custom-package');
    const customPackagesContainer = document.getElementById('custom-packages-container');
    
    if (addCustomPackageBtn && customPackagesContainer) {
        // Add new custom package field with animation
        addCustomPackageBtn.addEventListener('click', function() {
            const newPackageItem = document.createElement('div');
            newPackageItem.className = 'custom-package-item group relative';
            newPackageItem.style.opacity = '0';
            newPackageItem.style.transform = 'translateY(-20px)';
            
            newPackageItem.innerHTML = `
                <div class="flex items-center p-4 bg-gray-700 bg-opacity-50 rounded-lg border border-gray-600 hover:border-[#39FF14] transition-all duration-300 hover:shadow-lg hover:shadow-[#39FF14]/20">
                    <div class="flex-1 min-w-0 pr-3">
                        <input type="text" name="custom_packages[]" placeholder="Enter custom package name" 
                            class="w-full px-3 py-2 bg-transparent border-none focus:outline-none focus:ring-0 placeholder-gray-400 text-white text-sm custom-package-input" />
                    </div>
                    <div class="flex-shrink-0">
                        <button type="button" class="remove-custom-package opacity-0 group-hover:opacity-100 px-3 py-2 bg-red-600 text-white rounded-md text-xs hover:bg-red-500 hover:scale-105 active:scale-95 transition-all duration-200 flex items-center space-x-1.5 shadow-sm hover:shadow-md">
                            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                            </svg>
                            <span>Remove</span>
                        </button>
                    </div>
                </div>
            `;
            
            customPackagesContainer.appendChild(newPackageItem);
            
            // Animate the new item in
            setTimeout(() => {
                newPackageItem.style.transition = 'all 0.3s ease-out';
                newPackageItem.style.opacity = '1';
                newPackageItem.style.transform = 'translateY(0)';
            }, 10);
            
            // Add click sound to new input
            const newInput = newPackageItem.querySelector('input');
            const clickSound = new Audio("./../static/audio/button-click.wav");
            
            newInput.addEventListener('click', () => {
                clickSound.play().catch(e => console.log('Audio play failed:', e));
            });
            
            // Add focus effects and remove button visibility
            newInput.addEventListener('focus', function() {
                this.closest('.custom-package-item').querySelector('div').classList.add('ring-2', 'ring-[#39FF14]', 'ring-opacity-50');
                // Always show remove button for additional packages
                const removeBtn = this.closest('.custom-package-item').querySelector('.remove-custom-package');
                if (removeBtn) {
                    removeBtn.style.opacity = '1';
                    removeBtn.style.pointerEvents = 'auto';
                }
            });
            
            newInput.addEventListener('blur', function() {
                this.closest('.custom-package-item').querySelector('div').classList.remove('ring-2', 'ring-[#39FF14]', 'ring-opacity-50');
            });
            
            // Show remove button when typing
            newInput.addEventListener('input', function() {
                const removeBtn = this.closest('.custom-package-item').querySelector('.remove-custom-package');
                if (removeBtn) {
                    removeBtn.style.opacity = '1';
                    removeBtn.style.pointerEvents = 'auto';
                }
            });
            
            // Add remove functionality to new remove button with animation
            const removeBtn = newPackageItem.querySelector('.remove-custom-package');
            removeBtn.addEventListener('click', function() {
                const item = this.closest('.custom-package-item');
                item.style.transition = 'all 0.3s ease-in';
                item.style.opacity = '0';
                item.style.transform = 'translateX(100px)';
                setTimeout(() => {
                    item.remove();
                }, 300);
            });
            
            // Focus the new input
            setTimeout(() => {
                newInput.focus();
            }, 350);
        });
        
        // Add remove functionality to initial remove button (if it exists)
        const initialRemoveBtn = customPackagesContainer.querySelector('.remove-custom-package');
        if (initialRemoveBtn) {
            initialRemoveBtn.addEventListener('click', function() {
                const packageItem = this.closest('.custom-package-item');
                if (packageItem) {
                    packageItem.style.transition = 'all 0.3s ease-in';
                    packageItem.style.opacity = '0';
                    packageItem.style.transform = 'translateX(100px)';
                    setTimeout(() => {
                        packageItem.remove();
                    }, 300);
                }
            });
        }
        
        // Show/hide initial remove button based on input content
        const initialInput = customPackagesContainer.querySelector('input[name="custom_packages[]"]');
        if (initialInput && initialRemoveBtn) {
            // Function to check and show/hide remove button
            function updateRemoveButtonVisibility() {
                if (initialInput.value.trim()) {
                    initialRemoveBtn.style.opacity = '1';
                    initialRemoveBtn.style.pointerEvents = 'auto';
                } else {
                    initialRemoveBtn.style.opacity = '0';
                    initialRemoveBtn.style.pointerEvents = 'none';
                }
            }
            
            // Check on page load
            updateRemoveButtonVisibility();
            
            // Show remove button when input has content
            initialInput.addEventListener('input', updateRemoveButtonVisibility);
            
            // Show remove button on focus if there's content
            initialInput.addEventListener('focus', function() {
                this.closest('.custom-package-item').querySelector('div').classList.add('ring-2', 'ring-[#39FF14]', 'ring-opacity-50');
                updateRemoveButtonVisibility();
            });
            
            initialInput.addEventListener('blur', function() {
                this.closest('.custom-package-item').querySelector('div').classList.remove('ring-2', 'ring-[#39FF14]', 'ring-opacity-50');
                updateRemoveButtonVisibility();
            });
        }
        
        // Add whoosh sound effect to add button (only on actual click)
        addCustomPackageBtn.addEventListener('click', function() {
            const whooshSound = new Audio("./../static/audio/812682__audiopapkin__sound-design-elements-whoosh-sfx-045.wav");
            whooshSound.volume = 0.4;
            whooshSound.play().catch(e => console.log('Audio play failed:', e));
        });
        
        // Add fantasy sound effect to create draft button
        const createDraftBtn = document.querySelector('button[type="submit"]');
        if (createDraftBtn) {
            createDraftBtn.addEventListener('click', function() {
                const fantasySound = new Audio("./../static/audio/376746__zenithinfinitivestudios__fantasy_ui_button_2.wav");
                fantasySound.volume = 0.5;
                fantasySound.play().catch(e => console.log('Audio play failed:', e));
            });
        }
    }
});