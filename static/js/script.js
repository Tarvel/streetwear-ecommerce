function incrementQuantity(inputId) {
  const input = document.getElementById(inputId);
  const max = parseInt(input.max);
  const currentValue = parseInt(input.value);
  if (currentValue < max) {
    input.value = currentValue + 1;
  }
}

function decrementQuantity(inputId) {
  const input = document.getElementById(inputId);
  const min = parseInt(input.min);
  const currentValue = parseInt(input.value);
  if (currentValue > min) {
    input.value = currentValue - 1;
  }
}

function showToast(message) {
  const toast = document.getElementById("toast-message");
  toast.innerText = message;
  toast.classList.remove("hidden");
  setTimeout(() => {
    toast.classList.add("hidden");
  }, 3000);
}

function setActiveThumbnail(thumbnail) {
  const thumbnails = document.querySelectorAll('.cursor-pointer');
  thumbnails.forEach(img => img.classList.remove('ring-2', 'ring-accent', 'opacity-100'));
  thumbnail.classList.add('ring-2', 'ring-accent', 'opacity-100');
}

document.addEventListener('DOMContentLoaded', () => {
  const flashMessages = document.querySelectorAll('.flash-message');
  flashMessages.forEach((msg, index) => {
    setTimeout(() => {
      msg.classList.remove('opacity-0', '-translate-y-12', 'md:translate-x-full');
    }, 100 + (index * 200));
    setTimeout(() => {
      msg.classList.add('opacity-0', '-translate-y-12', 'md:translate-x-full');
      setTimeout(() => {
        msg.remove();
      }, 500);
    }, 4000 + (index * 200));
  });

  const themeToggle = document.getElementById('theme-toggle');
  const themeIcon = document.getElementById('theme-icon');
  const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;

  themeToggle.addEventListener('click', () => {
    document.documentElement.classList.toggle('dark');
    themeIcon.classList.toggle('fa-moon');
    themeIcon.classList.toggle('fa-sun');
    fetch('/set-theme/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
      },
      body: JSON.stringify({
        theme: document.documentElement.classList.contains('dark') ? 'dark' : 'light'
      }),
    });
  });

  const searchModal = document.getElementById('search-modal');
  const closeModal = document.getElementById('close-modal');
  const searchToggleDesktop = document.getElementById('search-toggle-desktop');
  const searchToggleMobile = document.getElementById('search-toggle-mobile');

  const openSearchModal = () => searchModal.classList.remove('hidden');
  const closeSearchModal = () => searchModal.classList.add('hidden');

  searchToggleDesktop.addEventListener('click', openSearchModal);
  searchToggleMobile.addEventListener('click', openSearchModal);
  closeModal.addEventListener('click', closeSearchModal);

  searchModal.addEventListener('click', (e) => {
    if (e.target === searchModal) {
      closeSearchModal();
    }
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && !searchModal.classList.contains('hidden')) {
      closeSearchModal();
    }
  });

  const menuToggle = document.getElementById('menu-toggle');
  const closeMenu = document.getElementById('close-menu');
  const mobileMenu = document.getElementById('mobile-menu');
  const menuOverlay = document.getElementById('mobile-menu-overlay');

  const showMobileMenu = () => {
    mobileMenu.classList.remove('-translate-x-full');
    menuOverlay.classList.remove('hidden');
    document.body.classList.add('overflow-hidden');
  };

  const hideMobileMenu = () => {
    mobileMenu.classList.add('-translate-x-full');
    menuOverlay.classList.add('hidden');
    document.body.classList.remove('overflow-hidden');
  };

  menuToggle.addEventListener('click', showMobileMenu);
  closeMenu.addEventListener('click', hideMobileMenu);
  menuOverlay.addEventListener('click', hideMobileMenu);

  const container = document.getElementById('slideshow-container');
  if (container) {
    const slides = Array.from(container.querySelectorAll('.slide'));
    const controls = document.getElementById('slideshow-controls');
    const nextBtn = document.getElementById('next-slide-btn');
    const prevBtn = document.getElementById('prev-slide-btn');
    const indicatorsContainer = document.getElementById('slideshow-indicators');
    const autoPlayDelay = 3000;

    let currentIndex = 0;
    let slideInterval;

    if (slides.length <= 1) {
      if (slides.length === 1) {
        animateText(slides[0], true);
      }
      indicatorsContainer.remove();
      return;
    }

    controls.classList.remove('hidden');

    slides.forEach((_, index) => {
      const dot = document.createElement('button');
      dot.setAttribute('aria-label', `Go to slide ${index + 1}`);
      dot.classList.add('w-2.5', 'h-2.5', 'rounded-full', 'transition-all', 'duration-300', 'hover:bg-white');
      dot.classList.toggle('bg-white', index === 0);
      dot.classList.toggle('bg-white/40', index !== 0);
      dot.addEventListener('click', () => {
        if (index === currentIndex) return;
        showSlide(index);
        resetInterval();
      });
      indicatorsContainer.appendChild(dot);
    });
    const indicators = Array.from(indicatorsContainer.querySelectorAll('button'));

    function animateText(slide, show) {
      const textElements = slide.querySelectorAll('.slide-text');
      textElements.forEach(el => {
        el.classList.toggle('translate-y-full', !show);
      });
    }

    function showSlide(index) {
      const currentSlide = slides[currentIndex];
      const nextSlide = slides[index];

      animateText(currentSlide, false);

      currentSlide.classList.remove('opacity-100', 'z-10', 'scale-100');
      currentSlide.classList.add('opacity-0', 'z-0', 'scale-105');
      nextSlide.classList.remove('opacity-0', 'z-0', 'scale-95');
      nextSlide.classList.add('opacity-100', 'z-10', 'scale-100');

      setTimeout(() => {
        animateText(nextSlide, true);
      }, 350);
      setTimeout(() => {
        currentSlide.classList.remove('scale-105');
        currentSlide.classList.add('scale-95');
      }, 1000);

      indicators[currentIndex].classList.replace('bg-white', 'bg-white/40');
      indicators[index].classList.replace('bg-white/40', 'bg-white');

      currentIndex = index;
    }

    function nextSlide() {
      const newIndex = (currentIndex + 1) % slides.length;
      showSlide(newIndex);
    }

    function prevSlide() {
      const newIndex = (currentIndex - 1 + slides.length) % slides.length;
      showSlide(newIndex);
    }

    function startInterval() {
      clearInterval(slideInterval);
      slideInterval = setInterval(nextSlide, autoPlayDelay);
    }

    function resetInterval() {
      startInterval();
    }

    nextBtn.addEventListener('click', () => { nextSlide(); resetInterval(); });
    prevBtn.addEventListener('click', () => { prevSlide(); resetInterval(); });
    container.addEventListener('mouseenter', () => clearInterval(slideInterval));
    container.addEventListener('mouseleave', startInterval);
    document.addEventListener('visibilitychange', () => {
      if (document.hidden) {
        clearInterval(slideInterval);
      } else {
        startInterval();
      }
    });

    animateText(slides[0], true);
    startInterval();
  }

  const setupDropdown = (buttonId, dropdownId) => {
    const button = document.getElementById(buttonId);
    const dropdown = document.getElementById(dropdownId);

    if (button && dropdown) {
      button.addEventListener('click', (event) => {
        event.stopPropagation();
        document.querySelectorAll('.absolute.z-20').forEach(menu => {
            if (menu.id !== dropdownId) {
               menu.classList.add('hidden');
            }
        });
        dropdown.classList.toggle('hidden');
      });
    }
  };

  setupDropdown('shop-btn', 'shop-dropdown');
  setupDropdown('availability-btn', 'availability-dropdown');
  setupDropdown('price-btn', 'price-dropdown');
  setupDropdown('sort-btn', 'sort-dropdown');
  setupDropdown('user-btn', 'user-dropdown');

  window.addEventListener('click', () => {
    document.querySelectorAll('.absolute.z-20').forEach(menu => {
      if (!menu.classList.contains('hidden')) {
        menu.classList.add('hidden');
      }
    });
  });
});