// PASSWORD VISIBILITY TOGGLE
document.querySelectorAll('[data-toggle="password"]').forEach(button => {
    button.addEventListener('click', () => {
        const input = document.getElementById(button.dataset.target);
        if (input.type === 'password') {
            input.type = 'text';
            button.textContent = 'Hide';
        } else {
            input.type = 'password';
            button.textContent = 'Show';
        }
    });
});





// PULSE ANIMATION ON HEADINGS WHEN PAGE LOADS
window.addEventListener('load', () => {
  document.querySelectorAll('.form-heading').forEach(h => {
    h.classList.add('animate-pulse');
    setTimeout(() => h.classList.remove('animate-pulse'), 2000);
  });
});





// ADD CLICK SOUND EFFECT TO ALL INPUT ELEMENTS
document.addEventListener('DOMContentLoaded', () => {
  const clickSound = new Audio("./../static/audio/button-click.wav");
  document.querySelectorAll('input').forEach(input => {
    input.addEventListener('click', () => {
      clickSound.play();
    });
  });
});





// FORM VALIDATION TO ENSURE THAT PASSWORD MATCHES PASSWORD CONFIRMATION IN THE REGISTRATION FORM
document.querySelector('form').addEventListener('submit', function(e) {
    const password = document.getElementById('register-password');
    const confirm = document.getElementById('register-confirm');
    
    if (password.value !== confirm.value) {
        e.preventDefault();
        alert('Passwords do not match!');
    }
});
