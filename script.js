const revealItems = document.querySelectorAll('.reveal');
const tiltCards = document.querySelectorAll('.tilt-card');
const heroFrame = document.querySelector('.hero-frame');
const heroSigil = document.querySelector('.hero-sigil');
const missionFrame = document.querySelector('.mission-frame');

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

const missionPanel = document.querySelector('.mission-panel');
const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

const runMissionSequence = () => {
  if (!missionPanel || missionPanel.dataset.sequenceStarted === 'true') {
    return;
  }

  missionPanel.dataset.sequenceStarted = 'true';
  missionPanel.classList.add('sequence-headline');

  if (prefersReducedMotion) {
    missionPanel.classList.add('sequence-network', 'sequence-cta');
    return;
  }

  window.setTimeout(() => {
    missionPanel.classList.add('sequence-network');
  }, 420);

  window.setTimeout(() => {
    missionPanel.classList.add('sequence-cta');
  }, 1320);
};

revealItems.forEach((item) => revealObserver.observe(item));

if (missionPanel) {
  const missionSequenceObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          runMissionSequence();
        }
      });
    },
    {
      threshold: 0.28,
    }
  );

  missionSequenceObserver.observe(missionPanel);
}

tiltCards.forEach((card) => {
  card.addEventListener('mousemove', (event) => {
    const rect = card.getBoundingClientRect();
    const offsetX = (event.clientX - rect.left) / rect.width - 0.5;
    const offsetY = (event.clientY - rect.top) / rect.height - 0.5;
    const isMissionCard = Boolean(card.closest('.mission-panel'));
    const rotateScale = isMissionCard ? 4.5 : 8;
    const lift = isMissionCard ? -2 : -4;
    const rotateY = offsetX * rotateScale;
    const rotateX = offsetY * -rotateScale;
    const shadow = isMissionCard
      ? '0 24px 52px rgba(91, 174, 173, 0.16)'
      : '0 32px 72px rgba(91, 174, 173, 0.22)';

    card.style.transform = `perspective(900px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(${lift}px)`;
    card.style.boxShadow = shadow;
  });

  card.addEventListener('mouseleave', () => {
    card.style.transform = '';
    card.style.boxShadow = '';
  });
});

if (missionFrame && window.matchMedia('(hover: hover) and (pointer: fine)').matches && !prefersReducedMotion) {
  missionFrame.addEventListener('pointermove', (event) => {
    const rect = missionFrame.getBoundingClientRect();
    const relativeX = ((event.clientX - rect.left) / rect.width) * 100;
    const relativeY = ((event.clientY - rect.top) / rect.height) * 100;
    const offsetX = (event.clientX - rect.left) / rect.width - 0.5;
    const offsetY = (event.clientY - rect.top) / rect.height - 0.5;

    missionFrame.style.setProperty('--mission-x', `${relativeX}%`);
    missionFrame.style.setProperty('--mission-y', `${relativeY}%`);
    missionFrame.style.setProperty('--mission-parallax-x', `${offsetX * 8}px`);
    missionFrame.style.setProperty('--mission-parallax-y', `${offsetY * 8}px`);
    missionFrame.style.setProperty('--mission-parallax-bg-x', `${offsetX * 3.5}px`);
    missionFrame.style.setProperty('--mission-parallax-bg-y', `${offsetY * 3.5}px`);
  });

  missionFrame.addEventListener('pointerleave', () => {
    missionFrame.style.setProperty('--mission-x', '50%');
    missionFrame.style.setProperty('--mission-y', '34%');
    missionFrame.style.setProperty('--mission-parallax-x', '0px');
    missionFrame.style.setProperty('--mission-parallax-y', '0px');
    missionFrame.style.setProperty('--mission-parallax-bg-x', '0px');
    missionFrame.style.setProperty('--mission-parallax-bg-y', '0px');
  });
}

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
