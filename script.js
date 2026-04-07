const revealItems = document.querySelectorAll('.reveal');
const tiltCards = document.querySelectorAll('.tilt-card');
const heroFrame = document.querySelector('.hero-frame');
const heroSigil = document.querySelector('.hero-sigil');

const revealObserver = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
      }
    });
  },
  {
    threshold: 0.22,
  }
);

revealItems.forEach((item) => revealObserver.observe(item));

tiltCards.forEach((card) => {
  card.addEventListener('mousemove', (event) => {
    const rect = card.getBoundingClientRect();
    const offsetX = (event.clientX - rect.left) / rect.width - 0.5;
    const offsetY = (event.clientY - rect.top) / rect.height - 0.5;
    const rotateY = offsetX * 8;
    const rotateX = offsetY * -8;

    card.style.transform = `perspective(900px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-4px)`;
    card.style.boxShadow = '0 32px 72px rgba(91, 174, 173, 0.22)';
  });

  card.addEventListener('mouseleave', () => {
    card.style.transform = '';
    card.style.boxShadow = '';
  });
});

if (heroFrame && heroSigil) {
  heroFrame.addEventListener('pointermove', (event) => {
    const rect = heroFrame.getBoundingClientRect();
    const relativeX = ((event.clientX - rect.left) / rect.width) * 100;
    const relativeY = ((event.clientY - rect.top) / rect.height) * 100;
    const offsetX = (event.clientX - rect.left) / rect.width - 0.5;
    const offsetY = (event.clientY - rect.top) / rect.height - 0.5;

    heroFrame.style.setProperty('--pointer-x', `${relativeX}%`);
    heroFrame.style.setProperty('--pointer-y', `${relativeY}%`);
    heroSigil.style.transform = `translateY(-50%) translate(${offsetX * 14}px, ${offsetY * 14}px)`;
  });

  heroFrame.addEventListener('pointerleave', () => {
    heroFrame.style.setProperty('--pointer-x', '50%');
    heroFrame.style.setProperty('--pointer-y', '50%');
    heroSigil.style.transform = '';
  });
}
