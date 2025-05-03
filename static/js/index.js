// PARALLAX BACKGROUND EFFECT
document.addEventListener('DOMContentLoaded', () => {
  try {
    console.log('Initializing parallax effect...');
    const parallaxEls = document.querySelectorAll('[data-parallax]');
    console.log('Found parallax elements:', parallaxEls.length);

    if (parallaxEls.length === 0) {
      console.warn('No elements with data-parallax attribute found');
    }

    window.addEventListener('mousemove', e => {
      const x = (e.clientX / window.innerWidth - 0.5) * 2;
      const y = (e.clientY / window.innerHeight - 0.5) * 2;
      
      parallaxEls.forEach(el => {
        if (!el.style.transition) {
          el.style.transition = 'transform 0.2s cubic-bezier(0.25, 0.46, 0.45, 0.94)';
        }
        const depth = parseFloat(el.dataset.depth || '0.8'); // increased default depth
        const moveX = x * depth * 50; // increased multiplier
        const moveY = y * depth * 50; // increased multiplier
        el.style.transform = `translate(${moveX}px, ${moveY}px) scale(1.1)`; // increased scale
      });
    });
  } catch (error) {
    console.error('Error initializing parallax:', error);
  }
});