(() => {
  document.querySelectorAll('[data-navigation-toggle]').forEach(button => {
    const menu = document.getElementById(button.getAttribute('aria-controls'));
    if (!menu) return;
    const header = button.closest('header');
    header.classList.add('navigation-ready');
    const close = () => {
      header.classList.remove('navigation-open');
      button.setAttribute('aria-expanded', 'false');
      button.setAttribute('aria-label', '開啟導覽選單');
    };
    button.addEventListener('click', () => {
      const open = button.getAttribute('aria-expanded') !== 'true';
      header.classList.toggle('navigation-open', open);
      button.setAttribute('aria-expanded', String(open));
      button.setAttribute('aria-label', open ? '關閉導覽選單' : '開啟導覽選單');
    });
    menu.addEventListener('click', event => { if (event.target.closest('a')) close(); });
    document.addEventListener('keydown', event => {
      if (event.key === 'Escape' && header.classList.contains('navigation-open')) {
        close(); button.focus();
      }
    });
    document.addEventListener('click', event => { if (!header.contains(event.target)) close(); });
    window.matchMedia('(max-width: 1100px)').addEventListener('change', close);
  });
})();
